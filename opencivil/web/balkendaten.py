"""
opencivil/web/balkendaten.py -- was die Oberflaeche von einem Balkensystem zeigt.

VERANTWORTUNG:
Aus einem gerechneten System (:class:`~opencivil.stabwerk.rechnung.Balkensystem`)
die Daten fuer die Oberflaeche, in den Einheiten der Anzeige -- kN, kNm, mm,
mrad, Stellen in m:

* mit jeder Rechnung eine knappe Uebersicht (:func:`uebersicht`): die
  Meldungen mit den Elementen, die sie betreffen, die Knoten ohne
  Drehsteifigkeit, und je Fall die Extremwerte und die Lagerkraefte;
* auf Anfrage die Verlaeufe eines Falls fuer die Bilder (:func:`verlauf`):
  je Stab Proben von N, V, M und der Verschiebung, je Knoten seine
  Verschiebung -- oder dass seine Drehung nicht bestimmbar ist.

Die Verlaeufe sind gross; mit jeder Rechnung mitgeliefert, machten sie jede
Eingabe langsamer, auch wenn niemand die Bilder ansieht -- dasselbe wie bei
den Diagrammen der Querschnittsanalyse. Gerechnet wird hier nichts, nur
umgerechnet und in Listen gelegt.
"""

from __future__ import annotations

from typing import Any, Dict, List

from opencivil.stabwerk.rechnung import Balkensystem
from opencivil.stabwerk.system import UNBESTIMMT, Fall

#: Wie viele Stuecke ein Stab im Bild mindestens hat -- dazu jede Grenze und jeder Extremwert.
PROBEN_JE_STAB = 24

kN, mm, mrad = 1e-3, 1e3, 1e3


def uebersicht(system: Balkensystem) -> Dict[str, Any]:
    """Was die Oberflaeche nach jeder Rechnung von einem System weiss -- ohne die Verlaeufe."""
    e = system.ergebnis
    if e is None:
        return {"gerechnet": False}
    return {
        "gerechnet": True,
        "gueltig": e.gueltig,
        "meldungen": [{"text": m.text, "elemente": list(m.elemente), "fehler": m.fehler}
                      for m in e.meldungen],
        "unbestimmt": e.unbestimmt(),
        "unbestimmt_text": UNBESTIMMT,
        "beweglich": list(e.beweglich),
        "unbekannte": len(e.unbekannte),
        "faelle": [_fall(system, f) for f in e.faelle],
    }


def _fall(system: Balkensystem, fall: Fall) -> Dict[str, Any]:
    staebe = {}
    for name, v in system.verlaeufe(fall.name).items():
        extrem = {}
        for groesse, faktor in (("N", kN), ("V", kN), ("M", kN), ("w", mm)):
            e = v.extrem(groesse)
            extrem[groesse] = {"kleinst": [e.kleinst[0], e.kleinst[1] * faktor],
                               "groesst": [e.groesst[0], e.groesst[1] * faktor]}
        staebe[name] = extrem
    orte = system.ergebnis.orte
    return {
        "name": fall.name,
        "kombination": fall.kombination,
        "staebe": staebe,
        "lagerkraefte": [
            {"ort": name, "knoten": orte[name].knoten, "stab": orte[name].stab,
             "stelle": orte[name].stelle, "R_x": rx * kN, "R_z": rz * kN, "M": rm * kN}
            for name, (rx, rz, rm) in fall.lagerkraefte.items()],
    }


def verlauf(system: Balkensystem, name: str) -> Dict[str, Any]:
    """Die Bilder eines Falls: je Stab die Proben, je Knoten die Verschiebung."""
    fall = system.ergebnis.fall(name)
    staebe = {}
    for stab, v in system.verlaeufe(name).items():
        staebe[stab] = {
            "L": v.L, "c": v.c, "s": v.s, "x_a": v.x_a, "z_a": v.z_a,
            "proben": [{"x": w["x"], "N": w["N"] * kN, "V": w["V"] * kN, "M": w["M"] * kN,
                        "ux": w["ux"] * mm, "uz": w["uz"] * mm, "w": w["w"] * mm}
                       for w in v.proben(PROBEN_JE_STAB)],
        }
    knoten = {}
    for ort in system.ergebnis.orte.values():
        if not ort.knoten:
            continue
        ux, uz, phi = fall.verschiebungen[ort.name]
        unbestimmt = ort.drehung == "unbestimmt"
        knoten[ort.knoten] = {"x": ort.x, "z": ort.z, "ux": ux * mm, "uz": uz * mm,
                              "phi": None if unbestimmt else phi * mrad,
                              "unbestimmt": unbestimmt}
    return {"fall": name, "kombination": fall.kombination, "staebe": staebe,
            "knoten": knoten, "unbestimmt_text": UNBESTIMMT}


def faelle(system: Balkensystem) -> List[str]:
    """Die Namen der gerechneten Faelle, Lastfaelle zuerst."""
    return [f.name for f in system.ergebnis.faelle] if system.ergebnis else []
