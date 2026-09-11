"""
opencivil/web/bruecke.py -- Welche Dateien der Browser laden muss.

VERANTWORTUNG:
Fuehrt Buch darueber, aus welchen Quelldateien der Rechenkern besteht, und
schreibt diese Liste nach ``web/kern/dateien.json``. Die Bruecke in
``web/js/kern.js`` liest sie, holt die Dateien uebers Netz und legt sie ins
Dateisystem von Pyodide -- danach ist ``import opencivil`` im Browser
dasselbe wie auf dem Rechner.

WARUM EINE LISTE UND KEIN ARCHIV:
Ein Archiv waere ein zweites, erzeugtes Abbild des Quellcodes im Repo -- und
damit etwas, das unbemerkt veralten kann. Die Liste ist reiner Text, im Diff
lesbar, und :func:`stimmt_ueberein` prueft im Test, dass sie zu den
tatsaechlich vorhandenen Dateien passt. Veraltet sie, schlaegt der Test an,
nicht erst die veroeffentlichte Seite.

WARUM ALLE DATEIEN UND NICHT NUR DIE GEBRAUCHTEN:
Man koennte die Liste auf das beschraenken, was :mod:`opencivil.web.dienst`
einbindet. Dann muesste die Regel aber bei jeder neuen Einbindung nachgezogen
werden, und wer das vergisst, merkt es erst im Browser. Ein paar Dutzend
Kilobyte sind der bessere Handel.

AUFRUF::

    python3 -m opencivil.web.bruecke        # schreibt web/kern/dateien.json
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

WURZEL = Path(__file__).resolve().parents[2]
PAKET = WURZEL / "opencivil"
MANIFEST = WURZEL / "web" / "kern" / "dateien.json"


def kerndateien() -> List[str]:
    """
    Alle Quelldateien des Kerns, als Pfade vom Projektverzeichnis aus.

    Sortiert, damit das Manifest bei gleichem Stand Zeichen fuer Zeichen gleich
    herauskommt und im Diff nur echte Aenderungen auftauchen.
    """
    return sorted(
        pfad.relative_to(WURZEL).as_posix()
        for pfad in PAKET.rglob("*.py")
        if "__pycache__" not in pfad.parts
    )


def manifest() -> dict:
    return {
        "hinweis": (
            "Erzeugt von opencivil/web/bruecke.py. Nicht von Hand ändern -- "
            "stattdessen 'python3 -m opencivil.web.bruecke' laufen lassen."
        ),
        "dateien": kerndateien(),
    }


def stimmt_ueberein() -> bool:
    """Ob das abgelegte Manifest den vorhandenen Dateien entspricht."""
    if not MANIFEST.is_file():
        return False
    try:
        abgelegt = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return abgelegt.get("dateien") == kerndateien()


def schreiben(pfad: Path | None = None) -> Path:
    ziel = Path(pfad) if pfad is not None else MANIFEST
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(
        json.dumps(manifest(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return ziel


if __name__ == "__main__":
    geschrieben = schreiben()
    print(f"{geschrieben.relative_to(WURZEL)}: {len(kerndateien())} Dateien")
