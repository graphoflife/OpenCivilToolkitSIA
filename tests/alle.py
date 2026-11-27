"""
tests/alle.py -- alle Tests, verteilt auf die Kerne des Rechners.

    python3 -m tests.alle                      # alle Testdateien
    python3 -m tests.alle test_pfahl test_setzung
    python3 -m tests.alle -j 4                 # mit vier Prozessen

Dasselbe wie ``python3 -m unittest discover -s tests -t .``, nur
gleichzeitig: jede Testdatei läuft in einem eigenen Prozess, die längste
zuerst. Nacheinander brauchten alle Tests am 2026-11-27 rund sechs Minuten
auf einem von acht Kernen; das war dem Benutzer zu lang, und weniger Tests
je Commit wollte er nicht (Benutzer, 2026-11-27).

Wie lange eine Datei zuletzt brauchte, steht in ``tests/.dauern.json``,
nicht im Repo: nur für die Reihenfolge. Fehlt die Datei, beginnt die
grösste Testdatei.

Ausgegeben wird, was unittest zu jeder Datei mit Fehlern schreibt, und am
Schluss dieselben zwei Zeilen wie bei unittest: «Ran … tests in … s» und
«OK» oder «FAILED (failures=…, errors=…)». Mit Fehlern endet das Programm
mit dem Code 1.

Kein fremdes Paket: ``subprocess`` und ein Pool von Fäden, die je auf
einen Prozess warten.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence

WURZEL = Path(__file__).resolve().parent.parent
ORDNER = WURZEL / "tests"
DAUERN = ORDNER / ".dauern.json"

#: Die längste Datei brauchte am 2026-11-27 keine zwei Minuten; eine, die
#: zehn braucht, hängt.
GRENZE_S = 600.0

_GELAUFEN = re.compile(r"^Ran (\d+) tests? in [\d.]+s$", re.M)
_ZAEHLER = re.compile(r"(failures|errors|skipped|expected failures|unexpected successes)=(\d+)")
_URTEIL = re.compile(r"^(?:OK|FAILED)\b.*$", re.M)


@dataclass
class Lauf:
    """Was eine Testdatei ergab."""

    modul: str
    dauer: float
    ausgabe: str
    tests: int
    fehlschlaege: int
    fehler: int

    @property
    def gut(self) -> bool:
        return self.fehlschlaege == 0 and self.fehler == 0


def module(namen: Sequence[str] = ()) -> List[str]:
    """
    Die Testdateien wie ``unittest discover`` sie findet: ``tests/test*.py``.
    Mit Namen nur diese -- «test_pfahl», «tests.test_pfahl» oder
    «tests/test_pfahl.py».
    """
    if not namen:
        return sorted(f"tests.{p.stem}" for p in ORDNER.glob("test*.py"))
    gewaehlt = []
    for name in namen:
        stamm = Path(name).stem if name.endswith(".py") else name.rpartition(".")[2]
        if not (ORDNER / f"{stamm}.py").is_file():
            raise SystemExit(f"Eine Testdatei «{name}» gibt es nicht.")
        gewaehlt.append(f"tests.{stamm}")
    return gewaehlt


def reihenfolge(namen: List[str], dauern: Dict[str, float]) -> List[str]:
    """
    Die längste zuerst. Eine Datei ohne gemessene Dauer kommt vor allen
    anderen -- sie könnte die längste sein --, und unter diesen die grösste.
    """
    def gewicht(modul: str) -> tuple:
        datei = ORDNER / f"{modul.rpartition('.')[2]}.py"
        return (modul not in dauern, dauern.get(modul, 0.0), datei.stat().st_size)
    return sorted(namen, key=gewicht, reverse=True)


def laufen(modul: str) -> Lauf:
    """Eine Testdatei in einem eigenen Prozess, wie unittest sie allein liefe."""
    beginn = time.monotonic()
    try:
        prozess = subprocess.run(
            [sys.executable, "-m", "unittest", modul], cwd=WURZEL,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=GRENZE_S)
        ausgabe = prozess.stdout
    except subprocess.TimeoutExpired:
        ausgabe = f"ERROR: {modul} hielt nach {GRENZE_S:.0f} s nicht an.\n"
        return Lauf(modul, time.monotonic() - beginn, ausgabe, 0, 0, 1)
    dauer = time.monotonic() - beginn
    gelaufen = _GELAUFEN.search(ausgabe)
    urteile = _URTEIL.findall(ausgabe)
    schluss = urteile[-1] if urteile else ""
    zaehler = ({art: int(zahl) for art, zahl in _ZAEHLER.findall(schluss)}
               if schluss.startswith("FAILED") else {})
    fehler = zaehler.get("errors", 0)
    if gelaufen is None or not schluss or (prozess.returncode != 0 and not zaehler):
        # Die Datei lief nicht zu Ende: ein Fehler beim Import, ein Absturz.
        fehler = max(fehler, 1)
    return Lauf(modul, dauer, ausgabe, int(gelaufen.group(1)) if gelaufen else 0,
                zaehler.get("failures", 0), fehler)


def dauern_lesen() -> Dict[str, float]:
    try:
        return {k: float(v) for k, v in json.loads(DAUERN.read_text(encoding="utf-8")).items()}
    except (OSError, ValueError, AttributeError):
        return {}


def dauern_schreiben(dauern: Dict[str, float], laeufe: List[Lauf]) -> None:
    dauern.update({l.modul: round(l.dauer, 2) for l in laeufe})
    try:
        DAUERN.write_text(json.dumps(dauern, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    except OSError:
        pass


def main(argv: Sequence[str] = ()) -> int:
    leser = argparse.ArgumentParser(prog="python3 -m tests.alle",
                                    description="Alle Tests, verteilt auf die Kerne.")
    leser.add_argument("module", nargs="*", help="nur diese Testdateien")
    leser.add_argument("-j", type=int, default=os.cpu_count() or 2, help="Zahl der Prozesse")
    wahl = leser.parse_args(argv)
    dauern = dauern_lesen()
    namen = reihenfolge(module(wahl.module), dauern)
    beginn = time.monotonic()
    with ThreadPoolExecutor(max_workers=max(1, wahl.j)) as pool:
        laeufe = list(pool.map(laufen, namen))
    gesamt = time.monotonic() - beginn
    dauern_schreiben(dauern, laeufe)
    for lauf in sorted((l for l in laeufe if not l.gut), key=lambda l: l.modul):
        print(f"===== {lauf.modul} =====")
        print(lauf.ausgabe.rstrip())
        print()
    tests = sum(l.tests for l in laeufe)
    fehlschlaege = sum(l.fehlschlaege for l in laeufe)
    fehler = sum(l.fehler for l in laeufe)
    einzeln = sum(l.dauer for l in laeufe)
    print(f"Ran {tests} tests in {gesamt:.1f}s ({len(laeufe)} Dateien, {wahl.j} Prozesse; "
          f"nacheinander {einzeln:.0f}s)")
    if fehlschlaege or fehler:
        print(f"FAILED (failures={fehlschlaege}, errors={fehler})")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
