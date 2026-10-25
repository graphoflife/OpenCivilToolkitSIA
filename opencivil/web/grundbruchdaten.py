"""
opencivil/web/grundbruchdaten.py -- was die Oberflaeche von einem Grundbruch zeichnet.

VERANTWORTUNG:
Je Fundament die Zahlen der Situationszeichnung, in den Einheiten der
Anzeige -- m, kN, Grad: wie tief und wie weit der Gleitkoerper reicht, sein
Umriss, die Lage des Grundwassers, wie die Rechnung sie eingeordnet hat, und
je Kombination die Kraefte, die Neigung der Last und die beiden
Erfuellungsgrade. Die Abmessungen selbst liest die Oberflaeche aus dem
Eintrag; was der Kern daraus macht, kommt von hier.

Gerechnet wird hier nichts, was nicht der Kern schon weiss: der Umriss kommt
aus :func:`opencivil.geotechnik.grundbruch.gleitkoerper`, mit denselben
Werten b und phi_eff wie die Formeln fuer L_Gl und H_Gl.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Optional

from opencivil.core.rechenwerk import Loesung
from opencivil.geotechnik import grundbruch
from opencivil.projekt import Aufbau

kN = 1e-3


def situationen(aufbau: Aufbau, loesung: Loesung) -> Dict[str, Any]:
    """Je Fundament, nach Kennung, was die Zeichnung vom Kern braucht."""
    return {kennung: situation(aufbau, kennung, loesung) for kennung in aufbau.grundbrueche}


def situation(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]:
    """
    Was die Zeichnung eines Fundaments braucht. Ohne eingeschaltete
    Kombination gibt es keinen Nachweis und keinen Befund -- dann zeichnet
    sie nur das Fundament, ohne Gleitkörper und ohne Kräfte.
    """
    fundament = aufbau.grundbrueche[kennung]
    nachweis = aufbau.feld("grundbruch").get(kennung)
    gleiten = aufbau.feld("gleiten").get(kennung)
    befund: Optional[grundbruch.Grundbruchbefund] = (
        loesung.befunde.get(nachweis.id) if nachweis is not None else None)
    drainiert = befund is not None and not befund.undrainiert

    def grad_gleiten(name: str) -> Optional[float]:
        wert = (loesung.werte.get(gleiten.d_ausnutzung[name].id)
                if gleiten is not None and name in gleiten.d_ausnutzung else None)
        return wert.groesse.si if wert is not None else None

    faelle = [{
        "name": r.kombination.name,
        "N_Ed": r.kombination.N_Ed.si * kN,
        "T_Ed": r.kombination.T_Ed.si * kN,
        "delta_R": math.degrees(r.delta_R),
        "grad_grundbruch": r.erfuellungsgrad,
        "grad_gleiten": grad_gleiten(r.kombination.name),
    } for r in (befund.ergebnisse if befund is not None else [])]
    # Die Kombination mit dem kleinsten Erfuellungsgrad, Grundbruch oder Gleiten.
    massgebend = min(faelle, default=None, key=lambda f: min(
        f["grad_grundbruch"], math.inf if f["grad_gleiten"] is None else f["grad_gleiten"]))
    # Der Umriss mit denselben b und phi_eff wie L_Gl und H_Gl im Befund.
    umriss = (grundbruch.gleitkoerper(loesung.werte[fundament.id_von("b")].groesse.si,
                                      loesung.werte[fundament.id_von("phi_eff")].groesse.si)
              if drainiert else [])
    return {
        "undrainiert": befund.undrainiert if befund is not None else None,
        "grundwasser": befund.grundwasser if befund is not None else "",
        "L_gl": befund.L_gl if befund is not None else None,
        "H_gl": befund.H_gl if befund is not None else None,
        "umriss": [list(punkt) for punkt in umriss],
        "faelle": faelle,
        "massgebend": massgebend["name"] if massgebend is not None else None,
    }
