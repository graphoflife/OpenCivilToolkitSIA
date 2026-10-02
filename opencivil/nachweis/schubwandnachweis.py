"""
opencivil/nachweis/schubwandnachweis.py -- Querkraft und Torsion am gezeichneten Querschnitt.

VERANTWORTUNG:
Je Lastfall ``(V_y, V_z, T)`` auf die Schubwaende verteilt und jede Wand mit
dem Fachwerk nachgewiesen. Die Verteilung -- Federn nach ``b_w · l``, Versatz,
Zellen nach Bredt -- steht in :mod:`opencivil.querschnitt.schubwaende`; hier
wird sie aufgeschrieben und geurteilt.

Liefert zudem je Lastfall die Laengszugkraft ``ΔN, ΔM_y, ΔM_z``, wenn sie
zugeschaltet ist: der Nachweis von Biegung und Normalkraft liest sie.

DER MASSSTAB:
Je Wand ``v_Rd / |q_Ed|``, gemessen am staerksten Stueck der Wand; massgebend
ist die schwaechste Wand.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence

from opencivil.core.berechnung import (
    Eingabebezug, Eingaben, Nachweis, NachweisUrteil, grad_def, grad_formel,
)
from opencivil.core.einheiten import EINHEITSLOS, KN, KN_PRO_M, KNM, Groesse
from opencivil.core.latex import Mathe, als_text, fest
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import WertDef
from opencivil.material.basis import Baustoff
from opencivil.querschnitt import schubwaende as sw
from opencivil.querschnitt.analyse import Lastfall, Querschnittsanalyse, Wandangabe


class Schubwandnachweis(Nachweis):
    """Querkraft und Torsion, je Lastfall auf die Schubwaende verteilt."""

    THEMA = "Querkraft und Torsion"

    def __init__(self, analyse: Querschnittsanalyse, lastfaelle: Sequence[Lastfall],
                 *, einachsig: bool, mit_laengszug: bool) -> None:
        self.analyse = analyse
        self.lastfaelle = list(lastfaelle)
        self.einachsig = einachsig
        self.mit_laengszug = mit_laengszug
        self.verteilungen: Dict[str, Optional[sw.Verteilung]] = {}
        self.widerstaende: Dict[str, List[sw.Wandwiderstand]] = {}
        """Je Lastfall und Wand der Widerstand bei der gewählten Neigung -- für die Diagramme."""
        self.modell: Optional[sw.Zellenmodell] = None
        self.waende: List[sw.Wand] = []

        basis = f"{analyse.id}.nachweis.vt"
        self.d_ausnutzung: Dict[str, WertDef] = {
            f.name: grad_def(f"{basis}.{f.kennung}.erfuellungsgrad",
                             rf"\alpha_{{eff,V,{als_text(f.name)}}}",
                             f"Erfüllungsgrad Querkraft und Torsion – {f.name}",
                             "SIA 262:2025, 4.3.3")
            for f in self.lastfaelle if self._belastet(f)
        }
        self.d_laengszug: Dict[str, Dict[str, WertDef]] = {}
        if mit_laengszug:
            for f in self.lastfaelle:
                self.d_laengszug[f.name] = {
                    "N": WertDef(f"{basis}.{f.kennung}.dN", r"\Delta N", KN,
                                 f"Längszugkraft aus Querkraft und Torsion – {f.name}",
                                 stellen=1),
                    "M_y": WertDef(f"{basis}.{f.kennung}.dM_y", r"\Delta M_y", KNM,
                                   f"Moment der Längszugkraft um y – {f.name}", stellen=1),
                    "M_z": WertDef(f"{basis}.{f.kennung}.dM_z", r"\Delta M_z", KNM,
                                   f"Moment der Längszugkraft um z – {f.name}", stellen=1),
                }
        bezuege = list(analyse.grundbezuege()) + [
            Eingabebezug("alpha_min", analyse.id_von("alpha_min")),
            Eingabebezug("alpha_max", analyse.id_von("alpha_max")),
            Eingabebezug("k_c", analyse.id_von("k_c")),
        ]
        ausgaben = (list(self.d_ausnutzung.values())
                    + [d for je in self.d_laengszug.values() for d in je.values()])
        super().__init__(
            basis, ausgaben=ausgaben, bezuege=bezuege,
            titel=f"Querkraft und Torsion – {analyse.name}",
            referenz="SIA 262:2025, 4.3.3", abschnitt=analyse.abschnitt)

    def _belastet(self, fall: Lastfall) -> bool:
        return bool(fall.V_z or fall.T or (fall.V_y and not self.einachsig))

    # -- Festigkeiten der Waende -----------------------------------------------

    def _f_sd(self, e: Eingaben, w: Wandangabe) -> float:
        if w.stahl is None:
            return 0.0
        k = "f_yd" if self.analyse.satz(w.stahl) == "bemessung" else "f_yk"
        return abs(self.analyse.kennwert(e, w.stahl, k))

    def _f_cd(self, e: Eingaben, w: Wandangabe) -> float:
        k = "f_cd" if self.analyse.satz(w.beton) == "bemessung" else "f_ck"
        return abs(self.analyse.kennwert(e, w.beton, k))

    # -- Pruefen ----------------------------------------------------------------

    def pruefe(self, e: Eingaben, p: Protokoll):
        bezug = (e.g("y_S").si, e.g("z_S").si)
        self.waende = self.analyse.schubwaende(
            f_sd=lambda w: self._f_sd(e, w), f_cd=lambda w: self._f_cd(e, w),
            k_c=e.g("k_c").si)
        self.modell = sw.zellen(self.waende) if self.waende else sw.Zellenmodell((), ())
        alpha_min = int(round(e.g("alpha_min").si * 180.0 / math.pi))
        alpha_max = int(round(e.g("alpha_max").si * 180.0 / math.pi))
        self._protokoll_ansatz(p, e)

        ergebnis: Dict[str, Groesse] = {}
        urteile: List[NachweisUrteil] = []
        for fall in self.lastfaelle:
            V_y = 0.0 if self.einachsig else fall.V_y
            if not self._belastet(fall):
                self.verteilungen[fall.name] = None
                self._laengszug_null(ergebnis, fall)
                continue
            p.titel(fall.name, ebene=3)
            urteil, grad, laengs = self._ein_fall(
                p, fall, V_y, bezug, alpha_min, alpha_max)
            ergebnis[self.d_ausnutzung[fall.name].id] = Groesse(grad, EINHEITSLOS)
            urteile.append(urteil)
            if self.mit_laengszug:
                d = self.d_laengszug[fall.name]
                laengs = laengs or sw.Laengszug(0.0, 0.0, 0.0)
                ergebnis[d["N"].id] = Groesse.aus_si(laengs.N, KN)
                ergebnis[d["M_y"].id] = Groesse.aus_si(laengs.M_y, KNM)
                ergebnis[d["M_z"].id] = Groesse.aus_si(laengs.M_z, KNM)
        return ergebnis, urteile

    def _laengszug_null(self, ergebnis: Dict[str, Groesse], fall: Lastfall) -> None:
        if self.mit_laengszug:
            for teil, d in self.d_laengszug[fall.name].items():
                ergebnis[d.id] = Groesse(0.0, KN if teil == "N" else KNM)

    def _ohne(self, p: Protokoll, fall: Lastfall, grund: str):
        p.warnung(grund)
        d = self.d_ausnutzung[fall.name]
        self.verteilungen[fall.name] = None
        return NachweisUrteil(
            art="V+T", ziel=d.id, fall=fall.name, erfuellt=False,
            erfuellungsgrad=Groesse(0.0, EINHEITSLOS), begruendung=grund,
            hinweis=grund), 0.0, None

    def _ein_fall(self, p: Protokoll, fall: Lastfall, V_y: float, bezug,
                  alpha_min: int, alpha_max: int):
        werte = Zwischenwerte(f"{self.id}.{fall.kennung}")
        p.tabelle(kopf=["Einwirkung", "Wert", ""], zeilen=[
            ["V_y,Ed", Mathe(fest(V_y / 1e3, 1)), "kN"],
            ["V_z,Ed", Mathe(fest(fall.V_z / 1e3, 1)), "kN"],
            ["T_Ed", Mathe(fest(fall.T / 1e3, 1)), "kNm"],
        ], titel="Einwirkung", ausrichtung="lrl")
        if not self.waende:
            return self._ohne(p, fall, "Es gibt keine Schubwand, die Querkraft oder "
                                       "Torsion aufnehmen könnte.")
        try:
            v = sw.verteilen(self.waende, self.modell, V_y=V_y, V_z=fall.V_z, T=fall.T,
                             bezug=bezug)
        except sw.WandFehler as fehler:
            return self._ohne(p, fall, str(fehler))
        self.verteilungen[fall.name] = v

        # -- Verteilung ---------------------------------------------------------
        if v.mit_drehung:
            p.text("Keine geschlossene Zelle: Querkraft und Torsion tragen die "
                   "Federn gemeinsam, mit Verschiebung und Drehung.")
        else:
            p.formel(werte.moment("dT", r"\Delta T", v.versatz),
                     r"\sum_i V_i \cdot r_i", {},
                     titel="Versatz: Moment der Querkraftanteile um den Schwerpunkt")
            p.formel(werte.moment("T_Zellen", r"T_{Zellen}", fall.T - v.versatz),
                     r"@T - @dT", {"T": werte.moment("T", "T_{Ed}", fall.T),
                                   "dT": werte.moment("dT", r"\Delta T", v.versatz)},
                     titel="Was die Zellen tragen")
            p.tabelle(kopf=["Zelle", Mathe(r"A_k\ [\mathrm{mm}^2]"),
                            Mathe(r"q_k\ [\mathrm{kN/m}]")],
                      zeilen=[[f"Zelle {k + 1}", Mathe(fest(z.flaeche * 1e6, 0)),
                               Mathe(fest(q / 1e3, 1))]
                              for k, (z, q) in enumerate(zip(self.modell.zellen,
                                                             v.zellenfluss))],
                      titel="Umlauf-Schubfluss der Zellen (Bredt)", ausrichtung="lrr")

        # -- Je Wand: staerkstes Stueck gegen den Widerstand ---------------------
        zugkraft = fall.N > 0.0
        zeilen = []
        bester: Optional[tuple] = None
        neigungen: List[int] = []
        self.widerstaende[fall.name] = []
        for i, w in enumerate(self.waende):
            fluss = [abs(q) for s, q in zip(self.modell.stuecke, v.fluss) if s.wand == i]
            q_ed = max(fluss) if fluss else 0.0
            r = sw.widerstand(w, alpha_min=alpha_min, alpha_max=alpha_max, zugkraft=zugkraft)
            self.widerstaende[fall.name].append(r)
            neigungen.append(r.alpha)
            # Ein Fluss unter einem Millionstel N/m ist Rundungsrauschen der
            # Verteilung, keine Beanspruchung -- dort steht ∞, nicht 8·10¹⁶.
            grad_w = (r.v_Rd / q_ed) if q_ed > 1e-6 else math.inf
            zeilen.append([w.name, Mathe(fest(v.aus_querkraft[i] / 1e3, 1)),
                           Mathe(fest(q_ed / 1e3, 1)), Mathe(f"{r.alpha}"),
                           Mathe(fest(r.v_Rd_s / 1e3, 1)), Mathe(fest(r.v_Rd_c / 1e3, 1)),
                           Mathe(fest(r.v_Rd / 1e3, 1)),
                           Mathe("\\infty" if math.isinf(grad_w) else fest(grad_w, 2))])
            if bester is None or grad_w < bester[0]:
                bester = (grad_w, w, q_ed, r)
        p.tabelle(
            kopf=["Wand", Mathe(r"V_i\ [\mathrm{kN}]"), Mathe(r"|q_{Ed}|\ [\mathrm{kN/m}]"),
                  Mathe(r"\alpha\ [{}^{\circ}]"), Mathe(r"v_{Rd,s}\ [\mathrm{kN/m}]"),
                  Mathe(r"v_{Rd,c}\ [\mathrm{kN/m}]"), Mathe(r"v_{Rd}\ [\mathrm{kN/m}]"),
                  Mathe(r"\alpha_{eff}")],
            zeilen=zeilen, ausrichtung="lrrrrrrr",
            titel="Je Wand: Kraft aus der Querkraft, stärkster Schubfluss, Widerstand")
        if zugkraft:
            p.text("Normalzug: die Druckdiagonalen steilen sich auf, α mindestens 40°.")

        grad, w, q_ed, r = bester
        einwirkung = werte.wert("q_Ed", r"q_{Ed}", Groesse.aus_si(q_ed, KN_PRO_M), 1)
        widerstand = werte.wert("v_Rd", r"v_{Rd}", Groesse.aus_si(r.v_Rd, KN_PRO_M), 1)
        if math.isinf(grad):
            grad = 1e9
        erfuellt = grad >= 1.0
        p.text(f"Massgebend: {w.name}.")
        grad_formel(p, self.d_ausnutzung[fall.name], grad, widerstand, einwirkung,
                    erfuellt, mit_urteil=True)

        laengs = None
        if self.mit_laengszug:
            laengs = sw.laengszug(self.modell, v, neigungen, bezug)
            p.tabelle(kopf=["Längszugkraft", "Wert", ""], zeilen=[
                [Mathe(r"\Delta N = \sum |q|\, l \cot\alpha"), Mathe(fest(laengs.N / 1e3, 1)), "kN"],
                [Mathe(r"\Delta M_y = -\sum \Delta N_i (z_i - z_S)"),
                 Mathe(fest(laengs.M_y / 1e3, 1)), "kNm"],
                [Mathe(r"\Delta M_z = -\sum \Delta N_i (y_i - y_S)"),
                 Mathe(fest(laengs.M_z / 1e3, 1)), "kNm"],
            ], titel="Längszugkraft aus dem Druckfeld der Wände, je Stück in seiner Mitte",
                ausrichtung="lrl")

        return NachweisUrteil(
            art="V+T", ziel=self.d_ausnutzung[fall.name].id, fall=fall.name,
            erfuellt=erfuellt, erfuellungsgrad=Groesse(grad, EINHEITSLOS),
            begruendung=f"Massgebend {w.name}, α = {r.alpha}°.",
            einwirkung=einwirkung, widerstand=widerstand), grad, laengs

    # -- Mitschrift ----------------------------------------------------------------

    def _protokoll_ansatz(self, p: Protokoll, e: Eingaben) -> None:
        p.erklaerung(
            "Jede Schubwand trägt eine Kraft entlang ihrer Achse; ihre Länge ist "
            "der Hebelarm des Fachwerks. Verteilt wird elastisch: der Querschnitt "
            "verschiebt sich, und jede Wand wehrt sich wie eine Feder mit der "
            "Steifigkeit b_w·l. Das Moment dieser Querkraftanteile um den "
            "Schwerpunkt ist der Versatz ΔT; den Rest der Torsion tragen die "
            "geschlossenen Zellen als Umlauf-Schubfluss nach Bredt, mehrzellig "
            "mit gleicher Verdrillung aller Zellen. Ohne Zelle trägt die Torsion "
            "über dieselben Federn mit Drehung. Die Wandkräfte ergeben so immer "
            "V_y, V_z und um den Schwerpunkt T.")
        p.ansatz(r"k_i = b_{w,i} \cdot l_i \qquad \sum_i k_i\, e_i e_i^T\, u = V "
                 r"\qquad V_i = k_i\, e_i \cdot u \qquad \Delta T = \sum_i V_i\, r_i",
                 titel="Querkraft über die Federn der Wände")
        p.ansatz(r"T - \Delta T = \sum_k 2 A_k\, q_k \qquad "
                 r"\oint_k \frac{q}{b_w}\, \mathrm{d}s = 2 A_k\, \theta",
                 titel="Torsion in den Zellen (Bredt, mehrzellig)")
        p.ansatz(r"v_{Rd,s} = \frac{A_{sw}}{s}\, f_{sd} \cot\alpha \qquad "
                 r"v_{Rd,c} = b_w\, k_c\, f_{cd} \sin\alpha \cos\alpha \qquad "
                 r"v_{Rd} = \max_\alpha \min(v_{Rd,s};\ v_{Rd,c})",
                 titel="Widerstand je Länge einer Wand (Fachwerk)",
                 referenz="SIA 262:2025, 4.3.3.4")
        p.tabelle(kopf=["Grenze", "Wert"], zeilen=[
            [Mathe(r"\alpha_{min}"), Mathe(e["alpha_min"].zahl_latex())],
            [Mathe(r"\alpha_{max}"), Mathe(e["alpha_max"].zahl_latex())],
            [Mathe("k_c"), Mathe(e["k_c"].zahl_latex())],
        ], titel="Druckfeld", ausrichtung="lr")
        if self.waende:
            zellen_von: Dict[int, List[int]] = {}
            for k, z in enumerate(self.modell.zellen):
                for stueck, _ in z.rand:
                    zellen_von.setdefault(self.modell.stuecke[stueck].wand, []).append(k + 1)
            p.tabelle(
                kopf=["Wand", Mathe(r"l\ [\mathrm{mm}]"), Mathe(r"b_w\ [\mathrm{mm}]"),
                      Mathe(r"k = b_w l\ [\mathrm{mm}^2]"),
                      Mathe(r"A_{sw}/s\ [\mathrm{mm^2/m}]"), "Zelle"],
                zeilen=[[w.name, Mathe(fest(w.laenge * 1e3, 0)), Mathe(fest(w.b_w * 1e3, 0)),
                         Mathe(fest(w.steifigkeit * 1e6, 0)), Mathe(fest(w.a_sw_s * 1e6, 0)),
                         ", ".join(str(k) for k in sorted(set(zellen_von.get(i, [])))) or "–"]
                        for i, w in enumerate(self.waende)],
                titel="Schubwände und ihre Steifigkeit", ausrichtung="lrrrrl")
