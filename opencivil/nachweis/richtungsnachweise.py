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

from typing import Dict, List

from opencivil.core.berechnung import Ausfuehrung, Eingaben
from opencivil.core.nachweis import NICHT_FUEHRBAR, Nachweis, NachweisUrteil, Vergleich, grad_def
from opencivil.core.latex import als_text, angabe, vergleich
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import WertDef, kennung_aus
from opencivil.material.basis import Baustoffart
from opencivil.nachweis import duktilitaet
from opencivil.nachweis.rissgroessen import (
    bruttoquerschnitt, protokoll_rissmoment, protokoll_spannung_ungerissen, rissbezuege,
    rissmoment,
)
from opencivil.nachweis.sproedes_versagen import SproedesVersagen
from opencivil.querschnitt.analyse import Querschnittsanalyse


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
    """``x/d <= k * 435 N/mm^2 / f_yd`` bei reiner Biegung, je Richtung."""

    THEMA = "Duktilität je Richtung"
    LANGNAME = "Duktilität"
    ART = "x/d"

    def __init__(self, analyse: Querschnittsanalyse, *, beiwert: float) -> None:
        self.analyse = analyse
        self.beiwert = beiwert
        basis = f"{analyse.id}.nachweis.duktilitaet"
        self.d_ausnutzung = grade_je_seite(basis, "x/d", "Erfüllungsgrad Duktilität",
                                           duktilitaet.REFERENZ, analyse)
        super().__init__(basis, ausgaben=list(self.d_ausnutzung.values()),
                         bezuege=analyse.grundbezuege(),
                         titel=f"Duktilität – {analyse.name}",
                         referenz=duktilitaet.REFERENZ, abschnitt=analyse.abschnitt)

    def pruefe(self, e: Eingaben, p: Protokoll):
        q, _ = self.analyse.interaktion(e)
        p.erklaerung(
            "Ein Querschnitt kann Schnittgrössen umlagern, wenn die Bewehrung "
            "fliesst, bevor der Beton bricht -- dann ist die Druckzone klein. "
            "Gemessen wird das an x/d bei reiner Biegung: x ist der Abstand der "
            "Nulllinie vom gedrücktesten Betonpunkt, d der des Schwerpunkts der "
            "Zugbewehrung, beide senkrecht zur Nulllinie. Zur Zugbewehrung "
            "zählen die gedehnten Stäbe auf der gezogenen Seite des "
            "Schwerpunkts; liegen dort verschiedene Stähle, gilt die Grenze des "
            "festesten.")
        duktilitaet.protokoll_bedingung(p, self.beiwert)
        f_ck = max((self.analyse.kennwert(e, s, "f_ck") for s in self.analyse.baustoffe
                    if s.art is Baustoffart.BETON), default=0.0)
        urteile: List[NachweisUrteil] = []
        for seite in self.analyse.zugseiten:
            name = seite.beschriftung
            werte = Zwischenwerte(f"{self.id}.{kennung_aus(name)}")
            d_grad = self.d_ausnutzung[name]
            punkt = self.analyse.biegung.bei_reiner_biegung(q, seite)
            x, d = q.druckzone(punkt)
            p.titel(name, ebene=3)
            if d <= 0.0:
                p.text("Keine Bewehrung auf der gezogenen Seite → kein Nachweis.")
                continue
            # Die Werkstoffe der Interaktion stehen in der Reihenfolge der Baustoffe.
            staehle = [self.analyse.baustoffe[w]
                       for w in sorted({s.werkstoff for _, s in q.zugbewehrung(punkt)})]
            grund = duktilitaet.hindernis(staehle, f_ck)
            if grund:
                p.text(grund)
                urteile.append(self.urteil(d_grad, name, NICHT_FUEHRBAR, grund))
                continue
            stahl = max(staehle, key=lambda s: self.analyse.kennwert(e, s, "f_yd"))
            grenze = duktilitaet.grenze(self.beiwert, self.analyse.kennwert(e, stahl, "f_yd"))
            g = werte.zahl("grenze", r"\left(x/d\right)_{max}", grenze)
            duktilitaet.protokoll_grenze(p, werte, g, beiwert=self.beiwert,
                                         f_yd=e[stahl.eingabename("f_yd")])
            verhaeltnis = x / d
            x_d = werte.zahl("x_d", "x/d", verhaeltnis)
            v = Vergleich(x_d, g)
            p.formel(x_d, r"\frac{@x}{@d}",
                     {"x": werte.laenge("x", "x", x), "d": werte.laenge("d", "d", d)},
                     titel="Bezogene Druckzonenhöhe bei reiner Biegung",
                     nachsatz=vergleich(r"\le", angabe(g), v.erfuellt))
            v.zeile(p, d_grad)
            urteile.append(self.urteil(d_grad, name, v,
                                       f"x/d = {verhaeltnis:.3f} gegen {grenze:.3f}."))
        self.protokoll_massgebend(p, urteile)
        return Ausfuehrung({}, self.teilurteile(urteile))


class SproedesVersagenQA(Nachweis):
    """``M_Rd(N = 0) >= M_Riss`` je Richtung."""

    THEMA = "Sprödes Versagen je Richtung"
    LANGNAME = "Sprödes Versagen"
    ART = "Riss"

    def __init__(self, analyse: Querschnittsanalyse) -> None:
        self.analyse = analyse
        basis = f"{analyse.id}.nachweis.sproede"
        self.d_ausnutzung = grade_je_seite(basis, "Riss", "Erfüllungsgrad sprödes Versagen",
                                           SproedesVersagen.REFERENZ, analyse)
        super().__init__(basis, ausgaben=list(self.d_ausnutzung.values()),
                         bezuege=analyse.grundbezuege() + rissbezuege(analyse),
                         titel=f"Sprödes Versagen – {analyse.name}",
                         referenz=SproedesVersagen.REFERENZ, abschnitt=analyse.abschnitt)

    def pruefe(self, e: Eingaben, p: Protokoll):
        q, _ = self.analyse.interaktion(e)
        p.erklaerung(
            "Ein zu schwach bewehrter Querschnitt reisst und versagt im selben "
            "Augenblick. Darum muss der bewehrte Querschnitt mehr tragen als der "
            "unbewehrte im Augenblick des Risses: M_Rd bei N = 0 mindestens das "
            "Rissmoment. Das Rissmoment gehört dem ungerissenen "
            "Bruttoquerschnitt; bei unsymmetrischer Form mit dem "
            "Deviationsmoment.")
        protokoll_spannung_ungerissen(p, self.analyse.biegung)
        p.ansatz(r"M_{Rd}(N = 0) \ge M_{Riss} = f_{ct,eff} \cdot W",
                 titel="Sprödes Versagen", referenz=SproedesVersagen.REFERENZ,
                 name="Bedingung gegen sprödes Versagen")

        brutto = bruttoquerschnitt(self.analyse, e.si_nach_id())
        urteile: List[NachweisUrteil] = []
        for seite in self.analyse.zugseiten:
            name, (M_y, M_z) = seite.beschriftung, seite.moment
            werte = Zwischenwerte(f"{self.id}.{kennung_aus(name)}")
            d_grad = self.d_ausnutzung[name]
            p.titel(name, ebene=3)
            punkt = self.analyse.biegung.bei_reiner_biegung(q, seite)
            _, d = q.druckzone(punkt)
            if d <= 0.0:
                p.text("Keine Bewehrung auf der gezogenen Seite → kein Nachweis.")
                continue

            riss = rissmoment(brutto, M_y, M_z)
            M_Riss = protokoll_rissmoment(p, e, self.analyse, werte, brutto, riss, M_y, M_z,
                                          referenz=SproedesVersagen.REFERENZ)
            M_Rd_si = self.analyse.biegung.betrag(punkt.M_y, punkt.M_z)
            M_Rd = werte.moment("M_Rd", "M_{Rd}", M_Rd_si)
            p.wert(M_Rd, titel="Biegewiderstand bei N = 0 in dieser Richtung")
            v = Vergleich(M_Riss, M_Rd)
            v.zeile(p, d_grad)
            urteile.append(self.urteil(d_grad, name, v, "M_Rd bei N = 0 gegen das Rissmoment."))
        self.protokoll_massgebend(p, urteile)
        return Ausfuehrung({}, self.teilurteile(urteile))
