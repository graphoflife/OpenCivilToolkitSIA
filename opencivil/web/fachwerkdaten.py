"""
opencivil/web/fachwerkdaten.py -- was die Oberflaeche von einem Fachwerkmodell zeichnet.

VERANTWORTUNG:
Aus dem Befund eines Fachwerkmodells die Daten seiner Zeichnung: seine
Meldungen und ob es bereit ist, ein Fachwerk zu suchen -- keine Meldung
haelt es auf (:func:`uebersicht`). Dazu der Teil des Katalogs, den nur das
Fachwerkmodell braucht (:func:`katalog`): die Vorsilben seiner Teile und
die Stellungen eines Lagers. Scheiben, Lager und Lasten zeichnet die
Oberflaeche nach dem Projekt.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from opencivil.core.rechenwerk import Loesung
from opencivil.fachwerkmodell.modell import Halt
from opencivil.fachwerkmodell.werk import Fachwerkbefund
from opencivil.projekt import Aufbau
from opencivil.projekt.fachwerkmodell import VORSILBEN


def zeichnung(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]:
    """Was die Zeichnung eines Fachwerkmodells unter seine Teile legt -- auch wenn es nicht rechnet."""
    return uebersicht(loesung.befunde.get(aufbau.fachwerkmodelle[kennung].rechnung.id))


def uebersicht(befund: Optional[Fachwerkbefund]) -> Dict[str, Any]:
    """``bereit`` und ``meldungen`` (``{text, elemente, fehler, unfertig}``) -- ohne Befund leer."""
    if befund is None:
        return {"bereit": False, "meldungen": []}
    return {"bereit": not befund.haelt_an, "meldungen": [m.als_dict() for m in befund.meldungen]}


def katalog() -> Dict[str, Any]:
    """Womit die Kennungen der Teile beginnen, je Liste, und wie ein Lager halten kann."""
    return {"vorsilben": dict(VORSILBEN),
            "halt": [{"wert": h.value, "beschriftung": h.beschriftung, "titel": h.erklaerung}
                     for h in Halt]}
