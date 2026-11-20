"""
opencivil/web/uebersetzt.py -- das Uebersetzte fuer den naechsten Start.

WOZU:
Beim Einbinden uebersetzt Python jede Quelldatei in Bytecode, und in Pyodide
ist das rund die Haelfte des Einlesens. Von sich aus haelt Pyodide das
Uebersetzte nicht fest (``sys.dont_write_bytecode``). Der Faden der Seite
(``web/js/kern_arbeiter.js``) laesst Python die ``.pyc``-Dateien schreiben,
packt sie einige Sekunden nach dem Start mit :func:`packen` in ein Stueck und
legt es in einen Speicher des Browsers. Beim naechsten Besuch setzt
:func:`einsetzen` sie vor dem Einbinden wieder an ihren Ort, und Python
uebersetzt nur noch, was fehlt.

Mitliefern ginge nicht: Bytecode gilt nur fuer seine Fassung von Python, und
die im Browser ist eine andere als die auf dem Rechner. So uebersetzt
Pyodide selbst, einmal je Stand der Quellen.

AM INHALT GEPRUEFT:
Ob ein ``.pyc`` noch zu seiner Quelle passt, prueft Python sonst an deren
Zeit und Groesse. Die Zeit hilft hier nicht -- jeder Start legt die Quellen
neu an --, und auf die Groesse allein ist kein Verlass: eine geaenderte
Ziffer laesst sie gleich, und still liefe der alte Code. Darum legt
:func:`packen` jedes ``.pyc`` als eines ab, das Python am Inhalt der Quelle
prueft (hash-basiert, PEP 552): beim Einbinden vergleicht es diesen mit dem,
aus dem uebersetzt wurde, und uebersetzt neu, wenn er abweicht. Ins Stueck
kommt nur, was zu den Quellen von jetzt passt.
"""

from __future__ import annotations

import importlib.util
import marshal
import os
from pathlib import Path
from typing import Dict, Optional

#: Kennzeichen im Kopf eines ``.pyc``: hash-basiert (Bit 0) und an der Quelle
#: geprueft (Bit 1), PEP 552.
AM_INHALT = 0b11


def einsetzen(stueck: str | os.PathLike, wurzel: str | os.PathLike) -> int:
    """
    Setzt die ``.pyc``-Dateien aus ``stueck`` an ihren Ort unter ``wurzel``
    und gibt zurueck, wie viele es waren.

    Ob eines gilt, prueft Python beim Einbinden selbst, am Inhalt seiner
    Quelle; ein veraltetes uebersetzt es neu.
    """
    with open(stueck, "rb") as datei:
        dateien: Dict[str, bytes] = marshal.load(datei)
    for name, inhalt in dateien.items():
        ziel = Path(wurzel, name)
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_bytes(inhalt)
    return len(dateien)


def packen(stueck: str | os.PathLike, wurzel: str | os.PathLike) -> bool:
    """
    Schreibt jedes ``.pyc`` unter ``wurzel``, das zu seiner Quelle passt, in
    ein Stueck nach ``stueck`` -- jedes am Inhalt der Quelle geprueft.

    Gibt zurueck, ob das Stueck neu ist. Liegt dort schon dasselbe, etwa weil
    es so eingesetzt wurde und nichts neu zu uebersetzen war, bleibt es
    liegen: dann gibt es nichts abzulegen.
    """
    wurzel = Path(wurzel)
    dateien = {}
    for pyc in sorted(wurzel.rglob("*.pyc")):
        geprueft = _am_inhalt_geprueft(pyc)
        if geprueft is not None:
            dateien[pyc.relative_to(wurzel).as_posix()] = geprueft
    try:
        with open(stueck, "rb") as datei:
            if marshal.load(datei) == dateien:
                return False
    except (OSError, EOFError, ValueError, TypeError):
        pass   # noch keines da, oder ein unlesbares: neu schreiben
    with open(stueck, "wb") as datei:
        marshal.dump(dateien, datei)
    return True


def _am_inhalt_geprueft(pyc: Path) -> Optional[bytes]:
    """
    Das ``.pyc`` mit einem Kopf, der Python am Inhalt der Quelle pruefen
    laesst -- oder ``None``, wenn es nicht zu ihr passt, sie fehlt oder es
    fuer eine andere Fassung von Python uebersetzt ist.
    """
    daten = pyc.read_bytes()
    if daten[:4] != importlib.util.MAGIC_NUMBER:
        return None
    try:
        quelle = Path(importlib.util.source_from_cache(pyc))
        inhalt = quelle.read_bytes()
    except (ValueError, OSError):
        return None
    marke = importlib.util.source_hash(inhalt)
    if int.from_bytes(daten[4:8], "little") & 0b1:
        passt = daten[8:16] == marke
    else:
        passt = daten[8:16] == _zeit_und_groesse(quelle.stat())
    if not passt:
        return None
    return daten[:4] + AM_INHALT.to_bytes(4, "little") + marke + daten[16:]


def _zeit_und_groesse(stand: os.stat_result) -> bytes:
    """Was ein an der Zeit gepruefter Kopf von der Quelle festhaelt: Sekunde und Groesse, je 4 Byte."""
    return ((int(stand.st_mtime) & 0xFFFFFFFF).to_bytes(4, "little")
            + (stand.st_size & 0xFFFFFFFF).to_bytes(4, "little"))
