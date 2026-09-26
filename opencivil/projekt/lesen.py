"""
opencivil/projekt/lesen.py -- was in einer Projektdatei stehen darf, und wie es gelesen wird.

VERANTWORTUNG:
Die Leser, mit denen die ``aus_dict`` der Eintraege eine Datei aufnehmen:
Zahlen, Pflichtfelder, Schalter, Teilungen, die Rissanforderung -- und die
alten Formate, die es in gespeicherten Dateien noch gibt (vier Lagen statt
beliebig vieler, flache statt verschachtelter Gebrauchslisten, Lastfaelle
in y).

Ein eigenes Modul, weil sie die Lesefunktionen des ganzen Pakets sind:
:mod:`eintraege`, :mod:`platte` und :mod:`aufbau` brauchen sie alle. Mit
Unterstrich waren sie privat und wurden trotzdem von drei Modulen
importiert.
"""

from __future__ import annotations

import dataclasses
from typing import Any, Dict, List, Mapping, Optional

from opencivil.material.beton import BETONSORTEN
from opencivil.material.betonstahl import STAHLSORTEN
from opencivil.nachweis.mindestbewehrung import RISSBREITE
from opencivil.querschnitt.platte import Richtung


class ProjektFehler(Exception):
    """Die Projektbeschreibung ist in sich nicht stimmig."""


def zahl(d: Mapping[str, Any], feld: str, vorgabe: float) -> float:
    """
    Eine Zahl aus der Beschreibung. Die Vorgabe gilt nur, wenn nichts dasteht.

    Bewusst **nicht** ``float(d.get(feld) or vorgabe)``: dieser Ausdruck kann
    eine eingegebene Null nicht von einem fehlenden Feld unterscheiden und
    ersetzt sie stillschweigend. Im Eingabefeld stand dann ``h = 0``, gerechnet
    wurde mit 300 mm, und die Herleitung schrieb 300 mm hin -- ein Widerspruch,
    den niemand sieht. Eine Platte ohne Dicke meldete «alle Nachweise erfüllt».
    """
    wert = d.get(feld)
    if wert is None or wert == "":
        return vorgabe
    try:
        return float(wert)
    except (TypeError, ValueError):
        raise ProjektFehler(
            f"Das Feld '{feld}' enthält keine Zahl, sondern {wert!r}."
        ) from None


def pflichtfeld(d: Mapping[str, Any], feld: str, wer: str) -> str:
    """
    Ein Feld, ohne das sich nichts zusammenbauen laesst.

    Ohne diese Pruefung kam der nackte ``KeyError`` bis in die Oberflaeche --
    eine Fehlermeldung, die dem Benutzer nichts sagt und nach einem Absturz
    aussieht.
    """
    wert = d.get(feld)
    if wert in (None, ""):
        raise ProjektFehler(f"{wer} hat kein Feld '{feld}'. Die Datei ist unvollständig.")
    return str(wert)


def sorten(art: str) -> Mapping[str, Any]:
    return BETONSORTEN if art == "beton" else STAHLSORTEN


def vorgabe(cls, feld: str) -> Any:
    """
    Die Vorgabe eines Feldes, wie die Datenklasse sie festlegt -- auch fuer
    Felder mit ``default_factory``.

    Die Leser nehmen ihre Vorgaben von der Klasse (``cls.h`` oder hier) und
    schreiben sie nicht noch einmal hin. Stand die Zahl zweimal da -- im Feld
    und im Leser, und ein drittes Mal in der Oberflaeche --, gab es drei
    Vorgaben, die nur so lange uebereinstimmten, wie niemand eine aenderte.
    """
    f = next(f for f in dataclasses.fields(cls) if f.name == feld)
    if f.default is not dataclasses.MISSING:
        return f.default
    if f.default_factory is not dataclasses.MISSING:
        return f.default_factory()
    raise KeyError(f"{cls.__name__}.{feld} hat keine Vorgabe.")


def rissanforderung_aus(wert: Any, vorgabe: str) -> str:
    """
    Die Anforderung an die Rissbildung, oder die Vorgabe.

    Eine unbekannte Angabe wird nicht stillschweigend auf 'normal' gezogen --
    sie waere die mildeste der drei, und eine stillschweigende Milderung ist
    genau das, was ein Nachweiswerkzeug nicht tun darf.
    """
    if wert in (None, ""):
        return vorgabe
    text = str(wert)
    if text not in RISSANFORDERUNGEN:
        raise ProjektFehler(
            f"Unbekannte Rissanforderung '{text}'. Möglich sind: "
            f"{', '.join(RISSANFORDERUNGEN)}.")
    return text


def teilungen_aus(roh, vorgabe) -> List[float]:
    """
    Eine Liste von Teilungen, aufsteigend und ohne Unsinn.

    Ohne brauchbare Angabe die Vorgabe: eine leere Liste hiesse, dass die
    Suche nichts zu versuchen haette, und das ist kein Zustand, in dem man
    eine Oberflaeche stehen lassen will.
    """
    werte = []
    for x in (roh or []):
        try:
            zahl = float(x)
        except (TypeError, ValueError):
            continue
        if zahl > 0:
            werte.append(zahl)
    return sorted(set(werte)) or list(vorgabe)


def schalter_aus(*werte: Any, vorgabe: bool = False) -> bool:
    """
    Ein Schalter aus dem, was in der Datei steht.

    Frueher war jeder dieser Nachweise eine Liste von vier Schaltern, einer je
    Lage, und die Zwaengung hatte je einen fuer x und y. Nachgewiesen wird nur
    noch x, und dort entscheidet die unguenstigere der beiden Lagen -- ein
    Schalter genuegt. Eine alte Datei bringt noch die Liste mit: war darin
    irgendein Haken gesetzt, gilt der Nachweis als eingeschaltet. Das ist die
    Lesart, die nichts wegnimmt, was jemand verlangt hat.

    Mehrere Werte, weil aus `zwaengung_x` und `zwaengung_y` einer wird.
    """
    gefunden = False
    for wert in werte:
        if wert is None:
            continue
        gefunden = True
        if any(wert) if isinstance(wert, (list, tuple)) else bool(wert):
            return True
    return False if gefunden else vorgabe


#: Wahl der Tragrichtung einer Schnittgroessenkombination -- historisch.
#:
#: Schnittgroessen gehoeren jetzt immer zur Tragrichtung x; die Wahl gibt es
#: nicht mehr. Die Konstante steht noch, um alte Dateien zu lesen.
BEIDE_RICHTUNGEN = "beide"


def nur_x(d: Mapping[str, Any], was: str) -> None:
    """
    Alte Lastfaelle, die nur in y galten, gehen nicht mehr.

    Nachgewiesen wird ausschliesslich x. Ein Lastfall mit ``richtung: "y"``
    stillschweigend auf x umzudeuten hiesse, eine Zahl an einem anderen
    Querschnitt anzusetzen als der Benutzer gemeint hat -- genau die Art von
    stiller Aenderung, die ein Nachweiswerkzeug nicht machen darf. ``x`` und
    ``beide`` gelten unveraendert weiter.
    """
    if str(d.get("richtung") or "") == Richtung.Y.value:
        raise ProjektFehler(
            f"{was} gilt nur in y-Richtung. Nachgewiesen wird nur noch x -- "
            f"die y-Lagen stehen im Querschnitt, damit die statische Höhe und "
            f"der Bewehrungsgehalt stimmen, nachgewiesen werden sie nicht. "
            f"Bitte die Richtung auf x stellen oder den Lastfall löschen.")


#: Wie die Rissanforderungen an der Maske heissen.
_BESCHRIFTUNG: Dict[str, str] = {
    "normal": "Normal",
    "erhoeht": "Erhöht",
    "hoch": "Hoch",
}

#: Anforderung an die Rissbildung, mit ihrer Beschriftung. Welche es gibt,
#: sagt :data:`mindestbewehrung.RISSBREITE` -- dort steht zu jeder die
#: Rissbreite, und die Liste der Werte soll nur einmal dastehen. Kaeme dort
#: eine dazu, ohne dass sie hier eine Beschriftung hat, scheiterte schon der
#: Import.
RISSANFORDERUNGEN: Dict[str, str] = {wert: _BESCHRIFTUNG[wert] for wert in RISSBREITE}


def gebrauchsliste_roh(d: Mapping[str, Any], feld: str,
                       alt: str) -> Mapping[str, Any]:
    """
    Die Gebrauchsliste einer Platte aus der Datei -- verschachtelt oder flach.

    Bis zur :class:`Gebrauchsliste` standen die drei Angaben einzeln an der
    Platte: ``haeufige``, ``haeufige_aus_tragsicherheit``, ``haeufige_anteil``
    und dasselbe fuer ``quasistaendige``. Solche Dateien gibt es; sie werden
    hier in die neue Form gebracht, geschrieben wird nur noch diese.
    """
    neu = d.get(feld)
    if isinstance(neu, Mapping):
        return neu
    return {"faelle": d.get(alt) or [],
            "aus_tragsicherheit": d.get(f"{alt}_aus_tragsicherheit", False),
            "anteil": d.get(f"{alt}_anteil")}


def lagen_aus_altem_format(d: Mapping[str, Any]) -> List[dict]:
    """
    Rechnet eine vor dem Vier-Lagen-Modell gespeicherte Platte um.

    Frueher gab es beliebig viele Lagen je Seite, jede mit einem einzigen
    Bewehrungssatz. Uebernommen werden die beiden aeussersten je Seite:

        lagen_unten[0] -> 1. Lage      lagen_oben[0] -> 4. Lage
        lagen_unten[1] -> 2. Lage      lagen_oben[1] -> 3. Lage

    Weitere Lagen der alten Beschreibung gehen dabei verloren -- besser als eine
    gespeicherte Datei gar nicht mehr zu oeffnen, aber der Benutzer sollte sie
    nachsehen.
    """
    def umbauen(alt: Optional[Mapping[str, Any]]) -> dict:
        if not alt:
            return {"stahl": "", "grund": {"durchmesser": 0.0}, "zulage": {"durchmesser": 0.0}}
        return {
            "stahl": alt.get("stahl", ""),
            "grund": {
                "durchmesser": alt.get("durchmesser", 0.0),
                "abstand": alt.get("abstand"),
                "anzahl": alt.get("anzahl"),
            },
            "zulage": {"durchmesser": 0.0},
        }

    unten = list(d.get("lagen_unten") or [])
    oben = list(d.get("lagen_oben") or [])
    return [
        umbauen(unten[0] if len(unten) > 0 else None),   # 1. Lage
        umbauen(unten[1] if len(unten) > 1 else None),   # 2. Lage
        umbauen(oben[1] if len(oben) > 1 else None),     # 3. Lage
        umbauen(oben[0] if len(oben) > 0 else None),     # 4. Lage
    ]
