#!/usr/bin/env python3
"""
werkzeug/pyodide_holen.py -- Pyodide herunterladen und ins Repo legen.

VERANTWORTUNG:
Holt das Paket ``pyodide-core`` von GitHub und legt genau die fuenf Dateien
nach ``web/vendor/pyodide/``, die der Browser braucht. Alles andere aus dem
Paket bleibt draussen -- siehe ``web/vendor/pyodide/HERKUNFT.md``.

Dieses Skript laeuft von Hand, nicht beim Bauen: Pyodide liegt bewusst im Repo,
damit die Seite ohne fremden Dienst laeuft. Gebraucht wird es nur, wenn die
Version gewechselt werden soll.

FREMDPAKETE:
Dazu die Pakete, die die App «Python» einbinden kann (:data:`PAKETE`):
numpy und pandas, mit allem, was sie brauchen (Benutzer, 2026-10-15). Sie
kommen einzeln aus der Verteilung derselben Fassung, und jede Datei wird gegen
die Pruefsumme in ``pyodide-lock.json`` gehalten. Ein weiteres Paket kommt nur
mit der ausdruecklichen Erlaubnis des Benutzers dazu, Datei fuer Datei.
Welche Pakete dann beiliegen, liest die Bruecke aus den Dateien im Ordner
(``opencivil/web/bruecke.py``) -- eine zweite Liste gibt es nicht.

AUFRUF::

    python3 werkzeug/pyodide_holen.py              # Fassung aus HERKUNFT.md
    python3 werkzeug/pyodide_holen.py 314.0.7      # bestimmte Fassung
    python3 werkzeug/pyodide_holen.py --pakete     # nur die Fremdpakete
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path
from typing import Iterable, List

WURZEL = Path(__file__).resolve().parents[1]
ZIEL = WURZEL / "web" / "vendor" / "pyodide"
HERKUNFT = ZIEL / "HERKUNFT.md"

#: Nur diese Dateien werden uebernommen. Der Rest des Pakets ist fuer den
#: Browser nutzlos (Kommandozeile, Typangaben) und wuerde das Repo bloss
#: aufblaehen.
GEBRAUCHT = (
    "pyodide.mjs",
    "pyodide.asm.mjs",
    "pyodide.asm.wasm",
    "python_stdlib.zip",
    "pyodide-lock.json",
)

QUELLE = ("https://github.com/pyodide/pyodide/releases/download/"
          "{fassung}/pyodide-core-{fassung}.tar.bz2")

#: Was die App «Python» einbinden kann; was diese brauchen, kommt mit
#: (:func:`huelle`). Jedes weitere nur mit Erlaubnis des Benutzers.
PAKETE = ("numpy", "pandas")

#: Die Pakete einzeln, aus der vollen Verteilung derselben Fassung.
PAKETQUELLE = "https://cdn.jsdelivr.net/pyodide/v{fassung}/full/{datei}"


def fassung_aus_herkunft() -> str:
    """Liest die derzeit abgelegte Fassung aus der Herkunftsnotiz."""
    if not HERKUNFT.is_file():
        raise SystemExit(f"{HERKUNFT} fehlt -- bitte Fassung angeben.")
    treffer = re.search(r"^# Pyodide (\S+)", HERKUNFT.read_text(encoding="utf-8"), re.M)
    if not treffer:
        raise SystemExit(f"In {HERKUNFT} steht keine Fassung in der Titelzeile.")
    return treffer.group(1)


def holen(fassung: str) -> None:
    adresse = QUELLE.format(fassung=fassung)
    print(f"Lade {adresse}")

    with tempfile.TemporaryDirectory() as ordner:
        paket = Path(ordner) / "pyodide-core.tar.bz2"
        with urllib.request.urlopen(adresse, timeout=300) as antwort:
            paket.write_bytes(antwort.read())
        print(f"  {paket.stat().st_size / 1e6:.1f} MB geladen, entpacke …")

        with tarfile.open(paket, "r:bz2") as archiv:
            # Nur die gebrauchten Dateien, und nur solche unmittelbar im Ordner
            # ``pyodide/`` -- das schliesst Pfadausbrueche im Archiv gleich mit aus.
            gefunden = {}
            for eintrag in archiv.getmembers():
                teile = Path(eintrag.name).parts
                if (len(teile) == 2 and teile[0] == "pyodide"
                        and teile[1] in GEBRAUCHT and eintrag.isfile()):
                    gefunden[teile[1]] = eintrag

            fehlend = set(GEBRAUCHT) - set(gefunden)
            if fehlend:
                raise SystemExit(
                    "Im Paket fehlen erwartete Dateien: " + ", ".join(sorted(fehlend))
                    + "\nHat Pyodide den Aufbau des Pakets geändert?")

            ZIEL.mkdir(parents=True, exist_ok=True)
            for name, eintrag in sorted(gefunden.items()):
                quelle = archiv.extractfile(eintrag)
                assert quelle is not None
                ziel = ZIEL / name
                with quelle, ziel.open("wb") as aus:
                    shutil.copyfileobj(quelle, aus)
                ziel.chmod(0o644)
                print(f"  {name:<20} {ziel.stat().st_size / 1e6:6.1f} MB")

    pakete_holen(fassung)
    print(f"\nFertig in {ZIEL}")
    print(f"Steht in HERKUNFT.md noch die alte Fassung? Titelzeile auf "
          f"'# Pyodide {fassung}' setzen.")


def huelle(pakete: dict, namen: Iterable[str]) -> List[str]:
    """Die Pakete samt allem, was sie brauchen -- nach ``pyodide-lock.json``."""
    gesehen, offen = set(), list(namen)
    while offen:
        name = offen.pop()
        if name not in gesehen:
            gesehen.add(name)
            offen += pakete[name].get("depends", [])
    return sorted(gesehen)


def pakete_holen(fassung: str) -> None:
    """
    Holt :data:`PAKETE` samt Huelle und prueft jede Datei gegen die Pruefsumme
    der Fassung. Was schon richtig daliegt, bleibt; ein Rad, das nicht mehr
    gebraucht wird -- nach einem Wechsel der Fassung --, geht weg.
    """
    pakete = json.loads((ZIEL / "pyodide-lock.json").read_text(encoding="utf-8"))["packages"]
    gebraucht = {pakete[n]["file_name"]: pakete[n] for n in huelle(pakete, PAKETE)}
    for alt in ZIEL.glob("*.whl"):
        if alt.name not in gebraucht:
            alt.unlink()
            print(f"  {alt.name} entfernt")
    for datei, eintrag in sorted(gebraucht.items()):
        ziel = ZIEL / datei
        if ziel.is_file() and hashlib.sha256(ziel.read_bytes()).hexdigest() == eintrag["sha256"]:
            print(f"  {datei:<62} liegt schon da")
            continue
        adresse = PAKETQUELLE.format(fassung=fassung, datei=datei)
        with urllib.request.urlopen(adresse, timeout=300) as antwort:
            inhalt = antwort.read()
        if hashlib.sha256(inhalt).hexdigest() != eintrag["sha256"]:
            raise SystemExit(f"Pruefsumme stimmt nicht: {adresse}")
        ziel.write_bytes(inhalt)
        ziel.chmod(0o644)
        print(f"  {datei:<62} {len(inhalt) / 1e6:6.2f} MB")


if __name__ == "__main__":
    argumente = [a for a in sys.argv[1:] if a != "--pakete"]
    fassung = argumente[0] if argumente else fassung_aus_herkunft()
    if "--pakete" in sys.argv[1:]:
        pakete_holen(fassung)
    else:
        holen(fassung)
