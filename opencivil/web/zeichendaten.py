"""
opencivil/web/zeichendaten.py -- was die Oberflaeche je Bauteil zeichnet, nach seiner Art.

VERANTWORTUNG:
Je Bauteilart (:data:`~opencivil.projekt.aufbau.BAUTEILE`) die Funktion,
die aus Aufbau und Loesung die Zeichendaten eines Eintrags macht -- oder
keine, wo die Bilder anders kommen: bei der Platte aus den Linien und
Kurven der Antwort und aus eigenen Anfragen, ebenso bei der
Querschnittsanalyse -- sie bekommt hier nur, was sie aus einem
Balkensystem nimmt. Die
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
    ANALYSE, BALKENSYSTEM, BALKENSYSTEM3D, BAUTEILE, DECKE, DURCHSTANZEN, ERDBEBEN, FACHWERKMODELL,
    GRUNDBRUCH, MAUERWERK, PFAHL, PLATTE, SETZUNG,
)
from opencivil.web import (
    balkendaten, deckendaten, durchstanzdaten, erdbebendaten, fachwerkdaten, grundbruchdaten,
    mauerwerkdaten, pfahldaten, setzungsdaten,
)


def _balkensystem(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]:
    """
    Eben wie im Raum: die knappe Uebersicht, je Querschnitt sein Umriss und
    die Achse, um die sich sein Profil biegt, und je Linie ihre Achsen, die
    die Oberflaeche nicht selbst legt -- auch wenn das System nicht rechnet.
    """
    teil = aufbau.teile[kennung]
    system = teil.objekt
    return {"uebersicht": balkendaten.uebersicht(loesung.befunde.get(system.rechnung.id)),
            "umrisse": balkendaten.umrisse(system, loesung),
            "biegeachsen": balkendaten.biegeachsen(teil.eintrag),
            "achsen": balkendaten.stabachsen(system)}


def _analyse(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]:
    """
    Was die Kachel «Aus dem Balkensystem» vom Kern braucht -- ``None`` ohne
    System: welches gerechnet ist (die Oberflaeche zeigt es nur, solange es
    das gewaehlte ist), welche Staebe sich waehlen lassen und welche zaehlen,
    die Saetze, die grau dastehen, und je Stelle ihr Name, wofuer sie
    massgebend ist und ihre Werte als Lastfall, in kN und kNm
    (:mod:`~opencivil.projekt.aufbau.aus_system`). Ihre Bilder holt die
    Analyse anders.
    """
    teil = aufbau.teile[kennung]
    aus = teil.aus_system
    if aus is None:
        return {"aus_system": None}
    felder = ("N_Ed", "V_y_Ed", "V_z_Ed", "T_Ed", "M_y_Ed", "M_z_Ed")
    return {"aus_system": {
        "system": teil.eintrag.aus_system.system, "name": aus.system,
        "kandidaten": [{"kennung": k, "querschnitt": q} for k, q in aus.kandidaten],
        "staebe": aus.staebe, "hinweise": aus.hinweise,
        "stellen": [{"name": l.name, "gruende": ", ".join(s.gruende),
                     **{f: getattr(l, f) for f in felder}}
                    for (_, s), l in zip(aus.stellen, aus.lastfaelle)],
    }}


#: Je Bauteilart, nach ihrem Namen, was die Oberflaeche von einem Eintrag
#: zeichnet -- ``None``: ihre Bilder kommen anders.
ZEICHENDATEN: Dict[str, Optional[Callable[[Aufbau, str, Loesung], Any]]] = {
    PLATTE.name: None,
    ANALYSE.name: _analyse,
    BALKENSYSTEM.name: _balkensystem,
    BALKENSYSTEM3D.name: _balkensystem,
    DECKE.name: deckendaten.zeichnung,
    DURCHSTANZEN.name: durchstanzdaten.situation,
    FACHWERKMODELL.name: fachwerkdaten.zeichnung,
    MAUERWERK.name: mauerwerkdaten.zeichnung,
    GRUNDBRUCH.name: grundbruchdaten.situation,
    SETZUNG.name: setzungsdaten.situation,
    PFAHL.name: pfahldaten.situation,
    ERDBEBEN.name: erdbebendaten.ansicht,
}

_ohne = {a.name for a in BAUTEILE} - set(ZEICHENDATEN)
if _ohne:
    raise RuntimeError(f"zeichendaten.py: fuer {', '.join(sorted(_ohne))} steht nicht, was "
                       f"gezeichnet wird – auch keine ist eine Angabe (None).")


def zeichendaten(aufbau: Aufbau, loesung: Loesung) -> Dict[str, Any]:
    """Je Bauteil, nach Kennung, seine Zeichendaten -- nur fuer die Arten, die welche haben."""
    return {kennung: machen(aufbau, kennung, loesung)
            for kennung, teil in aufbau.teile.items()
            if (machen := ZEICHENDATEN[teil.art.name]) is not None}
