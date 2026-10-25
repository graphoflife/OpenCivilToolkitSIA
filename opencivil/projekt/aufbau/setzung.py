"""
opencivil/projekt/aufbau/setzung.py -- eine Setzungsberechnung wird Rechnung.

VERANTWORTUNG:
Aus einem :class:`~opencivil.projekt.setzung.SetzungEintrag` das Fundament
und sein Nachweis, die Setzung (:func:`bauen`).
"""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from opencivil.geotechnik.setzung import Schicht, Setzung, Setzungsfundament
from opencivil.projekt.lesen import als_groesse
from opencivil.projekt.setzung import SetzungEintrag

from opencivil.projekt.aufbau.kern import Aufbau, Bauteil

if TYPE_CHECKING:
    from opencivil.projekt.aufbau import Bauteilart


def bauen(art: "Bauteilart", eintrag: SetzungEintrag, aufbau: Aufbau) -> Bauteil:
    """
    Ein Fundament und seine Setzung, sobald es eine Schicht gibt. Ohne sie
    steht das Fundament allein da, wie ein Grundbruch ohne Kombination.
    Jede Zahl in der Einheit ihres Feldes
    (:func:`~opencivil.projekt.lesen.als_groesse`).
    """
    g = partial(als_groesse, eintrag)
    fundament = Setzungsfundament(
        name=eintrag.name, B=g("B"), L=g("L"), q_W=g("q_W"), q_E=g("q_E"),
        s_zul=g("s_zul"), dz=g("dz"), steifigkeit=eintrag.steifigkeit,
        schichten=[Schicht(name=s.name, d=als_groesse(s, "d"), M_E=als_groesse(s, "M_E"),
                           M_E_strich=als_groesse(s, "M_E_strich"))
                   for s in eintrag.schichten],
        praefix=f"{art.raum}.{eintrag.kennung}")
    fundament.ins_rechenwerk(aufbau.werk)
    teil = Bauteil(eintrag.kennung, eintrag.name, art, fundament)
    if eintrag.schichten:
        aufbau.eintragen(teil, "setzung", eintrag.kennung, Setzung(fundament))
    else:
        aufbau.warnungen.append(f"Setzung '{eintrag.name}': keine Schicht → kein Nachweis.")
    return teil
