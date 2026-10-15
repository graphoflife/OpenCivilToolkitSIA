"""
opencivil/konsole/sitzung.py -- eine Python-Sitzung für die App «Python».

VERANTWORTUNG:
Führt aus, was der Benutzer schreibt -- ein Skript oder eine Zeile der
Konsole -- in einem Namensraum, der zwischen den Läufen bleibt: was Skript A
anlegt, sieht Skript B (Benutzer, 2026-10-15). Was dabei herauskommt, steht
der Reihe nach als Ereignis da -- Ausgabe, Fehlerausgabe, der Wert der
letzten Zeile, ein Fehler, ein Bild aus :mod:`opencivil.konsole.zeichnen` --,
und dazu die Variablen für den Beobachter rechts.

WO SIE LÄUFT:
Im Browser, in einem eigenen Faden mit Pyodide (``web/js/konsole.js``), nie
auf dem Rechner: über den lokalen Server könnte sonst jede Webseite Code auf
ihm ausführen. Getestet wird sie unter CPython; nur das Nachladen der Pakete
(:mod:`opencivil.konsole.pakete`) gibt es dort nicht.

REINES PYTHON:
Im Namensraum liegt nichts vom Projekt (Benutzer, 2026-10-15). Wer will,
schreibt ``import opencivil`` -- der Rechenkern liegt im Faden bei.
"""

from __future__ import annotations

import ast
import builtins
import contextlib
import inspect
import linecache
import sys
import traceback
import types
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from opencivil.konsole import pakete, zeichnen

#: Wo die Konsole selbst liegt -- ihre Rahmen gehören in keine Fehlermeldung.
EIGENE = str(Path(__file__).resolve().parent)

#: Wie lang ein Wert in der Zeile des Beobachters wird -- und beim Darüberfahren.
KURZ = 120
LANG = 4000

#: Unter diesem Namen holt sich ein Skript das Zeichenmodul: ``import zeichnen as plt``.
ZEICHENMODUL = "zeichnen"


@dataclass
class Lauf:
    """Was ein Lauf ergab: die Ereignisse der Reihe nach, und ob er ohne Fehler durchkam."""

    ereignisse: List[Dict[str, Any]] = field(default_factory=list)
    fehlerfrei: bool = True

    def schreiben(self, art: str, text: str) -> None:
        """Text an die Ereignisse -- an das letzte gleicher Art, wenn es direkt davor steht."""
        if not text:
            return
        if self.ereignisse and self.ereignisse[-1]["art"] == art:
            self.ereignisse[-1]["text"] += text
        else:
            self.ereignisse.append({"art": art, "text": text})


class _Strom:
    """Was ``print`` erreicht: schreibt in den Lauf, unter seiner Art."""

    def __init__(self, lauf: Lauf, art: str) -> None:
        self.lauf, self.art = lauf, art

    def write(self, text: str) -> int:
        self.lauf.schreiben(self.art, text)
        return len(text)

    def flush(self) -> None:
        pass


def _keine_eingabe(*_args: Any) -> str:
    raise RuntimeError("input() geht hier nicht: es gibt keine Tastatur, die wartet. "
                       "Werte bitte im Skript setzen.")


class Sitzung:
    """Ein Namensraum und das Ausführen darin -- eine Konsole, ein Gedächtnis."""

    def __init__(self) -> None:
        self.namensraum: Dict[str, Any] = {}
        self.zuruecksetzen()

    def zuruecksetzen(self) -> None:
        """Ein leerer Namensraum -- alle Variablen weg, wie nach einem Neustart."""
        self.namensraum.clear()
        self.namensraum.update({"__name__": "__main__", "__builtins__": builtins,
                                "input": _keine_eingabe})
        zeichnen.clf()
        sys.modules.setdefault(ZEICHENMODUL, zeichnen)

    def ausfuehren(self, code: str, *, name: str = "Konsole", eingabe: bool = False) -> Lauf:
        """
        Führt ``code`` aus. ``name`` steht in einer Fehlermeldung als Datei:
        der Name des Skripts. Mit ``eingabe`` -- einer Zeile der Konsole --
        steht der Wert der letzten Zeile da, wenn sie ein Ausdruck ist, wie
        in der Python-Konsole: ``1 + 1`` zeigt ``2``.
        """
        lauf = Lauf()
        # Damit eine Fehlermeldung die Zeile zeigen kann, muss der Quelltext
        # dort liegen, wo traceback ihn sucht.
        linecache.cache[name] = (len(code), None, code.splitlines(True), name)
        zeichnen._ziel = lambda bild: lauf.ereignisse.append({"art": "bild", "bild": bild})
        try:
            with contextlib.redirect_stdout(_Strom(lauf, "ausgabe")), \
                    contextlib.redirect_stderr(_Strom(lauf, "fehlerausgabe")):
                self._ausfuehren(code, name, eingabe, lauf)
                # Was am Ende noch offen ist, kommt von selbst -- wie im Notizbuch.
                zeichnen.show()
        except BaseException as fehler:  # noqa: BLE001 -- der Benutzer darf alles werfen
            lauf.fehlerfrei = False
            zeichnen.clf()
            lauf.ereignisse.append({"art": "fehler", "text": _fehlertext(fehler, name)})
        finally:
            zeichnen._ziel = None
        return lauf

    def _ausfuehren(self, code: str, name: str, eingabe: bool, lauf: Lauf) -> None:
        baum = ast.parse(code, filename=name)
        letzte = None
        if eingabe and baum.body and isinstance(baum.body[-1], ast.Expr):
            letzte = ast.Expression(baum.body.pop().value)
        exec(compile(baum, name, "exec"), self.namensraum)  # noqa: S102 -- dafür ist sie da
        if letzte is not None:
            wert = eval(compile(letzte, name, "eval"), self.namensraum)  # noqa: S307
            if wert is not None:
                self.namensraum["_"] = wert
                lauf.ereignisse.append({"art": "wert", "text": _darstellung(wert, LANG)})

    # -- Der Beobachter -----------------------------------------------------

    def variablen(self) -> List[Dict[str, str]]:
        """
        Die Variablen des Namensraums, nach Namen: was der Benutzer angelegt
        hat. Weggelassen werden Namen mit Unterstrich, Module, Funktionen und
        Klassen -- wie im Variablen-Explorer von Spyder.
        """
        heraus = []
        for name in sorted(self.namensraum, key=str.lower):
            wert = self.namensraum[name]
            if name.startswith("_") or name == "input" and wert is _keine_eingabe:
                continue
            if isinstance(wert, types.ModuleType) or inspect.isroutine(wert) \
                    or inspect.isclass(wert):
                continue
            heraus.append({"name": name, "typ": _typ(wert), "groesse": _groesse(wert),
                           "wert": _darstellung(wert, KURZ, einzeilig=True),
                           "lang": _darstellung(wert, LANG)})
        return heraus


# ===========================================================================
# Darstellung
# ===========================================================================


def _typ(wert: Any) -> str:
    """Der Typ, wie man ihn sucht: ``int``, ``ndarray float64``, ``DataFrame``."""
    typ = type(wert).__name__
    dtype = getattr(wert, "dtype", None)
    if dtype is not None and hasattr(wert, "shape") and typ == "ndarray":
        return f"{typ} {dtype}"
    return typ


def _groesse(wert: Any) -> str:
    """Wie gross: Form eines Feldes oder einer Tabelle, sonst die Länge -- leer bei Zahlen."""
    form = getattr(wert, "shape", None)
    if isinstance(form, tuple) and form:
        return "×".join(str(n) for n in form)
    if isinstance(wert, (str, bytes, list, tuple, dict, set, frozenset, range)):
        return str(len(wert))
    return ""


def _darstellung(wert: Any, laenge: int, *, einzeilig: bool = False) -> str:
    """``repr`` -- gekürzt, und für die Zeile des Beobachters in eine Zeile gelegt."""
    try:
        text = repr(wert)
    except Exception as fehler:  # noqa: BLE001 -- ein kaputtes repr darf nichts anhalten
        text = f"<Darstellung fehlgeschlagen: {type(fehler).__name__}: {fehler}>"
    if einzeilig:
        text = " ".join(text.split())
    return text if len(text) <= laenge else text[:laenge - 1] + "…"


def _fehlertext(fehler: BaseException, name: str) -> str:
    """
    Die Fehlermeldung, wie Python sie schreibt -- ohne die Rahmen der Konsole
    selbst: wer sein Skript liest, sucht seine Zeile, nicht unsere. Fehlt ein
    Modul, steht dazu, was beiliegt.
    """
    if isinstance(fehler, SyntaxError):
        text = "".join(traceback.format_exception_only(type(fehler), fehler))
    else:
        bericht = traceback.TracebackException.from_exception(fehler)
        bericht.stack = traceback.StackSummary.from_list(
            [r for r in bericht.stack if not str(Path(r.filename).resolve()).startswith(EIGENE)
             or r.filename == name])
        text = "".join(bericht.format())
    if isinstance(fehler, ModuleNotFoundError) and fehler.name:
        text += pakete.hinweis(fehler.name.split(".")[0]) + "\n"
    return text
