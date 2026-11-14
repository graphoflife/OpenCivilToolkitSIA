"""
opencivil/pfahl/uebersicht.py -- was über der Nachweistabelle eines Pfahls steht.

VERANTWORTUNG:
Die Angaben zum Pfahl, aus den Werten der Lösung (:func:`angaben`), und die
Widerstände beider Nachweise nebeneinander, auf Druck und auf Zug -- vom
Mantel bis zum Bemessungswert (:func:`widerstandstabelle`). Gerechnet wird
hier nichts: die Zahlen stehen in den Befunden.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from opencivil.core.latex import Mathe, Zelle, als_text, angabe, fest
from opencivil.core.protokoll import GleichungBlock, TabellenBlock
from opencivil.core.wert import Wert
from opencivil.pfahl.aussen import Aussenbefund
from opencivil.pfahl.innen import Innenbefund
from opencivil.pfahl.pfahl import Pfahl


def angaben(pfahl: Pfahl, werte: Dict[str, Wert]) -> GleichungBlock:
    """
    In der ersten Zeile Art, Masse und Grundwasser, in der zweiten der
    Querschnitt mit η_i und die Grundlage des äusseren Widerstands mit η_a.
    """
    def teile(namen: List[str]) -> List[str]:
        return [angabe(werte[pfahl.id_von(n)]) for n in namen if pfahl.id_von(n) in werte]

    oben = [als_text(pfahl.art.beschriftung), *teile(["D", "L", "t_K", "t_w"])]
    unten = [*teile(pfahl.kurznamen("Querschnitt")),
             als_text(pfahl.grundlage.beschriftung), *teile(["eta_a"])]
    return GleichungBlock(
        latex=(r"\begin{aligned} & " + r" \qquad ".join(oben) + r" \\ & "
               + r" \qquad ".join(unten) + r" \end{aligned}"),
        titel="Angaben zum Pfahl")


def widerstandstabelle(aussen: Optional[Aussenbefund],
                       innen: Optional[Innenbefund]) -> TabellenBlock:
    """Je Widerstand eine Zeile, in kN: Druck und Zug nebeneinander."""
    def kn(si: Optional[float]) -> Zelle:
        return "–" if si is None else Mathe(fest(si / 1e3, 0))

    zeilen: List[List[Zelle]] = []
    if aussen is not None:
        if not aussen.aus_versuch:
            zeilen += [["Mantel", Mathe("R_{s,k}"), kn(aussen.R_s), kn(aussen.R_s)],
                       ["Fuss", Mathe("R_{b,k}"), kn(aussen.R_b), kn(None)]]
        zeilen += [["Äusserer, charakteristisch", Mathe("R_{a,k}"), kn(aussen.R_ak),
                    kn(aussen.R_ak_zug)],
                   ["Äusserer, Bemessungswert", Mathe("R_{a,d}"), kn(aussen.R_ad),
                    kn(aussen.R_ad_zug)]]
    if innen is not None:
        zeilen += [["Querschnitt", Mathe("R_{mat,d}"), kn(innen.R_mat), kn(innen.R_mat_zug)],
                   ["Innerer, Bemessungswert", Mathe("R_{i,d}"), kn(innen.R_id),
                    kn(innen.R_id_zug)]]
    return TabellenBlock(kopf=["Widerstand", "", Mathe(r"\text{Druck}\ [\mathrm{kN}]"),
                               Mathe(r"\text{Zug}\ [\mathrm{kN}]")],
                         zeilen=zeilen, titel="Widerstände", ausrichtung="llrr")
