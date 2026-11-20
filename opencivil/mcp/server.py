"""
opencivil/mcp/server.py -- das Protokoll: JSON-RPC 2.0 ueber stdin und stdout.

VERANTWORTUNG:
Wie eine Anfrage ankommt und ihre Antwort hinausgeht -- eine Nachricht je
Zeile, wie MCP es fuer stdio vorsieht. Der Server kennt ``initialize``,
``ping``, ``tools/list`` und ``tools/call``; eine Mitteilung (ohne ``id``)
beantwortet er nicht. Was ein Werkzeug tut, steht in
:mod:`opencivil.mcp.werkzeuge`.

STDOUT GEHOERT DEM PROTOKOLL:
Waehrend der Server laeuft, schreibt ``print`` nach stderr: eine Zeile, die
ein Baustein des Kerns ausgibt, zerbraeche sonst die naechste Nachricht.
"""

from __future__ import annotations

import json
import sys
import traceback
from typing import IO, Any, Callable, Dict, Optional

from opencivil.mcp.sitzung import Sitzung
from opencivil.mcp.werkzeuge import WERKZEUGE

#: Die Fassungen des Protokolls, die der Server spricht, die neueste zuerst.
FASSUNGEN = ("2025-06-18", "2025-03-26", "2024-11-05")

#: Was ``initialize`` ueber den Server sagt.
SERVER = {"name": "opencivil", "title": "OpenCivilToolkitSIA", "version": "1"}

#: Was eine KI vor dem ersten Werkzeug wissen sollte -- ``instructions`` von ``initialize``.
ANLEITUNG = """\
OpenCivilToolkitSIA rechnet Bauteile nach SIA 262:2025 und SIA 267:2013: Platten, \
Querschnittsanalysen, ebene und räumliche Balkensysteme, Decken, Durchstanzen, Grundbruch, \
Setzung und Pfähle. Jede Rechnung schreibt ihre Herleitung selbst.

Eine Projektdatei ist eine Mappe mit einem oder mehreren Projekten. Ein Projekt hat \
Materialien und je App Einträge, dazu in jeder App eine Sandbox zum Ausprobieren: sie kommt \
nicht in den Bericht, lässt sich nicht löschen, nur zurücksetzen.

Ablauf: datei_oeffnen oder datei_neu → eintraege → felder (Einheit und Grenzen je Feld) → \
eintrag_anlegen, eintrag_aendern → rechnen → datei_speichern. Jede Änderung prüft der Kern \
sofort; was er nicht lesen kann, ändert nichts, und seine Meldung kommt unverändert zurück. \
Python-Skripte der App «Python» führt dieser Zugang nicht aus."""

#: Die Fehler von JSON-RPC 2.0, die der Server meldet.
UNLESBAR, UNGUELTIG, UNBEKANNT, FALSCHE_PARAMETER, INNEN = -32700, -32600, -32601, -32602, -32603


class Protokollfehler(Exception):
    """Ein Fehler von JSON-RPC, mit seinem Code -- anders als der Fehler eines Werkzeugs."""

    def __init__(self, code: int, meldung: str) -> None:
        super().__init__(meldung)
        self.code = code


class Server:
    """Beantwortet die Nachrichten einer Verbindung, mit einer Sitzung fuer alle Werkzeuge."""

    def __init__(self) -> None:
        self.sitzung = Sitzung()
        self.methoden: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {
            "initialize": self._beginnen,
            "ping": lambda _parameter: {},
            "tools/list": lambda _parameter: {"tools": [w.verzeichnis() for w in WERKZEUGE.values()]},
            "tools/call": self._aufrufen,
        }

    def antwort(self, nachricht: Any) -> Optional[Any]:
        """Die Antwort auf eine Nachricht -- auf einen Stapel die Liste der Antworten, auf eine Mitteilung keine."""
        if isinstance(nachricht, list):
            if not nachricht:
                return _fehler(None, UNGUELTIG, "Ein leerer Stapel ist keine Anfrage.")
            antworten = [a for a in map(self._einzeln, nachricht) if a is not None]
            return antworten or None
        return self._einzeln(nachricht)

    def _einzeln(self, nachricht: Any) -> Optional[Dict[str, Any]]:
        if not isinstance(nachricht, dict) or nachricht.get("jsonrpc") != "2.0":
            return _fehler(None, UNGUELTIG, "Eine Nachricht ist ein Objekt mit «jsonrpc»: «2.0».")
        if "method" not in nachricht:
            return None   # eine Antwort des Programms auf der anderen Seite -- der Server fragt nie
        kennung = nachricht.get("id")
        methode = self.methoden.get(nachricht["method"])
        if "id" not in nachricht:
            return None   # eine Mitteilung: notifications/initialized, notifications/cancelled
        try:
            if methode is None:
                raise Protokollfehler(UNBEKANNT, f"Eine Methode «{nachricht['method']}» kennt "
                                                 f"dieser Server nicht.")
            parameter = nachricht.get("params") or {}
            if not isinstance(parameter, dict):
                raise Protokollfehler(FALSCHE_PARAMETER, "«params» ist ein Objekt.")
            return {"jsonrpc": "2.0", "id": kennung, "result": methode(parameter)}
        except Protokollfehler as fehler:
            return _fehler(kennung, fehler.code, str(fehler))
        except Exception as fehler:  # noqa: BLE001 -- eine Anfrage bleibt nie ohne Antwort
            traceback.print_exc()
            return _fehler(kennung, INNEN, f"{type(fehler).__name__}: {fehler}")

    def _beginnen(self, parameter: Dict[str, Any]) -> Dict[str, Any]:
        """``initialize``: die Fassung des Programms, wenn der Server sie spricht, sonst seine neueste."""
        gewuenscht = parameter.get("protocolVersion")
        return {"protocolVersion": gewuenscht if gewuenscht in FASSUNGEN else FASSUNGEN[0],
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": SERVER, "instructions": ANLEITUNG}

    def _aufrufen(self, parameter: Dict[str, Any]) -> Dict[str, Any]:
        werkzeug = WERKZEUGE.get(parameter.get("name"))
        if werkzeug is None:
            raise Protokollfehler(FALSCHE_PARAMETER, f"Ein Werkzeug «{parameter.get('name')}» gibt "
                                                     f"es nicht. Möglich sind: "
                                                     f"{', '.join(WERKZEUGE)}.")
        return werkzeug.aufrufen(self.sitzung, parameter.get("arguments") or {})


def _fehler(kennung: Any, code: int, meldung: str) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": kennung, "error": {"code": code, "message": meldung}}


def bedienen(eingabe: IO[bytes], ausgabe: IO[bytes]) -> None:
    """Liest Nachrichten aus ``eingabe``, Zeile fuer Zeile, und schreibt jede Antwort als eine Zeile nach ``ausgabe``."""
    server = Server()
    for zeile in eingabe:
        if not zeile.strip():
            continue
        try:
            nachricht = json.loads(zeile)
        except ValueError as fehler:      # auch kein UTF-8
            antwort: Any = _fehler(None, UNLESBAR, f"Kein JSON: {fehler}.")
        else:
            antwort = server.antwort(nachricht)
        if antwort is not None:
            ausgabe.write(json.dumps(antwort, ensure_ascii=False).encode("utf-8") + b"\n")
            ausgabe.flush()


def main() -> None:
    """``python3 -m opencivil.mcp``: bedient stdin und stdout, bis stdin endet."""
    ausgabe = sys.stdout.buffer
    sys.stdout = sys.stderr
    try:
        bedienen(sys.stdin.buffer, ausgabe)
    except KeyboardInterrupt:
        pass
