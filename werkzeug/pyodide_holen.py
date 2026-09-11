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

AUFRUF::

    python3 werkzeug/pyodide_holen.py            # Fassung aus HERKUNFT.md
    python3 werkzeug/pyodide_holen.py 314.0.7    # bestimmte Fassung
"""

from __future__ import annotations

import re
import shutil
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

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

    print(f"\nFertig in {ZIEL}")
    print(f"Steht in HERKUNFT.md noch die alte Fassung? Titelzeile auf "
          f"'# Pyodide {fassung}' setzen.")


if __name__ == "__main__":
    holen(sys.argv[1] if len(sys.argv) > 1 else fassung_aus_herkunft())
