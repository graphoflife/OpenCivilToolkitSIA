"""
opencivil/web/durchstanzdaten.py -- was die Oberflaeche von einer Durchstanzstelle zeichnet.

VERANTWORTUNG:
Je Durchstanzstelle der Grundriss, wie der Kern ihn gerechnet hat, in mm:
der Umriss der gestützten Fläche, die Plattenränder, die Aussparungen und
der Nachweisschnitt -- je Stück, ob es zählt --, und wo es eine braucht, die
Durchstanzbewehrung: die Leisten mit ihren Ankern und der äussere Schnitt.
Dazu die Zahlen der Legende.
Gezeichnet wird in der Oberflaeche, gerechnet nichts: die Linien kommen aus
dem Befund des Nachweises (:mod:`opencivil.durchstanzen.nachweis`).
"""

from __future__ import annotations

import math
from typing import Any, Dict, Optional

from opencivil.core.rechenwerk import Loesung
from opencivil.durchstanzen.mit_bewehrung import Bewehrungsbefund
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
    urteile = [u for u in loesung.urteile if u.raum == nachweis.id]
    massgebend = min(urteile, key=lambda u: u.erfuellungsgrad.si)
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
        "erfuellt": all(u.erfuellt for u in urteile),
        "grad": massgebend.gradtext(),
        "bewehrung": _bewehrung(befund.bewehrung),
    }


def _bewehrung(b: Optional[Bewehrungsbefund]) -> Optional[Dict[str, Any]]:
    """
    Was die Bemessung vorschlägt, in mm und kN: die Leisten mit ihren Ankern
    und der äussere Schnitt um sie, der Stahlpilz mit seinen Stegen und dem
    Schnitt um ihn -- was es davon gibt --, und die Zahlen der Legende.
    """
    if b is None:
        return None
    v, pilz = b.vorschlag, b.pilz
    daten: Dict[str, Any] = {
        "name": v.name if v is not None else "",
        "leisten": [], "aussen": [], "abstaende": [], "durchmesser": 0.0,
        "pilz": None,
        "d_v_out": b.d_v_out * mm,
        "u_out": b.u_out * mm,
        "V_Rd_s": b.V_Rd_s / 1e3,
        "V_Rd_max": b.V_Rd_max / 1e3 if math.isfinite(b.V_Rd_max) else None,
        "V_d_out": b.V_d_out / 1e3,
        "V_Rd_c_out": b.V_Rd_c_out / 1e3,
        "reicht": v.reicht if v is not None else True,
    }
    if v is not None:
        daten.update({
            "durchmesser": v.typ.durchmesser * mm,
            "leisten": [{"wurzel": _punkte([l.wurzel])[0], "anker": _punkte(l.anker(v.radien))}
                        for l in v.leisten],
            "aussen": [{"punkte": _punkte(l.punkte), "zaehlt": l.zaehlt}
                       for l in v.aussen.massgebend.linien],
            "abstaende": [x * mm for x in v.abstaende],
        })
    if pilz is not None:
        daten["pilz"] = {
            "name": pilz.pilz.name,
            "umriss": _punkte(pilz.umriss),
            "stege": [_punkte(steg) for steg in pilz.pilz.stege()],
            "schnitt": [{"punkte": _punkte(l.punkte), "zaehlt": l.zaehlt}
                        for l in pilz.schnitt.massgebend.linien],
            "d_v": pilz.d_v * mm,
        }
    return daten
