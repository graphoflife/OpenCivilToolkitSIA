"""
opencivil/web/durchstanzdaten.py -- was die Oberflaeche von einer Durchstanzstelle zeichnet.

VERANTWORTUNG:
Je Durchstanzstelle der Grundriss, wie der Kern ihn gerechnet hat, in mm:
der Umriss der gestützten Fläche, die Plattenränder, die Aussparungen und
der Nachweisschnitt -- je Stück, ob es zählt. Dazu die Zahlen der Legende.
Gezeichnet wird in der Oberflaeche, gerechnet nichts: die Linien kommen aus
dem Befund des Nachweises (:mod:`opencivil.durchstanzen.nachweis`).
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from opencivil.core.rechenwerk import Loesung
from opencivil.durchstanzen.nachweis import Durchstanzbefund
from opencivil.projekt import Aufbau

mm = 1e3


def _punkte(punkte) -> list:
    return [[p[0] * mm, p[1] * mm] for p in punkte]


def situationen(aufbau: Aufbau, loesung: Loesung) -> Dict[str, Any]:
    """Je Durchstanzstelle, nach Kennung, was die Zeichnung vom Kern braucht."""
    return {kennung: situation(aufbau, kennung, loesung)
            for kennung in aufbau.objekte("durchstanzen")}


def situation(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Optional[Dict[str, Any]]:
    """Was der Grundriss einer Stelle braucht -- ``None``, wenn ihr Nachweis nicht gelaufen ist."""
    nachweis = aufbau.feld("durchstanzen").get(kennung)
    befund: Optional[Durchstanzbefund] = (
        loesung.befunde.get(nachweis.id) if nachweis is not None else None)
    if befund is None:
        return None
    a = befund.schnitt.massgebend
    urteil = next(u for u in loesung.urteile if u.raum == nachweis.id)
    return {
        "umriss": _punkte(befund.umriss),
        "raender": [{"punkt": [p[0] * mm, p[1] * mm], "richtung": richtung}
                    for p, richtung in befund.raender],
        "aussparungen": [_punkte(x) for x in befund.aussparungen],
        "schnitt": [{"punkte": _punkte(l.punkte), "zaehlt": l.zaehlt} for l in a.linien],
        "schwerpunkt": [a.schwerpunkt[0] * mm, a.schwerpunkt[1] * mm],
        "d_v": befund.d_v * mm,
        "u": befund.u * mm,
        "k_e": befund.k_e,
        "psi": befund.psi,
        "V_d": befund.V_d_red / 1e3,
        "V_Rd_c": befund.V_Rd_c / 1e3,
        "erfuellt": urteil.erfuellt,
        "grad": urteil.gradtext(),
    }
