"""
opencivil/nachweis/richtungsnachweise.py -- Duktilitaet und sproedes Versagen des gezeichneten Querschnitts.

VERANTWORTUNG:
Zwei Nachweise, die wie bei der Platte dem Querschnitt gehoeren und keinem
Lastfall: Duktilitaet (``x/d``) und sproedes Versagen (``M_Rd >= M_Riss``).
Wo die Platte je Lage fragt, fragt der gezeichnete Querschnitt je Richtung:
Zug unten, oben, links, rechts -- einachsig nur unten und oben. In der
Zusammenfassung steht die unguenstigere.

Gerechnet wird bei reiner Biegung, ``N = 0``, mit dem Bruchzustand aus
:mod:`opencivil.querschnitt.interaktion`. Eine Richtung ohne Bewehrung auf
ihrer gezogenen Seite des Schwerpunkts hat keinen solchen Nachweis -- dort
steht ein Satz und kein Urteil, wie bei einer unbewehrten Lage der Platte.

ANNAHMEN:
Das Rissmoment gehoert dem ungerissenen Bruttoquerschnitt: unter reiner
Biegung das Moment, bei dem ``f_ct,eff`` zum ersten Mal irgendwo erreicht
wird -- mit ``I_yz``, einachsig mit waagrechter Nulllinie. Es steht mit den
uebrigen Rissgroessen an einer Stelle (:mod:`opencivil.nachweis.rissgroessen`);
die Zwaengung auf Biegung (:mod:`opencivil.nachweis.qa_gebrauch`) haelt
dasselbe Rissmoment gegen ihre Bewehrung.
"""

from __future__ import annotations

import math
from typing import Dict, List

from opencivil.core.berechnung import (
    Ausfuehrung, Eingaben, Nachweis, NachweisUrteil, grad_def, grad_formel,
)
from opencivil.core.einheiten import EINHEITSLOS, Groesse
from opencivil.core.latex import als_text, vergleich
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import WertDef, kennung_aus
from opencivil.nachweis.duktilitaet import DUKTILITAETSBEDINGUNG
from opencivil.nachweis.rissgroessen import (
    bruttoquerschnitt, protokoll_rissmoment, protokoll_spannung_ungerissen, rissbezuege,
    rissmoment,
)
from opencivil.querschnitt.analyse import Querschnittsanalyse
from opencivil.querschnitt.interaktion import Bruchpunkt, Querschnitt
from opencivil.querschnitt.zugseite import Zugseite


def bei_reiner_biegung(q: Querschnitt, seite: Zugseite, einachsig: bool) -> Bruchpunkt:
    """Der Bruchzustand bei N = 0, der diese Seite zieht -- einachsig mit waagrechter Nulllinie."""
    if einachsig:
        return q.bei_normalkraft(seite.psi, 0.0)
    return q.in_richtung(0.0, *seite.moment)


# ===========================================================================
# Die Nachweise
# ===========================================================================


def grade_je_seite(basis: str, symbol: str, beschreibung: str, referenz: str,
                   analyse: Querschnittsanalyse) -> Dict[str, WertDef]:
    """
    Je Zugseite der Analyse ein Erfuellungsgrad -- Kennung, Zeichen und Text
    nach einem Muster fuer alle Nachweise des gezeichneten Querschnitts, die
    je Seite urteilen: ``alpha_{eff,<symbol>,<Seite>}``.
    """
    namen = [seite.beschriftung for seite in analyse.zugseiten]
    return {name: grad_def(f"{basis}.{kennung_aus(name)}.erfuellungsgrad",
                           rf"\alpha_{{eff,{symbol},{als_text(name)}}}",
                           f"{beschreibung} – {name}", referenz)
            for name in namen}


class DuktilitaetQA(Nachweis):
    """``x/d <= Grenze`` bei reiner Biegung, je Richtung."""

    THEMA = "Duktilität je Richtung"
    LANGNAME = "Duktilität"

    def __init__(self, analyse: Querschnittsanalyse, *, grenze: float) -> None:
        self.analyse = analyse
        self.grenze = grenze
        basis = f"{analyse.id}.nachweis.duktilitaet"
        self.d_ausnutzung = grade_je_seite(basis, "x/d", "Erfüllungsgrad Duktilität",
                                           "SIA 262:2025, 4.1.4.2.5", analyse)
        super().__init__(basis, ausgaben=list(self.d_ausnutzung.values()),
                         bezuege=analyse.grundbezuege(),
                         titel=f"Duktilität – {analyse.name}",
                         referenz="SIA 262:2025, 4.1.4.2.5", abschnitt=analyse.abschnitt)

    def pruefe(self, e: Eingaben, p: Protokoll):
        q, _ = self.analyse.interaktion(e)
        p.erklaerung(
            "Ein Querschnitt kündigt sein Versagen an, wenn die Bewehrung fliesst, "
            "bevor der Beton bricht -- dann ist die Druckzone klein. Gemessen wird "
            "das an x/d bei reiner Biegung: x ist der Abstand der Nulllinie vom "
            "gedrücktesten Betonpunkt, d der des entferntesten gezogenen Stabs, "
            "beide senkrecht zur Nulllinie.")
        p.ansatz(r"\frac{x}{d} \le \left(\frac{x}{d}\right)_{max}",
                 titel="Duktilität", referenz="SIA 262:2025, 4.1.4.2.5",
                 name=DUKTILITAETSBEDINGUNG)
        ergebnis: Dict[str, Groesse] = {}
        urteile: List[NachweisUrteil] = []
        for seite in self.analyse.zugseiten:
            name = seite.beschriftung
            werte = Zwischenwerte(f"{self.id}.{kennung_aus(name)}")
            d_grad = self.d_ausnutzung[name]
            punkt = bei_reiner_biegung(q, seite, self.analyse.einachsig)
            x, d = q.druckzone(punkt)
            p.titel(name, ebene=3)
            if d <= 0.0 or not q.zugseite_bewehrt(punkt):
                p.text("Keine Bewehrung auf der gezogenen Seite → kein Nachweis.")
                ergebnis[d_grad.id] = Groesse(math.inf, EINHEITSLOS)
                continue
            verhaeltnis = x / d
            erfuellt = verhaeltnis <= self.grenze
            x_d = werte.zahl("x_d", "x/d", verhaeltnis)
            grenze = werte.zahl("grenze", r"\left(x/d\right)_{max}", self.grenze, stellen=2)
            p.formel(x_d, r"\frac{@x}{@d}",
                     {"x": werte.laenge("x", "x", x), "d": werte.laenge("d", "d", d)},
                     titel="Bezogene Druckzonenhöhe bei reiner Biegung",
                     nachsatz=vergleich(r"\le", f"{self.grenze:g}", erfuellt))
            grad = self.grenze / verhaeltnis if verhaeltnis > 0 else math.inf
            if math.isinf(grad):
                grad = 1e9
            grad_formel(p, d_grad, grad, grenze, x_d, erfuellt)
            ergebnis[d_grad.id] = Groesse(grad, EINHEITSLOS)
            urteile.append(NachweisUrteil(
                art="x/d", ziel=d_grad.id, fall=name, erfuellt=erfuellt,
                erfuellungsgrad=Groesse(grad, EINHEITSLOS),
                begruendung=f"x/d = {verhaeltnis:.3f} gegen {self.grenze:g}.",
                einwirkung=x_d, widerstand=grenze))
        self.protokoll_massgebend(p, urteile)
        return Ausfuehrung(ergebnis, self.teilurteile(urteile))


class SproedesVersagenQA(Nachweis):
    """``M_Rd(N = 0) >= M_Riss`` je Richtung."""

    THEMA = "Sprödes Versagen je Richtung"
    LANGNAME = "Sprödes Versagen"

    def __init__(self, analyse: Querschnittsanalyse) -> None:
        self.analyse = analyse
        basis = f"{analyse.id}.nachweis.sproede"
        self.d_ausnutzung = grade_je_seite(basis, "Riss", "Erfüllungsgrad sprödes Versagen",
                                           "SIA 262:2025, 4.4.1.3", analyse)
        super().__init__(basis, ausgaben=list(self.d_ausnutzung.values()),
                         bezuege=analyse.grundbezuege() + rissbezuege(analyse),
                         titel=f"Sprödes Versagen – {analyse.name}",
                         referenz="SIA 262:2025, 4.4.1.3", abschnitt=analyse.abschnitt)

    def pruefe(self, e: Eingaben, p: Protokoll):
        q, _ = self.analyse.interaktion(e)
        p.erklaerung(
            "Ein zu schwach bewehrter Querschnitt reisst und versagt im selben "
            "Augenblick. Darum muss der bewehrte Querschnitt mehr tragen als der "
            "unbewehrte im Augenblick des Risses: M_Rd bei N = 0 mindestens das "
            "Rissmoment. Das Rissmoment gehört dem ungerissenen "
            "Bruttoquerschnitt; bei unsymmetrischer Form mit dem "
            "Deviationsmoment.")
        protokoll_spannung_ungerissen(p, einachsig=self.analyse.einachsig)
        p.ansatz(r"M_{Rd}(N = 0) \ge M_{Riss} = f_{ct,eff} \cdot W",
                 titel="Sprödes Versagen", referenz="SIA 262:2025, 4.4.1.3",
                 name="Bedingung gegen sprödes Versagen")

        brutto = bruttoquerschnitt(self.analyse, e.si_nach_id())
        ergebnis: Dict[str, Groesse] = {}
        urteile: List[NachweisUrteil] = []
        for seite in self.analyse.zugseiten:
            name, (M_y, M_z) = seite.beschriftung, seite.moment
            werte = Zwischenwerte(f"{self.id}.{kennung_aus(name)}")
            d_grad = self.d_ausnutzung[name]
            p.titel(name, ebene=3)
            punkt = bei_reiner_biegung(q, seite, self.analyse.einachsig)
            _, d = q.druckzone(punkt)
            if d <= 0.0 or not q.zugseite_bewehrt(punkt):
                p.text("Keine Bewehrung auf der gezogenen Seite → kein Nachweis.")
                ergebnis[d_grad.id] = Groesse(math.inf, EINHEITSLOS)
                continue

            riss = rissmoment(brutto, M_y, M_z)
            M_Riss = protokoll_rissmoment(p, e, self.analyse, werte, brutto, riss, M_y, M_z,
                                          referenz="SIA 262:2025, 4.4.1.3")
            M_Rd_si = abs(punkt.M_y) if self.analyse.einachsig else punkt.moment
            M_Rd = werte.moment("M_Rd", "M_{Rd}", M_Rd_si)
            p.wert(M_Rd, titel="Biegewiderstand bei N = 0 in dieser Richtung")
            grad = M_Rd_si / riss.M_Riss
            erfuellt = grad >= 1.0
            grad_formel(p, d_grad, grad, M_Rd, M_Riss, erfuellt)
            ergebnis[d_grad.id] = Groesse(grad, EINHEITSLOS)
            urteile.append(NachweisUrteil(
                art="Riss", ziel=d_grad.id, fall=name, erfuellt=erfuellt,
                erfuellungsgrad=Groesse(grad, EINHEITSLOS),
                begruendung="M_Rd bei N = 0 gegen das Rissmoment.",
                einwirkung=M_Riss, widerstand=M_Rd))
        self.protokoll_massgebend(p, urteile)
        return Ausfuehrung(ergebnis, self.teilurteile(urteile))
