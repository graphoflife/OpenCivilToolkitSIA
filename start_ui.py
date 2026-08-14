#!/usr/bin/env python3
"""
start_ui.py -- Startet die Oberfläche.

    python3 start_ui.py [--port 8080] [--kein-browser]

Der Rechenkern läuft auch ohne das hier; siehe demo_material.py und
demo_nachweis.py. Diese Datei ist nur die Tür zur Oberfläche.
"""

import argparse
import threading
import webbrowser

from opencivil.web.server import starten


def main() -> None:
    zerleger = argparse.ArgumentParser(description="Oberfläche für OpenCivilToolkitSIA")
    zerleger.add_argument("--port", type=int, default=8080)
    zerleger.add_argument("--adresse", default="127.0.0.1")
    zerleger.add_argument(
        "--kein-browser", action="store_true", help="Browser nicht selbst öffnen"
    )
    argumente = zerleger.parse_args()

    if not argumente.kein_browser:
        adresse = f"http://{argumente.adresse}:{argumente.port}"
        threading.Timer(0.8, lambda: webbrowser.open(adresse)).start()

    starten(argumente.port, argumente.adresse)


if __name__ == "__main__":
    main()
