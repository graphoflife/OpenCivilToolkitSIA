"""
opencivil/konsole/pakete.py -- welche Fremdpakete ein Skript einbinden kann.

VERANTWORTUNG:
Mitgeliefert ist, was unter ``web/vendor/pyodide/`` liegt: numpy und pandas
samt dem, was pandas braucht (Benutzer, 2026-10-15; geholt mit
``werkzeug/pyodide_holen.py``). Welche das sind, schreibt die Brücke aus den
Dateien, die dort liegen, nach ``web/kern/dateien.json`` (Eintrag
``pakete``: Importname -> Paketname). Hier wird nur gelesen -- eine zweite
Liste gäbe es nicht, die veralten könnte.

WANN GELADEN WIRD:
Erst wenn ein Skript ein Paket mit ``import`` einbindet: numpy kostet 2.9 MB,
und wer nur rechnet, soll sie nicht laden. Was ein Code einbindet, liest
:func:`gebraucht` aus seinem Syntaxbaum; geladen wird im Faden von Pyodide
(:func:`laden`). Unter CPython gibt es dort nichts zu laden.
"""

from __future__ import annotations

import ast
import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, List

#: Das Verzeichnis des Kerns -- im Faden liegt es an derselben Stelle neben
#: ``opencivil/`` wie im Repo (``web/js/kern_arbeiter.js``).
VERZEICHNIS = Path(__file__).resolve().parents[2] / "web" / "kern" / "dateien.json"


@lru_cache(maxsize=1)
def mitgeliefert() -> Dict[str, str]:
    """Importname -> Paketname, für jedes Paket, das beiliegt."""
    try:
        return dict(json.loads(VERZEICHNIS.read_text(encoding="utf-8"))["pakete"])
    except (OSError, KeyError, ValueError):
        return {}


def importe(code: str) -> List[str]:
    """Die Module, die ``code`` einbindet -- nur der erste Teil des Namens: ``numpy`` für ``numpy.linalg``."""
    try:
        baum = ast.parse(code)
    except SyntaxError:
        return []
    namen = []
    for knoten in ast.walk(baum):
        if isinstance(knoten, ast.Import):
            namen += [a.name.split(".")[0] for a in knoten.names]
        elif isinstance(knoten, ast.ImportFrom) and knoten.module and not knoten.level:
            namen.append(knoten.module.split(".")[0])
    return list(dict.fromkeys(namen))


def gebraucht(code: str) -> List[str]:
    """Die beiliegenden Pakete, die ``code`` einbindet -- ihre Abhängigkeiten lädt Pyodide selbst."""
    pakete = mitgeliefert()
    return list(dict.fromkeys(pakete[n] for n in importe(code) if n in pakete))


async def laden(code: str) -> None:
    """Lädt im Faden von Pyodide, was ``code`` braucht; unter CPython nichts."""
    namen = gebraucht(code)
    if not namen:
        return
    try:
        import pyodide_js  # type: ignore[import-not-found] -- gibt es nur in Pyodide
        from pyodide.ffi import to_js  # type: ignore[import-not-found]
    except ImportError:
        return
    await pyodide_js.loadPackage(to_js(namen))


def hinweis(name: str) -> str:
    """Was zu einem Modul gesagt wird, das sich nicht einbinden liess."""
    pakete = mitgeliefert()
    if name in pakete:
        return (f"{name} liegt bei, wird aber nur geladen, wenn ein Skript es mit "
                f"«import {name}» einbindet.")
    beiliegend = ", ".join(sorted(pakete)) or "keine"
    return (f"{name} liegt hier nicht bei. Fremdpakete gibt es nur diese: {beiliegend}; "
            f"dazu die Standardbibliothek, opencivil und «import zeichnen» für Diagramme.")
