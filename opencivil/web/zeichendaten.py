"""
opencivil/web/zeichendaten.py -- was die Oberflaeche je Bauteil zeichnet, nach seiner Art.

VERANTWORTUNG:
Je Bauteilart (:data:`~opencivil.projekt.aufbau.BAUTEILE`) die Funktion,
die aus Aufbau und Loesung die Zeichendaten eines Eintrags macht -- oder
keine, wo die Bilder anders kommen: bei Platte und Querschnittsanalyse aus
den Linien und Kurven der Antwort und aus eigenen Anfragen. Die
Schnittstelle legt sie unter einem Schluessel ab, ``zeichendaten[kennung]``
(:func:`zeichendaten`). Fehlt hier eine Art, meldet sich das beim Laden --
nicht erst als leeres Bild. Bis 2026-11-10 stand je Art ein eigener
Schluessel in der Antwort.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from opencivil.core.rechenwerk import Loesung
from opencivil.projekt import Aufbau
from opencivil.projekt.aufbau import (
    ANALYSE, BALKENSYSTEM, BAUTEILE, DECKE, DURCHSTANZEN, GRUNDBRUCH, PLATTE, SETZUNG,
)
from opencivil.web import balkendaten, deckendaten, durchstanzdaten, grundbruchdaten, setzungsdaten


def _balkensystem(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]:
    """Die knappe Uebersicht und je Querschnitt sein Umriss -- auch wenn das System nicht rechnet."""
    system = aufbau.balkensysteme[kennung]
    return {"uebersicht": balkendaten.uebersicht(loesung.befunde.get(system.rechnung.id)),
            "umrisse": balkendaten.umrisse(system, loesung)}


#: Je Bauteilart, nach ihrem Namen, was die Oberflaeche von einem Eintrag
#: zeichnet -- ``None``: ihre Bilder kommen anders.
ZEICHENDATEN: Dict[str, Optional[Callable[[Aufbau, str, Loesung], Any]]] = {
    PLATTE.name: None,
    ANALYSE.name: None,
    BALKENSYSTEM.name: _balkensystem,
    DECKE.name: deckendaten.zeichnung,
    DURCHSTANZEN.name: durchstanzdaten.situation,
    GRUNDBRUCH.name: grundbruchdaten.situation,
    SETZUNG.name: setzungsdaten.situation,
}

_ohne = {a.name for a in BAUTEILE} - set(ZEICHENDATEN)
if _ohne:
    raise RuntimeError(f"zeichendaten.py: fuer {', '.join(sorted(_ohne))} steht nicht, was "
                       f"gezeichnet wird -- auch keine ist eine Angabe (None).")


def zeichendaten(aufbau: Aufbau, loesung: Loesung) -> Dict[str, Any]:
    """Je Bauteil, nach Kennung, seine Zeichendaten -- nur fuer die Arten, die welche haben."""
    return {kennung: machen(aufbau, kennung, loesung)
            for kennung, teil in aufbau.teile.items()
            if (machen := ZEICHENDATEN[teil.art.name]) is not None}
