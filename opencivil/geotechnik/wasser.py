"""
opencivil/geotechnik/wasser.py -- die Raumlast des Grundwassers, aus seiner Flüssigkeit.

VERANTWORTUNG:
Grundbruch und Pfahl rechnen mit γ_w, der Raumlast des Grundwassers. Seit
2026-11-27 ist sie keine Zahl am Bauteil mehr, sondern die Raumlast γ_fl
einer Flüssigkeit des Projekts (:mod:`opencivil.material.fluessigkeit`).
:func:`raumlast` setzt beide gleich, als eigene Zeile der Herleitung -- dort
steht so, welche Flüssigkeit gilt, und wer γ_fl überschreibt, rechnet auch
hier mit seiner Zahl.
"""

from __future__ import annotations

from typing import Tuple

from opencivil.core.berechnung import Formel
from opencivil.core.einheiten import KN_PRO_M3, Groesse
from opencivil.core.protokoll import Abschnitt
from opencivil.core.wert import WertDef
from opencivil.material.basis import Baustoff


def raumlast(praefix: str, abschnitt: Abschnitt, wasser: Baustoff) -> Tuple[WertDef, Formel]:
    """γ_w des Bauteils mit dem Namensraum ``praefix``: die Raumlast der Flüssigkeit ``wasser``."""
    d = WertDef(id=f"{praefix}.gamma_w", symbol=r"\gamma_w", einheit=KN_PRO_M3,
                beschreibung="Raumlast des Grundwassers", stellen=1)
    return d, Formel(
        id=d.id, ausgabe=d, abschnitt=abschnitt,
        eingaben={"gamma_fl": wasser.id_von("gamma_fl")},
        vorlage="@gamma_fl", funktion=_raumlast,
        titel=f"Raumlast des Grundwassers, «{wasser.name}»",
        name="Raumlast des Grundwassers")


def _raumlast(gamma_fl: Groesse) -> Groesse:
    return Groesse.aus_si(gamma_fl.si, KN_PRO_M3)
