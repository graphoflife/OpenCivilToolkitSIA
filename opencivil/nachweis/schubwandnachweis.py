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
Jede Schubwand fuer sich, mit ihrer ganzen Kraft, nicht je Meter (Benutzer,
2026-11-18): die gezeichneten Waende an ihren Knoten geteilt
(:func:`~opencivil.querschnitt.schubwaende.einzeln`), je Wand
``V_Ed = |q| · l`` gegen das Fachwerk mit ihrer Laenge als Hebelarm
(:func:`~opencivil.querschnitt.schubwaende.wandkraefte`,
:func:`~opencivil.querschnitt.schubwaende.widerstand`). Massgebend ist die
schwaechste Wand; nur sie steht in der Zusammenfassung.

GENEIGTE SPANNGLIEDER:
Ein geneigtes Glied mit Vordehnung traegt mit seiner lotrechten Kraft
``F · sin beta_p`` einen Teil von ``V_z``
(:mod:`opencivil.querschnitt.spannglieder`). Die Waende tragen den Rest:
``V_z - Σ F_i sin beta_p,i``, und in der Torsion fehlt ihnen das Moment
dieser Kraefte um den Schwerpunkt. Jede Wand vergleicht diesen Rest mit
ihrem Widerstand. Gleichung (50) schreibt den mitgetragenen Teil dem
Widerstand zu; an der Grenze ist das dasselbe, und nur so verteilt er sich
auf mehrere Waende -- nach Vorgabe, nicht nachgeschlagen. ``F`` ist
``P_inf``, wo die lotrechte Kraft wie ``V_z`` wirkt (4.3.3.4.8); wirkt sie
entgegen, die groesste Kraft im Glied (4.3.3.4.9): mit Verbund ``A_p``
mal die Fliessgrenze seines Wertesatzes -- so weit kann es im Bruch
tragen --, ohne Verbund ``A_p · sigma_p0``, die Kraft nach dem Spannen.
Welche Kraft die groesste ist, sagt die Norm nicht: nach Vorgabe, nicht
nachgeschlagen.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple

from opencivil.core.berechnung import Ausfuehrung, Eingaben
from opencivil.core.nachweis import NICHT_FUEHRBAR, Nachweis, NachweisUrteil, Vergleich, grad_def
from opencivil.core.einheiten import GRAD, KN, KNM, MM, Groesse
from opencivil.core.latex import Mathe, als_text, fest
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert, WertDef, grad_als_text
from opencivil.querschnitt import schubwaende as sw
from opencivil.querschnitt.analyse import Lastfall, Querschnittsanalyse
from opencivil.querschnitt.biegung import Biegung
from opencivil.querschnitt.fachwerk import ALPHA_ZUG, Buegelpunkt
from opencivil.querschnitt.spannglieder import (
    NACH_VORGABE, REFERENZ_GUENSTIG, REFERENZ_UNGUENSTIG, Spannglied, Verbund, geneigt,
    guenstig, lotrecht,
)

#: Die Seiten im Notizbuch, je Groesse eine.
GROESSTE_KRAFT = "Grösste Kraft eines geneigten Spannglieds"
LOTRECHT = "Lotrechte Kraft der geneigten Spannglieder"
QUERKRAFT_DER_WAENDE = "Querkraft der Wände neben geneigten Spanngliedern"
MOMENT_DER_GLIEDER = "Torsion aus der lotrechten Kraft der Spannglieder"
TORSION_DER_WAENDE = "Torsion der Wände neben geneigten Spanngliedern"

#: Wo die lotrechte Kraft der Glieder steht: mittragend und entgegen.
REFERENZ_GLIEDER = f"{REFERENZ_GUENSTIG}; {REFERENZ_UNGUENSTIG}"


def schub_belastet(biegung: Biegung, fall: Lastfall) -> bool:
    """
    Ob ein Lastfall die Schubwaende belastet -- einachsig zaehlt ``V_y``
    nicht. Fuer den Nachweis und fuer den Aufbau, der fragt, ob es ihn
    braucht.
    """
    return bool(fall.V_z or fall.T or biegung.querkraft_y(fall.V_y))


#: Warum ein Lastfall ohne Querkraft und Torsion keinen Schubfluss hat -- das
#: Diagramm zeigt den Satz an Stelle des Bildes.
OHNE_SCHUB = "Keine Querkraft und keine Torsion → kein Schubfluss."


@dataclass
class Schubbefund:
    """
    Was der Nachweis im Lauf fand: die Waende einzeln und ihre Zellen, je
    Lastfall die Verteilung des Schubflusses und je Wand den Widerstand bei
    der gewaehlten Neigung und ihren Vergleich -- fuer die Diagramme. Ein
    Lastfall ohne Verteilung (keine Last, keine Wand) fehlt in diesen dreien;
    war er belastet, sagt ``ohne`` warum.
    """

    modell: sw.Zellenmodell
    verteilungen: Dict[str, sw.Verteilung] = field(default_factory=dict)
    widerstaende: Dict[str, List[Buegelpunkt]] = field(default_factory=dict)
    vergleiche: Dict[str, List[Vergleich]] = field(default_factory=dict)
    """Je Wand ihre Kraft gegen ihren Widerstand, beide fuer die ganze Wand."""
    ohne: Dict[str, str] = field(default_factory=dict)
    """
    Je belasteter Lastfall ohne Verteilung der Grund -- es gibt keine Wand,
    oder die Waende tragen nicht. Derselbe Satz wie im Urteil.
    """
    glieder: Dict[str, float] = field(default_factory=dict)
    """Je Lastfall, was die geneigten Spannglieder von ``V_z`` tragen, in N -- ohne sie leer."""

    @property
    def waende(self) -> Tuple[sw.Wand, ...]:
        return self.modell.waende


@dataclass(frozen=True)
class GeneigtesGlied:
    """Ein geneigtes Glied, wie der Nachweis es liest: seine zwei Kraefte, seine Neigung, sein Hebel."""

    glied: Spannglied
    P_inf: Wert
    P_max: Wert
    beta: Wert
    hebel: Wert
    """``y - y_S``: wie weit es neben dem Schwerpunkt liegt."""

    def kraft(self, V_z: float) -> Wert:
        """``P_inf``, wo es ``V_z`` mittraegt -- sonst ``P_max``."""
        return self.P_inf if guenstig(self.glied.neigung, V_z) else self.P_max

    def lotrecht(self, V_z: float) -> float:
        """Seine lotrechte Kraft im Lastfall mit ``V_z``, in N."""
        return lotrecht(self.kraft(V_z).groesse.si, self.glied.neigung)


class Schubwandnachweis(Nachweis):
    """Querkraft und Torsion, je Lastfall auf die Schubwaende verteilt."""

    THEMA = "Querkraft und Torsion"
    ART = "V+T"

    def __init__(self, analyse: Querschnittsanalyse, lastfaelle: Sequence[Lastfall],
                 *, mit_laengszug: bool) -> None:
        self.analyse = analyse
        self.lastfaelle = list(lastfaelle)
        self.mit_laengszug = mit_laengszug
        self.geneigte = [g for g in analyse.spannglieder if geneigt(g)]

        basis = f"{analyse.id}.nachweis.vt"
        self.d_ausnutzung: Dict[str, WertDef] = {
            f.name: grad_def(f"{basis}.{f.kennung}.erfuellungsgrad",
                             rf"\alpha_{{eff,V,{als_text(f.name)}}}",
                             f"Erfüllungsgrad Querkraft und Torsion – {f.name}",
                             sw.REFERENZ_TORSION)
            for f in self.lastfaelle if schub_belastet(analyse.biegung, f)
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
        bezuege = list(analyse.grundbezuege()) + analyse.schubbezuege()
        if self.geneigte:
            bezuege += analyse.glieder.gliedbezuege(("A_p", "sigma_p0"), self.geneigte)
        ausgaben = (list(self.d_ausnutzung.values())
                    + [d for je in self.d_laengszug.values() for d in je.values()])
        super().__init__(
            basis, ausgaben=ausgaben, bezuege=bezuege,
            titel=f"Querkraft und Torsion – {analyse.name}",
            referenz=sw.REFERENZ_TORSION, abschnitt=analyse.abschnitt)

    # -- Pruefen ----------------------------------------------------------------

    def pruefe(self, e: Eingaben, p: Protokoll):
        bezug = (e.g("y_S").si, e.g("z_S").si)
        befund = Schubbefund(sw.zellen(self.analyse.schubwaende_mit(e)))
        alpha_min, alpha_max = self.analyse.neigungsgrenzen(e)
        self._protokoll_ansatz(p, e, befund)
        geneigte = self._protokoll_glieder(p, e, bezug)

        ergebnis: Dict[str, Groesse] = {}
        urteile: List[NachweisUrteil] = []
        for fall in self.lastfaelle:
            V_y = self.analyse.biegung.querkraft_y(fall.V_y)
            if not schub_belastet(self.analyse.biegung, fall):
                self._laengszug_null(ergebnis, fall)
                continue
            p.titel(fall.name, ebene=3)
            urteil, laengs = self._ein_fall(p, befund, fall, V_y, bezug, alpha_min, alpha_max,
                                            geneigte)
            urteile.append(urteil)
            if self.mit_laengszug:
                d = self.d_laengszug[fall.name]
                laengs = laengs or sw.Laengszug(0.0, 0.0, 0.0)
                ergebnis[d["N"].id] = Groesse.aus_si(laengs.N, KN)
                ergebnis[d["M_y"].id] = Groesse.aus_si(laengs.M_y, KNM)
                ergebnis[d["M_z"].id] = Groesse.aus_si(laengs.M_z, KNM)
        return Ausfuehrung(ergebnis, urteile, befund)

    def _laengszug_null(self, ergebnis: Dict[str, Groesse], fall: Lastfall) -> None:
        if self.mit_laengszug:
            for teil, d in self.d_laengszug[fall.name].items():
                ergebnis[d.id] = Groesse(0.0, KN if teil == "N" else KNM)

    def _ohne(self, p: Protokoll, befund: Schubbefund, fall: Lastfall, grund: str):
        p.warnung(grund)
        befund.ohne[fall.name] = grund
        return self.urteil(self.d_ausnutzung[fall.name], fall.name, NICHT_FUEHRBAR, grund), None

    def _ein_fall(self, p: Protokoll, befund: Schubbefund, fall: Lastfall, V_y: float,
                  bezug, alpha_min: int, alpha_max: int, geneigte: Sequence[GeneigtesGlied]):
        werte = Zwischenwerte(f"{self.id}.{fall.kennung}")
        p.tabelle(kopf=["Einwirkung", "Wert", ""], zeilen=[
            ["V_y,Ed", Mathe(fest(V_y / 1e3, 1)), "kN"],
            ["V_z,Ed", Mathe(fest(fall.V_z / 1e3, 1)), "kN"],
            ["T_Ed", Mathe(fest(fall.T / 1e3, 1)), "kNm"],
        ], titel="Einwirkung", ausrichtung="lrl")
        V_z, T = self._ohne_glieder(p, werte, befund, fall, geneigte)
        if not befund.waende:
            return self._ohne(p, befund, fall, "Es gibt keine Schubwand, die Querkraft oder "
                                       "Torsion aufnehmen könnte.")
        try:
            v = sw.verteilen(befund.modell, V_y=V_y, V_z=V_z.groesse.si, T=T.groesse.si,
                             bezug=bezug)
        except sw.WandFehler as fehler:
            return self._ohne(p, befund, fall, str(fehler))
        befund.verteilungen[fall.name] = v

        # -- Verteilung ---------------------------------------------------------
        if v.mit_drehung:
            p.text("Keine geschlossene Zelle: Querkraft und Torsion tragen die "
                   "Federn gemeinsam, mit Verschiebung und Drehung.")
        else:
            p.formel(werte.moment("dT", r"\Delta T", v.versatz),
                     r"\sum_i V_i \cdot r_i", {},
                     titel="Versatz: Moment der Querkraftanteile um den Schwerpunkt")
            p.formel(werte.moment("T_Zellen", r"T_{Zellen}", T.groesse.si - v.versatz),
                     r"@T - @dT", {"T": T, "dT": werte.moment("dT", r"\Delta T", v.versatz)},
                     titel="Was die Zellen tragen")
            p.tabelle(kopf=["Zelle", Mathe(r"A_k\ [\mathrm{mm}^2]"),
                            Mathe(r"q_k\ [\mathrm{kN/m}]")],
                      zeilen=[[f"Zelle {k + 1}", Mathe(fest(z.flaeche * 1e6, 0)),
                               Mathe(fest(q / 1e3, 1))]
                              for k, (z, q) in enumerate(zip(befund.modell.zellen,
                                                             v.zellenfluss))],
                      titel="Umlauf-Schubfluss der Zellen (Bredt)", ausrichtung="lrr")

        # -- Je Wand: ihre ganze Kraft gegen ihren Widerstand ---------------------
        zugkraft = fall.N > 0.0
        zeilen = []
        neigungen: List[int] = []
        widerstaende: List[Buegelpunkt] = []
        vergleiche: List[Vergleich] = []
        befund.widerstaende[fall.name] = widerstaende
        befund.vergleiche[fall.name] = vergleiche
        kraefte = sw.wandkraefte(befund.modell, v)
        for i, (w, V_Ed) in enumerate(zip(befund.waende, kraefte)):
            r = sw.widerstand(w, alpha_min=alpha_min, alpha_max=alpha_max, zugkraft=zugkraft)
            widerstaende.append(r)
            neigungen.append(r.alpha)
            wand = Vergleich(werte.kraft(f"V_Ed_{i + 1}", r"V_{Ed}", V_Ed),
                             werte.kraft(f"V_Rd_{i + 1}", r"V_{Rd}", r.V_Rd))
            vergleiche.append(wand)
            zeilen.append([w.name, Mathe(fest(v.aus_querkraft[i] / 1e3, 1)),
                           Mathe(fest(V_Ed / 1e3, 1)), Mathe(f"{r.alpha}"),
                           Mathe(fest(r.V_Rd_s / 1e3, 1)), Mathe(fest(r.V_Rd_c / 1e3, 1)),
                           Mathe(fest(r.V_Rd / 1e3, 1)),
                           Mathe(grad_als_text(wand.grad, wand.erfuellt, latex=True))])
        p.tabelle(
            kopf=["Wand", Mathe(r"V_i\ [\mathrm{kN}]"), Mathe(r"V_{Ed}\ [\mathrm{kN}]"),
                  Mathe(r"\alpha\ [{}^{\circ}]"), Mathe(r"V_{Rd,s}\ [\mathrm{kN}]"),
                  Mathe(r"V_{Rd,c}\ [\mathrm{kN}]"), Mathe(r"V_{Rd}\ [\mathrm{kN}]"),
                  Mathe(r"\alpha_{eff}")],
            zeilen=zeilen, ausrichtung="lrrrrrrr",
            titel="Je Wand: Kraft der Feder, ganze Kraft, Widerstand")
        if zugkraft:
            p.text(f"Normalzug: die Druckdiagonalen steilen sich auf, α mindestens "
                   f"{ALPHA_ZUG}° (SIA 262:2025, 4.3.3.3.3).")

        i = sw.schwaechste([vergleich.grad for vergleich in vergleiche])
        w, r, massgebend = befund.waende[i], widerstaende[i], vergleiche[i]
        p.text(f"Massgebend: {w.name}.")
        massgebend.zeile(p, self.d_ausnutzung[fall.name])

        laengs = None
        if self.mit_laengszug:
            laengs = sw.laengszug(befund.modell, v, neigungen, bezug)
            p.tabelle(kopf=["Längszugkraft", "Wert", ""], zeilen=[
                [Mathe(r"\Delta N = \sum |q|\, l \cot\alpha"), Mathe(fest(laengs.N / 1e3, 1)), "kN"],
                [Mathe(r"\Delta M_y = -\sum \Delta N_i (z_i - z_S)"),
                 Mathe(fest(laengs.M_y / 1e3, 1)), "kNm"],
                [Mathe(r"\Delta M_z = -\sum \Delta N_i (y_i - y_S)"),
                 Mathe(fest(laengs.M_z / 1e3, 1)), "kNm"],
            ], titel="Längszugkraft aus dem Druckfeld der Wände, je Wand in ihrer Mitte",
                ausrichtung="lrl")
            p.text(f"Je Wand ΔN_i = |q|·l·cot α, halb in jedem Gurt ({sw.REFERENZ_LAENGSZUG}).")

        glieder = (f" Geneigte Spannglieder: V_p = {befund.glieder[fall.name] / 1e3:.1f} kN."
                   if fall.name in befund.glieder else "")
        return self.urteil(self.d_ausnutzung[fall.name], fall.name, massgebend,
                           f"Massgebend {w.name}, α = {r.alpha}°.{glieder}"), laengs

    # -- Geneigte Spannglieder ----------------------------------------------------

    def _protokoll_glieder(self, p: Protokoll, e: Eingaben, bezug) -> List[GeneigtesGlied]:
        """Die Regel, und je geneigtes Glied seine grösste Kraft -- ohne Glied nichts."""
        if not self.geneigte:
            return []
        p.titel("Geneigte Spannglieder", ebene=3)
        p.erklaerung(
            "Ein geneigtes Spannglied trägt mit seiner lotrechten Kraft F·sin β_p einen Teil "
            "der Querkraft V_z; ist β_p positiv, wirkt sie wie ein positives V_z. Wirkt sie "
            "in einem Lastfall wie dessen V_z, trägt sie es mit, mit der Kraft nach allen "
            "Verlusten P∞; wirkt sie entgegen, kommt sie dazu, mit der grössten Kraft im "
            "Glied P_max. Die Wände tragen den Rest, und in der Torsion fehlt ihnen das "
            "Moment der lotrechten Kräfte um den Schwerpunkt. Gleichung (50) schreibt den "
            "mitgetragenen Teil dem Widerstand zu; hier mindert er die Kraft der Wände – an "
            "der Grenze dasselbe, und nur so verteilt er sich auf mehrere Wände.")
        p.ansatz(r"V_p = \sum_i F_i \cdot \sin\beta_{p,i} \qquad "
                 r"F_i = P_{\infty,i}\ \text{wo sie}\ V_{z,Ed}\ \text{mitträgt} \qquad "
                 r"F_i = P_{max,i}\ \text{wo sie entgegen wirkt}",
                 titel="Lotrechte Kraft der Glieder, und welche Kraft im Glied zählt",
                 referenz=REFERENZ_GLIEDER, name=LOTRECHT)
        p.ansatz(r"P_{max} = A_p \cdot f_{pd}\ \text{mit Verbund} \qquad "
                 r"P_{max} = A_p \cdot \sigma_{p0}\ \text{ohne Verbund}",
                 titel="Die grösste Kraft im Glied: mit Verbund bis zur Fliessgrenze, ohne "
                       "Verbund die nach dem Spannen",
                 referenz=f"{REFERENZ_UNGUENSTIG}; {NACH_VORGABE}", name=GROESSTE_KRAFT)
        p.ansatz(r"V_{z,w} = V_{z,Ed} - V_p \qquad "
                 r"T_w = T_{Ed} - \sum_i F_i \cdot \sin\beta_{p,i} \cdot (y_i - y_S)",
                 titel="Was die Wände tragen: die Last ohne die lotrechte Kraft der Glieder",
                 referenz=f"{REFERENZ_GLIEDER}; {NACH_VORGABE}", name=QUERKRAFT_DER_WAENDE)
        glieder, werte = self.analyse.glieder, Zwischenwerte(f"{self.id}.glieder")
        heraus = []
        for g in self.geneigte:
            k, index = g.kennung, glieder.index(g)
            A_p = e[f"A_p__{k}"]
            if g.verbund is Verbund.MIT:
                spannung = e[g.stahl.eingabename(self.analyse.wahl.satz(g.stahl).spannstahl)]
                wie = "mit Verbund bis zur Fliessgrenze"
            else:
                spannung = e[f"sigma_p0__{k}"]
                wie = "ohne Verbund die Kraft nach dem Spannen"
            P_max = werte.kraft(f"P_max_{k}", rf"P_{{max{index}}}",
                                A_p.groesse.si * spannung.groesse.si,
                                f"Grösste Kraft im Glied, {g.name}")
            p.formel(P_max, r"@A_p \cdot @f", {"A_p": A_p, "f": spannung},
                     titel=f"{g.name}: {wie}",
                     referenz=f"{REFERENZ_UNGUENSTIG}; {NACH_VORGABE}", name=GROESSTE_KRAFT)
            heraus.append(GeneigtesGlied(
                glied=g, P_inf=e[f"P_inf__{k}"], P_max=P_max,
                beta=werte.wert(f"beta_{k}", rf"\beta_{{p{index}}}", Groesse(g.neigung, GRAD),
                                1, f"Neigung, {g.name}"),
                hebel=werte.laenge(f"e_{k}", rf"e_{{p{index}}}", g.von[0] * MM.faktor - bezug[0],
                                   f"Lage neben dem Schwerpunkt, y - y_S, {g.name}")))
        p.tabelle(
            kopf=["Glied", Mathe(r"\beta_p\ [{}^{\circ}]"), Mathe(r"y - y_S\ [\mathrm{mm}]"),
                  Mathe(r"P_\infty\ [\mathrm{kN}]"), Mathe(r"P_{max}\ [\mathrm{kN}]"),
                  "Verbund"],
            zeilen=[[x.glied.name, Mathe(fest(x.glied.neigung, 1)),
                     Mathe(fest(x.hebel.groesse.si * 1e3, 0)),
                     Mathe(fest(x.P_inf.groesse.si / 1e3, 1)),
                     Mathe(fest(x.P_max.groesse.si / 1e3, 1)), x.glied.verbund.beschriftung]
                    for x in heraus],
            titel="Geneigte Spannglieder", ausrichtung="lrrrrl")
        return heraus

    def _ohne_glieder(self, p: Protokoll, werte: Zwischenwerte, befund: Schubbefund,
                      fall: Lastfall, geneigte: Sequence[GeneigtesGlied]) -> Tuple[Wert, Wert]:
        """
        ``V_z`` und ``T``, die die Waende tragen: ohne die lotrechte Kraft der
        geneigten Glieder und ihr Moment um den Schwerpunkt.
        """
        V_z = werte.kraft("V_z", r"V_{z,Ed}", fall.V_z)
        T = werte.moment("T", r"T_{Ed}", fall.T)
        if not geneigte:
            return V_z, T
        p.text("; ".join(
            f"{x.glied.name}: " + ("trägt V_z mit → P∞" if guenstig(x.glied.neigung, fall.V_z)
                                   else "wirkt V_z entgegen → P_max")
            for x in geneigte) + ".")

        def summe(glieder: Sequence[GeneigtesGlied], je_glied) -> Tuple[str, Dict[str, Wert]]:
            """Die Vorlage einer Summe über ``glieder`` und ihre Belegung."""
            vorlage, belegung = [], {}
            for i, x in enumerate(glieder):
                teil, mit = je_glied(i, x)
                vorlage.append(teil)
                belegung.update(mit)
            return " + ".join(vorlage), belegung

        V_p = werte.kraft("V_p", "V_p", sum(x.lotrecht(fall.V_z) for x in geneigte),
                          "Lotrechte Kraft der geneigten Spannglieder")
        befund.glieder[fall.name] = V_p.groesse.si
        p.formel(V_p, *summe(geneigte, lambda i, x: (rf"@F{i} \cdot \sin @b{i}",
                                           {f"F{i}": x.kraft(fall.V_z), f"b{i}": x.beta})),
                 titel="Lotrechte Kraft der geneigten Spannglieder", referenz=REFERENZ_GLIEDER,
                 name=LOTRECHT)
        V_z_w = werte.kraft("V_z_w", r"V_{z,w}", fall.V_z - V_p.groesse.si,
                            "Querkraft der Wände")
        p.formel(V_z_w, r"@V_z - @V_p", {"V_z": V_z, "V_p": V_p},
                 titel="Was die Wände von V_z tragen", name=QUERKRAFT_DER_WAENDE)
        neben = [x for x in geneigte if abs(x.hebel.groesse.si) > sw.KNOTEN_TOLERANZ]
        if not neben:
            return V_z_w, T
        T_p = werte.moment("T_p", "T_p", sum(x.lotrecht(fall.V_z) * x.hebel.groesse.si
                                             for x in neben),
                           "Moment der lotrechten Kraft der Glieder um den Schwerpunkt")
        p.formel(T_p, *summe(neben, lambda i, x: (
            rf"@F{i} \cdot \sin @b{i} \cdot @e{i}",
            {f"F{i}": x.kraft(fall.V_z), f"b{i}": x.beta, f"e{i}": x.hebel})),
                 titel="Ihr Moment um den Schwerpunkt", name=MOMENT_DER_GLIEDER)
        T_w = werte.moment("T_w", "T_w", fall.T - T_p.groesse.si, "Torsion der Wände")
        p.formel(T_w, r"@T - @T_p", {"T": T, "T_p": T_p},
                 titel="Was die Wände von T tragen", name=TORSION_DER_WAENDE)
        return V_z_w, T_w

    # -- Mitschrift ----------------------------------------------------------------

    def _protokoll_ansatz(self, p: Protokoll, e: Eingaben, befund: Schubbefund) -> None:
        p.erklaerung(
            "Jede Schubwand trägt eine Kraft entlang ihrer Achse; ihre Länge ist "
            "der Hebelarm des Fachwerks. Verteilt wird elastisch: der Querschnitt "
            "verschiebt sich, und jede Wand wehrt sich wie eine Feder mit der "
            "Steifigkeit b_w·l. Das Moment dieser Querkraftanteile um den "
            "Schwerpunkt ist der Versatz ΔT; den Rest der Torsion tragen die "
            "geschlossenen Zellen als Umlauf-Schubfluss nach Bredt, mehrzellig "
            "mit gleicher Verdrillung aller Zellen. Ohne Zelle trägt die Torsion "
            "über dieselben Federn mit Drehung. Die Wandkräfte ergeben so immer "
            "V_y, V_z und um den Schwerpunkt T. Eine gezeichnete Wand ist dort "
            "geteilt, wo eine andere auf ihr endet oder sie kreuzt (Wand 1.1, "
            "Wand 1.2 …): jede trägt so überall denselben Fluss und wird für sich "
            "nachgewiesen, mit ihrer ganzen Kraft, nicht je Meter – bei einer "
            "Zelle die Kraft aus der Querkraft und die aus der Torsion zusammen. "
            "In der Zusammenfassung steht die massgebende Wand.")
        p.ansatz(r"k_i = b_{w,i} \cdot l_i \qquad \sum_i k_i\, e_i e_i^T\, u = V "
                 r"\qquad V_i = k_i\, e_i \cdot u \qquad \Delta T = \sum_i V_i\, r_i",
                 titel="Querkraft über die Federn der Wände")
        p.ansatz(r"T - \Delta T = \sum_k 2 A_k\, q_k \qquad "
                 r"\oint_k \frac{q}{b_w}\, \mathrm{d}s = 2 A_k\, \theta",
                 titel="Torsion in den Zellen (Bredt, mehrzellig)", referenz=sw.REFERENZ_ZELLE)
        p.ansatz(r"V_{Ed} = |q| \cdot l",
                 titel="Kraft einer Wand: ihr Schubfluss über ihre Länge",
                 referenz=sw.REFERENZ_KRAFT)
        p.ansatz(r"V_{Rd,s} = \frac{A_{sw}}{s}\, l\, f_{yd} \cot\alpha \qquad "
                 r"V_{Rd,c} = b_w\, l\, k_c\, f_{cd} \sin\alpha \cos\alpha \qquad "
                 r"V_{Rd} = \max_\alpha \min(V_{Rd,s};\ V_{Rd,c})",
                 titel="Widerstand einer Wand (Fachwerk, ihre Länge l als Hebelarm)",
                 referenz=sw.REFERENZ_WAND)
        p.tabelle(kopf=["Grenze", "Wert"], zeilen=[
            [Mathe(r"\alpha_{min}"), Mathe(e["alpha_min"].zahl_latex())],
            [Mathe(r"\alpha_{max}"), Mathe(e["alpha_max"].zahl_latex())],
            [Mathe("k_c"), Mathe(e["k_c"].zahl_latex())],
        ], titel="Druckfeld", ausrichtung="lr")
        if befund.waende:
            zellen_von: Dict[int, List[int]] = {}
            for k, z in enumerate(befund.modell.zellen):
                for wand, _ in z.rand:
                    zellen_von.setdefault(wand, []).append(k + 1)
            p.tabelle(
                kopf=["Wand", Mathe(r"l\ [\mathrm{mm}]"), Mathe(r"b_w\ [\mathrm{mm}]"),
                      Mathe(r"k = b_w l\ [\mathrm{mm}^2]"),
                      Mathe(r"A_{sw}/s\ [\mathrm{mm^2/m}]"), "Zelle"],
                zeilen=[[w.name, Mathe(fest(w.laenge * 1e3, 0)), Mathe(fest(w.b_w * 1e3, 0)),
                         Mathe(fest(w.steifigkeit * 1e6, 0)), Mathe(fest(w.a_sw_s * 1e6, 0)),
                         ", ".join(str(k) for k in sorted(set(zellen_von.get(i, [])))) or "–"]
                        for i, w in enumerate(befund.waende)],
                titel="Schubwände und ihre Steifigkeit", ausrichtung="lrrrrl")
