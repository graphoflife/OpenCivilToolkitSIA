"""
opencivil/web/setzungsdaten.py -- was die Oberflaeche von einer Setzung zeichnet.

VERANTWORTUNG:
Je Fundament die Zahlen der Situationszeichnung, in den Einheiten der
Anzeige -- m und mm: wo gerechnet wurde, wie die Zusatzspannung mit der
Tiefe abnimmt, was jede Schicht zur Setzung beitraegt, die Setzung und die
zulaessige. Die Abmessungen selbst liest die Oberflaeche aus dem Eintrag;
was der Kern daraus macht, kommt von hier.

Gerechnet wird hier nichts, was nicht der Kern schon weiss: die Linie des
Einflussfaktors kommt aus :func:`opencivil.geotechnik.setzung.einflusslinie`,
mit denselben L, B und demselben Punkt wie die Tabelle der Teilschichten.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from opencivil.core.rechenwerk import Loesung
from opencivil.geotechnik import setzung
from opencivil.projekt import Aufbau

mm = 1e3


def situationen(aufbau: Aufbau, loesung: Loesung) -> Dict[str, Any]:
    """Je Fundament, nach Kennung, was die Zeichnung vom Kern braucht."""
    return {kennung: situation(aufbau, kennung, loesung) for kennung in aufbau.setzungen}


def situation(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]:
    """
    Was die Zeichnung eines Fundaments braucht. Ohne Schicht gibt es keinen
    Nachweis und keinen Befund -- dann zeichnet sie nur das Fundament.
    """
    fundament = aufbau.setzungen[kennung]
    nachweis = aufbau.feld("setzung").get(kennung)
    befund: Optional[setzung.Setzungsbefund] = (
        loesung.befunde.get(nachweis.id) if nachweis is not None else None)
    if befund is None:
        return {"punkt": fundament.steifigkeit.punkt, "lage": None, "linie": [],
                "schichten": [], "s": None}
    werte = loesung.werte
    L, B = (werte[fundament.id_von(n)].groesse.si for n in ("L", "B"))
    x, y = befund.punkt
    tiefe = befund.schichten[-1].z_u
    urteil = next(u for u in loesung.urteile if u.raum == nachweis.id)
    return {
        "punkt": fundament.steifigkeit.punkt,
        "lage": [x, y],
        "linie": [list(p) for p in setzung.einflusslinie(L, B, x, y, tiefe)],
        "J_fuss": befund.J_fuss,
        "schichten": [{"name": s.name, "z_o": s.z_o, "z_u": s.z_u, "s_W": s.s_W * mm,
                       "s_E": s.s_E * mm, "s": s.s * mm} for s in befund.schichten],
        "s_W": befund.s_W * mm,
        "s_E": befund.s_E * mm,
        "s": befund.s * mm,
        "s_zul": werte[fundament.id_von("s_zul")].groesse.si * mm,
        "erfuellt": urteil.erfuellt,
        "grad": urteil.gradtext(),
    }
