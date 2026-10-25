"""
opencivil/web/balkendaten.py -- was die Oberflaeche von einem Balkensystem zeigt.

VERANTWORTUNG:
Aus dem Befund eines gerechneten Systems
(:class:`~opencivil.stabwerk.rechnung.Systembefund`) die Daten fuer die Oberflaeche, in den Einheiten der Anzeige -- kN, kNm, mm,
mrad, Stellen in m:

* mit jeder Rechnung eine knappe Uebersicht (:func:`uebersicht`): die
  Meldungen mit den Elementen, die sie betreffen, die Knoten ohne
  Drehsteifigkeit, und je Fall die Extremwerte und die Lagerkraefte;
* auf Anfrage die Verlaeufe eines Falls fuer die Bilder (:func:`verlauf`):
  je Stab Proben von N, V, M und der Verschiebung, je Knoten seine
  Verschiebung -- oder dass seine Drehung nicht bestimmbar ist;
* je Querschnitt sein Umriss fuer das Bildchen in seiner Zeile
  (:func:`umrisse`).

Die Verlaeufe sind gross; mit jeder Rechnung mitgeliefert, machten sie jede
Eingabe langsamer, auch wenn niemand die Bilder ansieht -- dasselbe wie bei
den Diagrammen der Querschnittsanalyse. Gerechnet wird hier nichts, nur
umgerechnet und in Listen gelegt.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from opencivil.stabwerk.rechnung import Balkensystem, Systembefund
from opencivil.stabwerk.system import SUMMEN, UNBESTIMMT, Fall

#: Wie viele Stuecke ein Stab im Bild mindestens hat -- dazu jede Grenze und jeder Extremwert.
PROBEN_JE_STAB = 24

kN, mm, mrad = 1e-3, 1e3, 1e3


def uebersicht(befund: Optional[Systembefund]) -> Dict[str, Any]:
    """
    Was die Oberflaeche nach jeder Rechnung von einem System weiss -- ohne
    die Verlaeufe. Ohne Befund lief es nicht, etwa weil ein Baustoff fehlt.
    """
    if befund is None:
        return {"gerechnet": False}
    e = befund.ergebnis
    return {
        "gerechnet": True,
        "gueltig": e.gueltig,
        "meldungen": [{"text": m.text, "elemente": list(m.elemente), "fehler": m.fehler}
                      for m in e.meldungen],
        "unbestimmt": e.unbestimmt(),
        "unbestimmt_text": UNBESTIMMT,
        "summen_text": SUMMEN,
        "beweglich": list(e.beweglich),
        "unbekannte": len(e.unbekannte),
        "faelle": [_fall(befund, f) for f in e.faelle],
        # Das Eigengewicht je Stab in kN/m -- das Zeichenfenster zeigt es im
        # Lastfall, der es bekommt; gewaehlt und geloescht wird es nicht.
        "eigengewicht": {stab: g * kN for stab, g in befund.eigengewicht.items()},
    }


def _fall(befund: Systembefund, fall: Fall) -> Dict[str, Any]:
    staebe = {}
    for name, v in befund.verlaeufe(fall.name).items():
        extrem = {}
        for groesse, faktor in (("N", kN), ("V", kN), ("M", kN), ("w", mm), ("phi", mrad)):
            e = v.extrem(groesse)
            extrem[groesse] = {"kleinst": [e.kleinst[0], e.kleinst[1] * faktor],
                               "groesst": [e.groesst[0], e.groesst[1] * faktor]}
        staebe[name] = extrem
    return {
        "name": fall.name,
        "kombination": fall.kombination,
        "staebe": staebe,
        # Dieselben Zeilen wie in der Herleitung -- mit den Summen von
        # Linienlager und Bettung, sonst gingen die Kraefte nicht auf.
        "lagerkraefte": [
            {"wo": k.wo, "knoten": k.knoten, "summe": k.summe,
             "R_x": k.R_x * kN, "R_z": k.R_z * kN, "M": k.M * kN}
            for k in befund.lagerkraefte(fall)],
    }


def verlauf(befund: Systembefund, name: str) -> Dict[str, Any]:
    """Die Bilder eines Falls: je Stab die Proben, je Knoten die Verschiebung."""
    fall = befund.ergebnis.fall(name)
    staebe = {}
    for stab, v in befund.verlaeufe(name).items():
        staebe[stab] = {
            "L": v.L, "c": v.c, "s": v.s, "x_a": v.x_a, "z_a": v.z_a,
            "proben": [{"x": w["x"], "N": w["N"] * kN, "V": w["V"] * kN, "M": w["M"] * kN,
                        "ux": w["ux"] * mm, "uz": w["uz"] * mm, "w": w["w"] * mm,
                        "phi": w["phi"] * mrad}
                       for w in v.proben(PROBEN_JE_STAB)],
        }
    knoten = {}
    for ort in befund.ergebnis.orte.values():
        if not ort.knoten:
            continue
        ux, uz, phi = fall.verschiebungen[ort.name]
        unbestimmt = ort.drehung == "unbestimmt"
        knoten[ort.knoten] = {"x": ort.x, "z": ort.z, "ux": ux * mm, "uz": uz * mm,
                              "phi": None if unbestimmt else phi * mrad,
                              "unbestimmt": unbestimmt}
    return {"fall": name, "kombination": fall.kombination, "staebe": staebe,
            "knoten": knoten, "unbestimmt_text": UNBESTIMMT}


def faelle(befund: Optional[Systembefund]) -> List[str]:
    """Die Namen der gerechneten Faelle, Lastfaelle zuerst."""
    return [f.name for f in befund.ergebnis.faelle] if befund is not None else []


def umrisse(system: Balkensystem, loesung: Any) -> Dict[str, List[List[List[float]]]]:
    """
    Je Querschnitt eines Systems sein Umriss in mm, fuer das Bildchen in
    seiner Zeile (Benutzer, 2026-10-24) -- ihn kennt jeder Querschnitt selbst
    (:meth:`~opencivil.stabwerk.stabquerschnitt.Stabquerschnitt.umriss`).
    Ein Querschnitt, der nicht geht, hat keinen.
    """
    return {q.kennung: [[[round(y, 1), round(z, 1)] for y, z in p]
                        for p in ([] if q.fehler else q.umriss(loesung))]
            for q in system.querschnitte}
