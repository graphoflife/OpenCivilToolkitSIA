"""
opencivil/nachweis/qa_holz_kennzahlen.py -- was ein Holzquerschnitt aufnimmt, ohne Einwirkung.

VERANTWORTUNG:
Die Kennzahlen eines Querschnitts aus Holz nach SIA 265:2012, wie die des
Stahls (:mod:`opencivil.nachweis.qa_stahl_kennzahlen`) -- gerechnet immer, ob
es Lastfaelle gibt oder nicht. Je Beanspruchung allein, linear (4.1.2), mit
den Bemessungswerten der Tabellen 6 und 7 und dem Beiwert η_w der
Feuchteklasse der Analyse:

* der Zugwiderstand nach (6), der Druckwiderstand nach (10) ohne Knicken;
* je Achse der Biegewiderstand nach (14), beim Brettschichtholz um y mit
  ``k_h``;
* je Richtung der Querkraftwiderstand nach (23), aus der Schubflaeche;
* beim Rechteck der Torsionswiderstand nach (24).

Die Werte des Querschnitts -- ``W``, ``k_h``, ``A_V``, ``W_T`` -- rechnet
:class:`~opencivil.nachweis.qa_holz_werte.HolzwerteQA`; hier stehen nur die
Widerstaende. Stossartig ist hier nichts: ``η_t`` gehoert dem Lastfall.
"""

from __future__ import annotations

import math
from typing import Dict

from opencivil.core.berechnung import Eingabebezug, Eingaben, Kennzahlprozedur
from opencivil.core.einheiten import KN, KNM, Groesse
from opencivil.core.protokoll import Protokoll
from opencivil.core.wert import Wert
from opencivil.holzbau import gleichungen as gl
from opencivil.material.holz import zugglied_grund
from opencivil.nachweis.qa_holz_werte import (
    DRUCK, TORSION_NUR_RECHTECK, ZUG, HolzwerteQA, kennwert, stoffbezuege,
)
from opencivil.querschnitt.analyse import Querschnittsanalyse

#: Die Biegung, je mit und ohne k_h -- eine Vorlage, ein Name.
BIEGUNG = (r"@eta \cdot @f_m \cdot @W", "Biegewiderstand eines Holzquerschnitts")
BIEGUNG_K_H = (r"@eta \cdot @k_h \cdot @f_m \cdot @W", "Biegewiderstand des Brettschichtholzes")


class KennzahlenHolzQA(Kennzahlprozedur):
    """Die Kennzahlen eines Holzquerschnitts -- siehe Dateikopf."""

    THEMA = "Kennzahlen"

    def __init__(self, analyse: Querschnittsanalyse, werte: HolzwerteQA) -> None:
        self.analyse = analyse
        self.werte = werte
        basis = f"{analyse.id}.kennzahlen"
        dazu = self.anlegen(basis)
        klasse = f"Feuchteklasse {werte.feuchte.value}"
        dazu("N_Rd_zug", r"N_{Rd}^{+}", KN, "Zugwiderstand des Querschnitts", "Zugwiderstand",
             f"am gezeichneten Querschnitt, {klasse}", referenz=gl.REFERENZ_6)
        dazu("N_Rd_druck", r"N_{Rd}^{-}", KN, "Druckwiderstand des Querschnitts, ohne Knicken",
             "Druckwiderstand", f"ohne Knicken, {klasse}", referenz=gl.REFERENZ_10)
        for a in werte.achsen:
            mit = ", mit k_h" if self._mit_k_h(a) else ""
            dazu(f"M_{a}_Rd", rf"M_{{{a},Rd}}", KNM, f"Biegewiderstand um {a}",
                 f"Biegewiderstand um {a}", f"bis zur weitesten Faser, ohne Kippen{mit}, {klasse}",
                 referenz=gl.REFERENZ_14)
        for r in werte.richtungen:
            dazu(f"V_{r}_Rd", rf"V_{{{r},Rd}}", KN, f"Querkraftwiderstand in {r}, allein",
                 f"Querkraftwiderstand in {r}", f"am Schnitt mit dem grössten S/b, {klasse}",
                 referenz=gl.REFERENZ_23)
        if werte.holz.rechteck:
            dazu("T_Rd", r"T_{Rd}", KNM, "Torsionswiderstand, allein", "Torsionswiderstand",
                 f"in der Mitte der langen Seite, {klasse}", referenz=gl.REFERENZ_24)
        bezuege = ([Eingabebezug("A", analyse.id_von("A"))] + werte.als_eingaben()
                   + stoffbezuege(werte.stoff))
        super().__init__(basis, bezuege=bezuege, titel=f"Kennzahlen – {analyse.name}",
                         abschnitt=analyse.abschnitt)

    def _mit_k_h(self, achse: str) -> bool:
        """Ob die Biegung um ``achse`` ``k_h`` hat: beim Brettschichtholz um y."""
        return self.werte.brettschicht and achse == "y"

    # -- Rechnen ------------------------------------------------------------

    def rechne(self, e: Eingaben, p: Protokoll) -> Dict[str, Groesse]:
        p.titel("Kennzahlen")
        p.erklaerung(
            "Was der Holzquerschnitt aufnimmt, ohne Bezug auf einen Lastfall: je Beanspruchung "
            "allein, linear, mit den Bemessungswerten der Tabellen und η_w der Feuchteklasse – "
            "ohne stossartige Einwirkung. Knicken und Kippen gehören dem Stab und sind hier "
            "nicht dabei.")
        ergebnis: Dict[str, Groesse] = {}
        stoff = self.werte.stoff
        eta, A = e["eta_w"], e["A"]

        def f(kurz: str) -> Wert:
            return kennwert(e, stoff, kurz)

        def belegen(kurz: str, *faktoren: Wert, vorzeichen: float = 1.0) -> Wert:
            """Die Kennzahl ``kurz`` als Produkt der Faktoren."""
            return self._belegen(ergebnis, kurz,
                                 vorzeichen * math.prod(w.groesse.si for w in faktoren))

        p.titel("Normalkraft", ebene=3)
        p.formel(belegen("N_Rd_zug", eta, f("f_t_0_d"), A), ZUG[0],
                 {"eta": eta, "f_t": f("f_t_0_d"), "A": A}, titel="Zugwiderstand",
                 referenz=gl.REFERENZ_6, name=ZUG[1])
        grund = zugglied_grund(stoff)
        if grund:
            p.hinweis(grund)
        p.formel(belegen("N_Rd_druck", eta, f("f_c_0_d"), A, vorzeichen=-1.0), DRUCK[0],
                 {"eta": eta, "f_c": f("f_c_0_d"), "A": A},
                 titel="Druckwiderstand, ohne Knicken", referenz=gl.REFERENZ_10, name=DRUCK[1])

        p.titel("Biegung", ebene=3)
        for a in self.werte.achsen:
            W = e[f"W_{a}"]
            if self._mit_k_h(a):
                k_h = e["k_h"]
                p.formel(belegen(f"M_{a}_Rd", eta, k_h, f("f_m_d"), W), BIEGUNG_K_H[0],
                         {"eta": eta, "k_h": k_h, "f_m": f("f_m_d"), "W": W},
                         titel=f"Biegewiderstand um {a}, mit dem Höhenbeiwert",
                         referenz=gl.REFERENZ_14, name=BIEGUNG_K_H[1])
            else:
                p.formel(belegen(f"M_{a}_Rd", eta, f("f_m_d"), W), BIEGUNG[0],
                         {"eta": eta, "f_m": f("f_m_d"), "W": W},
                         titel=f"Biegewiderstand um {a}", referenz=gl.REFERENZ_14,
                         name=BIEGUNG[1])

        p.titel("Schub", ebene=3)
        for r in self.werte.richtungen:
            A_V = e[f"A_V_{r}"]
            p.formel(belegen(f"V_{r}_Rd", eta, f("f_v_d"), A_V), r"@eta \cdot @f_v \cdot @A",
                     {"eta": eta, "f_v": f("f_v_d"), "A": A_V},
                     titel=f"Querkraftwiderstand in {r}", referenz=gl.REFERENZ_23,
                     name="Querkraftwiderstand eines Holzquerschnitts")
        if self.werte.holz.rechteck:
            W_T = e["W_T"]
            p.formel(belegen("T_Rd", eta, f("f_v_d"), W_T), r"@eta \cdot @f_v \cdot @W",
                     {"eta": eta, "f_v": f("f_v_d"), "W": W_T}, titel="Torsionswiderstand",
                     referenz=gl.REFERENZ_24, name="Torsionswiderstand eines Rechtecks aus Holz")
        else:
            p.text(TORSION_NUR_RECHTECK)
        return ergebnis
