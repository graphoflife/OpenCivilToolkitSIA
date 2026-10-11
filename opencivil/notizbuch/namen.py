"""
opencivil/notizbuch/namen.py -- aus einem Namen wird ein Seitenname.

VERANTWORTUNG:
Eine Seite des Notizbuchs heisst wie ihre Datei, und Obsidian verlinkt ueber
den Dateinamen: ``[[Bemessungswert der Betondruckfestigkeit]]``. Was eine
Formel oder ein Thema heisst, muss darum auch als Dateiname taugen -- auf
jedem System und in jedem Link. Die Regel dafuer steht hier und nur hier;
Formelsammlung, Bruecke und api fragen sie ab.

WAS ERSETZT WIRD:
Ein Doppelpunkt wird zum Gedankenstrich (``Probe: Moment`` -> ``Probe –
Moment``), der Schraegstrich zum Divisionsstrich ∕, die uebrigen Zeichen, die
ein System oder ein Link nicht vertraegt, zu einem aehnlichen; ``?``, ``#``
und ``^`` fallen weg. Geschrieben wird in NFC: dieselben Buchstaben, gleich
codiert, wo immer die Datei entstand.

NIE STILL KUERZEN:
Ein zu langer Name ist ein Fehler. Abgeschnitten fielen zwei Namen mit
gleichem Anfang zusammen -- und eine Seite verschwaende hinter der anderen.

Dieses Modul importiert nichts aus ``opencivil``: die api laedt es auch in
Pyodide, wo jedes Modul beim Start mitkommt.
"""

from __future__ import annotations

import re
import unicodedata

#: Was in einem Dateinamen oder einem Link nicht stehen darf, und wofuer es
#: steht. ``:`` hat eine eigene Regel (siehe :func:`seitenname`).
ERSATZ = {
    "/": "∕",
    "\\": "∕",
    "|": "¦",
    "*": "·",
    '"': "'",
    "<": "‹",
    ">": "›",
    "[": "(",
    "]": ")",
}

#: Zeichen, die ersatzlos wegfallen: ``#`` und ``^`` meinen in einem
#: Obsidian-Link Ueberschrift und Absatz.
WEG = "?#^"

#: Laenger wird kein Name -- sonst ist er keiner mehr, sondern ein Satz.
HOECHSTENS = 100


class NamensFehler(ValueError):
    """Aus diesem Text wird kein brauchbarer Seitenname."""


def seitenname(text: str) -> str:
    """
    Der Name, unter dem eine Seite im Notizbuch steht -- zugleich ihr
    Dateiname ohne ``.md``.

    Einmal angewandt, aendert eine zweite Anwendung nichts mehr.
    """
    name = unicodedata.normalize("NFC", text)
    name = re.sub(r"\s+", " ", name).strip()
    name = re.sub(r"\s*:\s*", " – ", name)
    for zeichen, ersatz in ERSATZ.items():
        name = name.replace(zeichen, ersatz)
    name = "".join(z for z in name if z not in WEG)
    name = re.sub(r"\s+", " ", name).strip().lstrip(".").rstrip(". ")
    if not name:
        raise NamensFehler(f"Aus {text!r} wird kein Seitenname.")
    if len(name) > HOECHSTENS:
        raise NamensFehler(
            f"Der Name {name!r} ist {len(name)} Zeichen lang, erlaubt sind "
            f"{HOECHSTENS}. Kuerzer benennen -- abgeschnitten wird nicht.")
    return name


def vergleichsname(name: str) -> str:
    """
    Woran zwei Namen als derselbe gelten: Obsidian und manches Dateisystem
    unterscheiden gross und klein nicht.
    """
    return unicodedata.normalize("NFC", name).casefold()


def sortierschluessel(name: str) -> str:
    """
    Deutsch sortiert, und auf jedem Rechner gleich: ä wie a, ß wie ss --
    ohne die Spracheinstellung des Systems zu fragen.
    """
    zerlegt = unicodedata.normalize("NFD", name.casefold().replace("ß", "ss"))
    return "".join(z for z in zerlegt if not unicodedata.combining(z))
