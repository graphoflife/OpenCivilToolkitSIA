"""
opencivil/mcp/zeiger.py -- einzelne Felder eines Eintrags aendern, ueber Pfade.

Ein Pfad zeigt in einen Eintrag, wie er in der Datei steht und wie
``eintrag_lesen`` ihn zeigt: ``/lastfaelle/0/M_Ed`` ist ``M_Ed`` im ersten
Lastfall, nach RFC 6901 -- ``~1`` steht fuer «/» in einem Namen, ``~0`` fuer
«~». ``-`` am Ende einer Liste haengt an; der leere Pfad meint den ganzen
Eintrag. Ob das Geaenderte gilt, entscheidet danach der Leser des Kerns
(:mod:`opencivil.projekt.lesen`): ein Feld, das es nicht gibt, meldet er mit
dem aehnlichsten, das es gibt.
"""

from __future__ import annotations

import copy
import json
from typing import Any, Iterable, List, Mapping

from opencivil.mcp.sitzung import Werkzeugfehler
from opencivil.projekt.lesen import unbekanntes_feld


def anwenden(roh: Any, aenderungen: Iterable[Mapping[str, Any]]) -> Any:
    """
    Die ``aenderungen`` an ``roh``, der Reihe nach: je eine mit ``pfad`` und
    ``wert`` -- setzen, bei ``-`` anhaengen -- oder mit ``pfad`` und
    ``entfernen`` -- aus einer Liste nehmen, ein Feld auf seine Vorgabe
    zuruecksetzen. Gibt das Ganze zurueck.
    """
    for aenderung in aenderungen:
        roh = _eine(roh, aenderung)
    return roh


def _eine(roh: Any, aenderung: Mapping[str, Any]) -> Any:
    pfad = aenderung["pfad"]
    entfernen = bool(aenderung.get("entfernen"))
    if entfernen == ("wert" in aenderung):
        raise Werkzeugfehler(f"Pfad '{pfad}': je Änderung entweder «wert» oder «entfernen: true».")
    wert = copy.deepcopy(aenderung.get("wert"))
    *weg, letzter = _teile(pfad) or [None]
    if letzter is None:
        if entfernen:
            raise Werkzeugfehler("Den ganzen Eintrag löscht eintrag_loeschen.")
        return wert
    ziel = roh
    for teil in weg:
        ziel = _hinein(ziel, teil, pfad)
    if isinstance(ziel, list):
        if letzter == "-" and not entfernen:
            ziel.append(wert)
        elif entfernen:
            del ziel[_stelle(ziel, letzter, pfad)]
        else:
            ziel[_stelle(ziel, letzter, pfad)] = wert
    elif isinstance(ziel, dict):
        if not entfernen:
            ziel[letzter] = wert      # ein Feld, das es nicht gibt, meldet der Leser
        elif letzter in ziel:
            del ziel[letzter]
        else:
            raise unbekanntes_feld(f"Pfad '{pfad}'", letzter, ziel)
    else:
        raise _einzeln(pfad, letzter, ziel)
    return roh


def _teile(pfad: str) -> List[str]:
    """Die Namen eines Pfads, RFC 6901 -- keiner beim leeren."""
    if not pfad:
        return []
    if not pfad.startswith("/"):
        raise Werkzeugfehler(f"Ein Pfad beginnt mit «/»: '/{pfad}' statt '{pfad}'.")
    return [teil.replace("~1", "/").replace("~0", "~") for teil in pfad[1:].split("/")]


def _hinein(ziel: Any, teil: str, pfad: str) -> Any:
    """Einen Schritt tiefer -- in ein Feld oder an eine Stelle einer Liste."""
    if isinstance(ziel, list):
        return ziel[_stelle(ziel, teil, pfad)]
    if isinstance(ziel, dict):
        if teil not in ziel:
            raise unbekanntes_feld(f"Pfad '{pfad}'", teil, ziel)
        return ziel[teil]
    raise _einzeln(pfad, teil, ziel)


def _stelle(liste: List[Any], teil: str, pfad: str) -> int:
    """Die Stelle in einer Liste, ab 0 gezaehlt -- eine, die es gibt."""
    if not (teil.isascii() and teil.isdigit()):
        raise Werkzeugfehler(f"Pfad '{pfad}': in einer Liste zählt eine Nummer ab 0, nicht "
                             f"«{teil}»" + (" – «-» hängt nur an." if teil == "-" else "."))
    i = int(teil)
    if i >= len(liste):
        raise Werkzeugfehler(f"Pfad '{pfad}': die Liste ist leer." if not liste else
                             f"Pfad '{pfad}': die Liste hat {len(liste)} Einträge, 0 bis "
                             f"{len(liste) - 1}.")
    return i


def _einzeln(pfad: str, teil: str, wert: Any) -> Werkzeugfehler:
    return Werkzeugfehler(f"Pfad '{pfad}': vor «{teil}» steht ein einzelner Wert "
                          f"({json.dumps(wert, ensure_ascii=False)[:40]}), kein Objekt und "
                          f"keine Liste.")
