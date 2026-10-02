"""
opencivil/nachweis/schiefe_biegung.py -- Biegung und Normalkraft am gezeichneten Querschnitt.

VERANTWORTUNG:
Prueft je Lastfall ``(N_Ed, M_y,Ed, M_z,Ed)`` gegen den Bruchzustand des
gezeichneten Querschnitts -- schief, oder auf Wunsch nur um y.

WOGEGEN NACHGEWIESEN WIRD:
Bei der Platte gegen eine Handrechnung, die sich mit wenigen Zeilen
nachvollziehen laesst. Fuer ein beliebiges Polygon gibt es keine solche:
nachgewiesen wird darum gegen den Dehnungsfaecher selbst
(:mod:`opencivil.querschnitt.interaktion`). Was in der Herleitung steht, ist
nicht die Suche, sondern ihre **Probe**: die gefundene Dehnungsebene, die
Kraefte jedes Teils mit ihrem Angriffspunkt, und die drei Summen ``N``,
``M_y`` und ``M_z``. Wer nachrechnen will, rechnet diese Summen -- das geht
von Hand. Dasselbe Vorgehen wie beim Querschnittsloeser der Platte.

DER MASSSTAB:
Normalkraft fest, Richtung des Moments fest: ``α_eff = M_Rd / M_Ed`` in der
Richtung von ``(M_y,Ed, M_z,Ed)``. Ohne Moment ``N_Rd / N_Ed``.

LAENGSZUGKRAFT:
Ist sie zugeschaltet, kommt das, was das Druckfeld der Schubwaende in
Laengsrichtung braucht, zu N und den Momenten dazu -- siehe
:mod:`opencivil.querschnitt.schubwaende`. Die Werte liefert der Nachweis der
Schubwaende; dieser hier liest sie ueber das Rechenwerk.

VORZEICHEN:
N > 0 Zug; M_y > 0 zieht unten, M_z > 0 links.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from opencivil.core.berechnung import (
    Eingabebezug, Eingaben, Nachweis, NachweisUrteil, grad_def, grad_formel,
)
from opencivil.core.einheiten import EINHEITSLOS, KN, KNM, Groesse
from opencivil.core.latex import Mathe, als_text, fest
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert, WertDef
from opencivil.querschnitt.analyse import Lastfall, Querschnittsanalyse
from opencivil.querschnitt.interaktion import Bruchpunkt, Kraftanteil, Querschnitt

#: Ab welchem Moment ein Lastfall als Biegung gilt, in Nm. Darunter ist es
#: reine Normalkraft -- eine Richtung des Moments gibt es dann nicht.
KEIN_MOMENT = 1e-6


@dataclass
class Fallergebnis:
    """Was ein Lastfall ergab -- fuer die Diagramme nach dem Lauf."""

    fall: Lastfall
    N: float
    M_y: float
    M_z: float
    """Die Einwirkung, wie nachgewiesen -- mit Laengszugkraft, wo zugeschaltet."""

    punkt: Optional[Bruchpunkt]
    erfuellungsgrad: float


class SchiefeBiegung(Nachweis):
    """Biegung und Normalkraft, je Lastfall gegen den Dehnungsfaecher."""

    #: In der Formelsammlung ein eigenes Thema: gerechnet wird anders als
    #: bei der Platte, gegen den Dehnungsfaecher statt gegen eine Handrechnung.
    #: In der Zusammenfassung heisst er wie dort.
    THEMA = "Schiefe Biegung"
    LANGNAME = "Biegung und Normalkraft"

    def __init__(self, analyse: Querschnittsanalyse, lastfaelle: Sequence[Lastfall],
                 *, einachsig: bool, laengszug=None) -> None:
        self.analyse = analyse
        self.lastfaelle = list(lastfaelle)
        self.einachsig = einachsig
        self.laengszug = laengszug
        """Der Nachweis der Schubwaende, wenn die Laengszugkraft zaehlt."""

        self.querschnitt: Optional[Querschnitt] = None
        self.ergebnisse: List[Fallergebnis] = []

        basis = f"{analyse.id}.nachweis.mn"
        self.d_ausnutzung: Dict[str, WertDef] = {
            f.name: grad_def(f"{basis}.{f.kennung}.erfuellungsgrad",
                             rf"\alpha_{{eff,{als_text(f.name)}}}",
                             f"Erfüllungsgrad Biegung und Normalkraft – {f.name}",
                             "SIA 262:2025, 4.1.4")
            for f in self.lastfaelle
        }
        self.d_eckwerte = {
            "N_Rd_zug": WertDef(f"{basis}.N_Rd_zug", "N_{Rd}^{+}", KN,
                                "Grösste aufnehmbare Zugkraft", stellen=1),
            "N_Rd_druck": WertDef(f"{basis}.N_Rd_druck", "N_{Rd}^{-}", KN,
                                  "Grösste aufnehmbare Druckkraft", stellen=1),
        }
        bezuege = list(analyse.grundbezuege())
        if laengszug is not None:
            for f in self.lastfaelle:
                for teil, d in laengszug.d_laengszug[f.name].items():
                    bezuege.append(Eingabebezug(f"d{teil}_{f.kennung}", d.id))
        super().__init__(
            basis,
            ausgaben=list(self.d_ausnutzung.values()) + list(self.d_eckwerte.values()),
            bezuege=bezuege,
            titel=f"Biegung und Normalkraft – {analyse.name}",
            referenz="SIA 262:2025, 4.1.4",
            abschnitt=analyse.abschnitt,
        )

    # -- Pruefen ----------------------------------------------------------------

    def pruefe(self, e: Eingaben, p: Protokoll):
        q, herkunft = self.analyse.interaktion(e)
        self.querschnitt = q
        self._protokoll_ansatz(p, e, q)

        zug, druck = q.normalkraft_grenzen()
        werte = Zwischenwerte(self.id)
        p.tabelle(kopf=["Grenze", "Wert"], zeilen=[
            ["reiner Zug, gleichmässig", Mathe(f"N_{{Rd}}^{{+}} = {zug / 1e3:.1f}\\,\\mathrm{{kN}}")],
            ["reiner Druck, gleichmässig", Mathe(f"N_{{Rd}}^{{-}} = {druck / 1e3:.1f}\\,\\mathrm{{kN}}")],
        ], titel="Reine Normalkraft", ausrichtung="lr")
        ergebnis = {
            self.d_eckwerte["N_Rd_zug"].id: Groesse.aus_si(zug, KN),
            self.d_eckwerte["N_Rd_druck"].id: Groesse.aus_si(druck, KN),
        }

        self.ergebnisse = []
        urteile: List[NachweisUrteil] = []
        for fall in self.lastfaelle:
            urteil, grad = self._ein_fall(p, e, q, herkunft, fall, zug, druck)
            ergebnis[self.d_ausnutzung[fall.name].id] = Groesse(grad, EINHEITSLOS)
            if urteil is not None:
                urteile.append(urteil)
        return ergebnis, urteile

    def _einwirkung(self, e: Eingaben, fall: Lastfall) -> Tuple[float, float, float]:
        N, M_y, M_z = fall.N, fall.M_y, 0.0 if self.einachsig else fall.M_z
        if self.laengszug is not None:
            N += e.g(f"dN_{fall.kennung}").si
            M_y += e.g(f"dM_y_{fall.kennung}").si
            if not self.einachsig:
                M_z += e.g(f"dM_z_{fall.kennung}").si
        return N, M_y, M_z

    def _ein_fall(self, p: Protokoll, e: Eingaben, q: Querschnitt, herkunft: Sequence[str],
                  fall: Lastfall, zug: float, druck: float
                  ) -> Tuple[Optional[NachweisUrteil], float]:
        werte = Zwischenwerte(f"{self.id}.{fall.kennung}")
        d_grad = self.d_ausnutzung[fall.name]
        N, M_y, M_z = self._einwirkung(e, fall)
        p.titel(fall.name, ebene=3)
        self._protokoll_einwirkung(p, e, werte, fall, N, M_y, M_z)

        moment = abs(M_y) if self.einachsig else math.hypot(M_y, M_z)
        N_Ed = werte.kraft("N_Ed_wirk", "N_{Ed}", N)

        # -- Ohne Moment: reine Normalkraft ---------------------------------
        if moment <= KEIN_MOMENT:
            if N == 0.0:
                p.text("Keine Einwirkung → kein Nachweis.")
                self.ergebnisse.append(Fallergebnis(fall, N, M_y, M_z, None, math.inf))
                return None, math.inf
            grenze = zug if N > 0 else druck
            grad = grenze / N if grenze * N > 0 else 0.0
            N_Rd = werte.kraft("N_Rd", "N_{Rd}^{+}" if N > 0 else "N_{Rd}^{-}", grenze)
            erfuellt = grad >= 1.0
            grad_formel(p, d_grad, grad, N_Rd, N_Ed, erfuellt, mit_urteil=True)
            self.ergebnisse.append(Fallergebnis(fall, N, M_y, M_z, None, grad))
            return NachweisUrteil(
                art="M-N", ziel=d_grad.id, fall=fall.name, erfuellt=erfuellt,
                erfuellungsgrad=Groesse(grad, EINHEITSLOS),
                begruendung="Reine Normalkraft: gegen die gleichmässige Dehnung.",
                einwirkung=N_Ed, widerstand=N_Rd), grad

        M_Ed = werte.moment("M_Ed", "M_{Ed}", moment)

        # -- Jenseits der reinen Normalkraft: kein Bruchzustand -------------
        if N > zug or N < druck:
            grenze = zug if N > 0 else druck
            grad = grenze / N
            p.text("Die Normalkraft liegt jenseits dessen, was der Querschnitt "
                   "gleichmässig gedehnt aufnimmt -- es gibt keinen Bruchzustand "
                   "mit diesem N.")
            N_Rd = werte.kraft("N_Rd", "N_{Rd}^{+}" if N > 0 else "N_{Rd}^{-}", grenze)
            grad_formel(p, d_grad, grad, N_Rd, N_Ed, False, mit_urteil=True)
            self.ergebnisse.append(Fallergebnis(fall, N, M_y, M_z, None, grad))
            return NachweisUrteil(
                art="M-N", ziel=d_grad.id, fall=fall.name, erfuellt=False,
                erfuellungsgrad=Groesse(grad, EINHEITSLOS),
                begruendung="N_Ed jenseits der reinen Normalkraft-Tragfähigkeit.",
                einwirkung=N_Ed, widerstand=N_Rd), grad

        # -- Der Bruchzustand -------------------------------------------------
        if self.einachsig:
            punkt = q.bei_normalkraft(-math.pi / 2.0 if M_y >= 0 else math.pi / 2.0, N)
            M_Rd_si = abs(punkt.M_y)
        else:
            punkt = q.in_richtung(N, M_y, M_z)
            M_Rd_si = punkt.moment
        self._protokoll_bruchzustand(p, werte, q, punkt, herkunft)

        M_Rd = werte.moment("M_Rd", "M_{Rd}", M_Rd_si)
        if self.einachsig:
            # Nur sagen, was zutrifft: beim symmetrischen Querschnitt entsteht
            # gar kein M_z, das man uebergehen koennte.
            if abs(punkt.M_z) > 1e-3 * max(M_Rd_si, 1.0):
                p.text(f"Einachsig: nachgewiesen wird M_y. Das M_z = "
                       f"{punkt.M_z / 1e3:.1f} kNm, das der unsymmetrische Querschnitt "
                       f"dabei weckt, wird übergangen.")
        else:
            p.formel(M_Rd, r"\sqrt{@My^{2} + @Mz^{2}}",
                     {"My": werte.moment("M_y_Rd", "M_{y,Rd}", punkt.M_y),
                      "Mz": werte.moment("M_z_Rd", "M_{z,Rd}", punkt.M_z)},
                     titel="Widerstand in der Richtung der Einwirkung")
        grad = M_Rd_si / moment
        erfuellt = grad >= 1.0
        grad_formel(p, d_grad, grad, M_Rd, M_Ed, erfuellt, mit_urteil=True)
        self.ergebnisse.append(Fallergebnis(fall, N, M_y, M_z, punkt, grad))
        return NachweisUrteil(
            art="M-N", ziel=d_grad.id, fall=fall.name, erfuellt=erfuellt,
            erfuellungsgrad=Groesse(grad, EINHEITSLOS),
            begruendung=(f"Bei N_Ed = {N / 1e3:.1f} kN, in der Richtung des Moments."),
            einwirkung=M_Ed, widerstand=M_Rd), grad

    # -- Mitschrift ----------------------------------------------------------------

    def _protokoll_ansatz(self, p: Protokoll, e: Eingaben, q: Querschnitt) -> None:
        p.erklaerung(
            "Der Querschnitt bleibt eben (Bernoulli). Die Dehnung hängt nur vom "
            "Abstand v in Zugrichtung n ab, gemessen ab dem Schwerpunkt; die "
            "Nulllinie steht senkrecht zu n und darf schräg liegen. Zu jeder "
            "Dehnungsebene ergeben sich N, M_y und M_z durch Integration über "
            "die Fläche -- als Summe über Streifen quer zu n, deren Grenzen auf "
            "jede Polygonecke fallen, und Stab für Stab.")
        p.ansatz(
            r"\varepsilon(y, z) = \varepsilon_0 + \kappa \cdot v \qquad "
            r"v = n_y (y - y_S) + n_z (z - z_S) \qquad "
            r"N = \int_A \sigma\,\mathrm{d}A \qquad "
            r"M_y = -\int_A \sigma\,(z - z_S)\,\mathrm{d}A \qquad "
            r"M_z = -\int_A \sigma\,(y - y_S)\,\mathrm{d}A",
            titel="Dehnungsebene und innere Kräfte")
        p.erklaerung(
            "Der Bruchzustand: jede Dehnungsebene, bei der ein Werkstoff an "
            "seiner Grenze steht und keiner darüber. Der Beton wird an seinem "
            "gedrücktesten Punkt bis -ε_c2d gestaucht, ganz gedrückt am C-Punkt "
            "bis -ε_c1d; die Bewehrung bis ±ε_ud. Gesucht wird die Ebene mit "
            "N = N_Ed, deren Moment in die Richtung der Einwirkung zeigt. "
            "Nachgewiesen wird nicht die Suche, sondern ihre Probe: die Kräfte "
            "jedes Teils und ihre Summen.")
        p.ansatz(r"\alpha_{eff} = \frac{M_{Rd}}{M_{Ed}} \qquad M = \sqrt{M_y^2 + M_z^2}",
                 titel="Erfüllungsgrad bei fester Normalkraft und fester Richtung")
        self.analyse.werkstoffe_protokollieren(p, e, self.id)

    def _protokoll_einwirkung(self, p: Protokoll, e: Eingaben, werte: Zwischenwerte,
                              fall: Lastfall, N: float, M_y: float, M_z: float) -> None:
        zeilen = [["N_Ed", Mathe(fest(fall.N / 1e3, 1)), "kN"],
                  ["M_y,Ed", Mathe(fest(fall.M_y / 1e3, 1)), "kNm"]]
        if not self.einachsig:
            zeilen.append(["M_z,Ed", Mathe(fest(fall.M_z / 1e3, 1)), "kNm"])
        if self.laengszug is not None:
            dN = e.g(f"dN_{fall.kennung}").si
            dMy = e.g(f"dM_y_{fall.kennung}").si
            zeilen += [["ΔN aus Querkraft und Torsion", Mathe(fest(dN / 1e3, 1)), "kN"],
                       ["ΔM_y", Mathe(fest(dMy / 1e3, 1)), "kNm"]]
            if not self.einachsig:
                zeilen.append(["ΔM_z", Mathe(fest(e.g(f"dM_z_{fall.kennung}").si / 1e3, 1)),
                               "kNm"])
            zeilen += [["N (nachgewiesen)", Mathe(fest(N / 1e3, 1)), "kN"],
                       ["M_y (nachgewiesen)", Mathe(fest(M_y / 1e3, 1)), "kNm"]]
            if not self.einachsig:
                zeilen.append(["M_z (nachgewiesen)", Mathe(fest(M_z / 1e3, 1)), "kNm"])
        p.tabelle(kopf=["Einwirkung", "Wert", ""], zeilen=zeilen,
                  titel="Einwirkung", ausrichtung="lrl")

    def _protokoll_bruchzustand(self, p: Protokoll, werte: Zwischenwerte, q: Querschnitt,
                                punkt: Bruchpunkt, herkunft: Sequence[str]) -> None:
        n = punkt.zugrichtung
        richtung = math.degrees(math.atan2(n[1], n[0]))
        if punkt.chi > 0.0:
            nulllinie = -punkt.eps_m / punkt.chi * 1e3
            lage = (f"Die Nulllinie steht senkrecht zur Zugrichtung, {abs(nulllinie):.1f} mm "
                    f"{'auf der Zugseite' if nulllinie > 0 else 'auf der Druckseite'} "
                    f"des Schwerpunkts.")
        else:
            lage = "Die Dehnung ist gleichmässig -- keine Nulllinie."
        p.text(f"Bruchzustand: Zugrichtung n = ({n[0]:.3f}; {n[1]:.3f}), "
               f"{richtung:.1f}° gegen die y-Achse. {lage}")
        p.tabelle(kopf=[Mathe(r"\varepsilon_0\ [\text{‰}]"), Mathe(r"\kappa\ [\mathrm{1/m}]")],
                  zeilen=[[Mathe(fest(punkt.eps_m * 1e3, 3)), Mathe(fest(punkt.chi, 5))]],
                  titel="Dehnungsebene", ausrichtung="rr")

        anteile = q.anteile(punkt)
        zeilen = []
        beton = [a for a in anteile[:len(anteile) - len(q.bewehrung)] if a.N != 0.0]
        for a in beton:
            zeilen.append([a.name, Mathe(fest(a.N / 1e3, 1)), Mathe(fest(a.y * 1e3, 1)),
                           Mathe(fest(a.z * 1e3, 1)), "–", "–"])
        staebe = anteile[len(anteile) - len(q.bewehrung):]
        gruppen: Dict[str, List[Kraftanteil]] = {}
        for name, a in zip(herkunft, staebe):
            gruppen.setdefault(name, []).append(a)
        for name, teile in gruppen.items():
            F = sum(a.N for a in teile)
            if F != 0.0:
                y = sum(a.N * a.y for a in teile) / F
                z = sum(a.N * a.z for a in teile) / F
            else:
                y = sum(a.y for a in teile) / len(teile)
                z = sum(a.z for a in teile) / len(teile)
            eps = [a.eps for a in teile]
            sig = [a.sigma for a in teile]
            spanne = lambda werte_, f: (f"{f(werte_[0])}" if len(werte_) == 1 or
                                        abs(max(werte_) - min(werte_)) < 1e-12
                                        else f"{f(min(werte_))} \\ldots {f(max(werte_))}")
            zeilen.append([name, Mathe(fest(F / 1e3, 1)), Mathe(fest(y * 1e3, 1)),
                           Mathe(fest(z * 1e3, 1)),
                           Mathe(spanne(eps, lambda x: fest(x * 1e3, 2))),
                           Mathe(spanne(sig, lambda x: fest(x / 1e6, 0)))])
        p.tabelle(
            kopf=["Teil", Mathe(r"F\ [\mathrm{kN}]"), Mathe(r"y\ [\mathrm{mm}]"),
                  Mathe(r"z\ [\mathrm{mm}]"), Mathe(r"\varepsilon\ [\text{‰}]"),
                  Mathe(r"\sigma\ [\mathrm{N/mm^2}]")],
            zeilen=zeilen, ausrichtung="lrrrrr",
            titel="Kräfte im Bruchzustand -- Beton als Resultierende, Bewehrung je Element")
        y_S, z_S = q.bezug
        p.formel(werte.kraft("N_int", "N_{Rd}", sum(a.N for a in anteile)), r"\sum F_i", {},
                 titel="Probe: Normalkraft")
        p.formel(werte.moment("M_y_int", "M_{y,Rd}",
                              sum(-a.N * (a.z - z_S) for a in anteile)),
                 r"-\sum F_i \cdot (z_i - z_S)", {}, titel="Probe: Moment um y")
        if not self.einachsig:
            p.formel(werte.moment("M_z_int", "M_{z,Rd}",
                                  sum(-a.N * (a.y - y_S) for a in anteile)),
                     r"-\sum F_i \cdot (y_i - y_S)", {}, titel="Probe: Moment um z")
