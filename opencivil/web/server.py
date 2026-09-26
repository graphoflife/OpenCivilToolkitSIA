"""
opencivil/web/server.py -- Schlanker HTTP-Server fuer die Oberflaeche.

VERANTWORTUNG:
Liefert die Dateien der Oberflaeche aus und reicht Anfragen an
:mod:`opencivil.web.dienst` weiter. Mehr nicht -- gerechnet wird ausschliesslich
dort, und zwar von demselben Code, der im Browser unter Pyodide laeuft.

Bewusst nur mit der Standardbibliothek gebaut. Der Rechenkern kommt ohne
Fremdpakete aus; das soll auch fuer den Server gelten, damit das ganze Werkzeug
mit einem blossen ``python3`` laeuft.

WARUM ES IHN NEBEN DER BROWSERFASSUNG NOCH GIBT:
Zwei Dinge kann nur er. Erstens startet die Oberflaeche sofort, statt erst
einige Sekunden auf Pyodide zu warten. Zweitens kann er den Bericht mit einer
richtigen TeX-Maschine zu PDF uebersetzen -- im Browser bleibt es beim ``.tex``.

WURZEL DES DOKUMENTBAUMS:
Ausgeliefert wird vom Projektverzeichnis aus, nicht von ``web/``. Das ist
Absicht: auf GitHub Pages liegt das Repo genauso im Netz, und die Bruecke im
Browser holt sich die ``.py``-Dateien unter ``/opencivil/…``. Waere die Wurzel
hier eine andere, haetten die Adressen auf beiden Wegen verschiedene Tiefe --
und genau solche Unterschiede faellt einem erst auf der veroeffentlichten Seite
auf die Fuesse.

SICHERHEIT:
Der Server bindet sich nur an 127.0.0.1. Er ist ein Arbeitsgeraet fuer den
eigenen Rechner, nicht fuer ein Netz. Ausgeliefert werden nur die in
:data:`OEFFENTLICH` genannten Ordner, und Pfadausbrueche sind geprueft.

AUFRUF::

    python3 start_ui.py
    # oder
    python3 -m opencivil.web.server --port 8080
"""

from __future__ import annotations

import json
import mimetypes
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from opencivil.bericht.latex_dokument import finde_tex_maschine, uebersetze
from opencivil.web import dienst

WURZEL = Path(__file__).resolve().parents[2]
AUSGABE_ORDNER = WURZEL / "ausgabe"

#: Was aus dem Projektverzeichnis ins Netz darf. ``opencivil`` muss dabei sein:
#: die Bruecke im Browser laedt von dort die Quelldateien des Rechenkerns.
OEFFENTLICH = ("web", "opencivil")

#: Einzelne Dateien im Wurzelverzeichnis, die ebenfalls ausgeliefert werden.
OEFFENTLICHE_DATEIEN = ("index.html", "favicon.ico")

# application/wasm ist nicht bloss Kosmetik: ohne diesen Typ verweigert
# WebAssembly.instantiateStreaming den Dienst und Pyodide faellt auf einen
# langsameren Weg zurueck.
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("application/javascript", ".mjs")
mimetypes.add_type("application/wasm", ".wasm")
mimetypes.add_type("font/woff2", ".woff2")
mimetypes.add_type("text/x-python; charset=utf-8", ".py")


# ===========================================================================
# Was nur der Server kann: PDF
# ===========================================================================


def bericht_mit_pdf(rumpf: dict) -> dienst.Antwort:
    """
    Der Bericht des Dienstes, zusaetzlich auf die Platte gelegt und uebersetzt.

    Das ``.tex`` stammt unveraendert aus :func:`opencivil.web.dienst.bericht` --
    hier kommt nur dazu, was ein Browser nicht kann.
    """
    antwort = dienst.bearbeite("bericht", rumpf)
    if antwort.ist_fehler or not rumpf.get("pdf", True):
        return antwort

    pfad = (AUSGABE_ORDNER / antwort.daten["dateiname"]).with_suffix(".tex")
    pfad.parent.mkdir(parents=True, exist_ok=True)
    pfad.write_text(antwort.daten["tex"], encoding="utf-8")

    ergebnis = uebersetze(pfad)
    return dienst.Antwort({
        **antwort.daten,
        "tex_pfad": str(pfad),
        "pdf_pfad": str(ergebnis.pdf_pfad) if ergebnis.hat_pdf else "",
        "maschine": ergebnis.maschine,
        "meldung": ergebnis.meldung,
    })


# ===========================================================================
# Statische Dateien
# ===========================================================================


def aufloesen(pfad: str) -> Path | None:
    """
    Wandelt eine Adresse in eine Datei -- oder ``None``, wenn sie nicht darf.

    Erlaubt ist nur, was in :data:`OEFFENTLICH` und
    :data:`OEFFENTLICHE_DATEIEN` steht. Alles andere im Projektverzeichnis --
    ``daten/``, ``.git/``, ``tests/`` -- bleibt draussen, auch wenn der Server
    ohnehin nur auf 127.0.0.1 horcht.
    """
    teile = [t for t in pfad.split("/") if t not in ("", ".")]
    if not teile:
        teile = ["index.html"]
    if ".." in teile:
        return None
    if teile[0] not in OEFFENTLICH and not (
            len(teile) == 1 and teile[0] in OEFFENTLICHE_DATEIEN):
        return None

    ziel = (WURZEL / Path(*teile)).resolve()
    # Guertel und Hosenträger: auch nach dem Aufloesen von Verknuepfungen muss
    # die Datei noch unterhalb der Wurzel liegen.
    if not ziel.is_relative_to(WURZEL.resolve()):
        return None
    if ziel.is_dir():
        # /web/ meint /web/index.html -- so haelt es auch GitHub Pages.
        ziel = ziel / "index.html"
    return ziel if ziel.is_file() else None


# ===========================================================================
# HTTP
# ===========================================================================


class Handler(BaseHTTPRequestHandler):
    server_version = "OpenCivilToolkitSIA"
    protocol_version = "HTTP/1.1"

    # -- Antworten ----------------------------------------------------------

    def _json(self, daten: Any, status: int = 200) -> None:
        rumpf = dienst.nach_json(daten).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(rumpf)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(rumpf)

    def _antwort(self, antwort: dienst.Antwort) -> None:
        self._json(antwort.daten, antwort.status)

    def _fehler(self, status: int, meldung: str, spur: str = "") -> None:
        self._json({"fehler": meldung, "spur": spur}, status)

    # -- Verteilung ---------------------------------------------------------

    def do_GET(self) -> None:  # noqa: N802
        pfad = urlparse(self.path).path
        try:
            if pfad.startswith("/api/"):
                # Ohne Rumpf -- taugt fuer katalog und beispiel.
                return self._antwort(dienst.bearbeite(pfad[len("/api/"):]))
            return self._statisch(pfad)
        except Exception as exc:  # pragma: no cover -- Notnagel
            return self._fehler(500, str(exc), traceback.format_exc())

    def do_POST(self) -> None:  # noqa: N802
        pfad = urlparse(self.path).path
        if not pfad.startswith("/api/"):
            return self._fehler(404, f"Unbekannter Endpunkt: POST {pfad}")
        name = pfad[len("/api/"):]

        try:
            laenge = int(self.headers.get("Content-Length") or 0)
            roh = self.rfile.read(laenge) if laenge else b"{}"
            rumpf = json.loads(roh.decode("utf-8") or "{}")
        except (ValueError, UnicodeDecodeError) as exc:
            return self._fehler(400, f"Ungültiges JSON: {exc}")

        try:
            if name == "bericht":
                return self._antwort(bericht_mit_pdf(rumpf))
            return self._antwort(dienst.bearbeite(name, rumpf))
        except Exception as exc:  # pragma: no cover -- Notnagel
            return self._fehler(
                500, f"{type(exc).__name__}: {exc}", traceback.format_exc())

    # -- Statische Dateien --------------------------------------------------

    def _statisch(self, pfad: str) -> None:
        ziel = aufloesen(pfad)
        if ziel is None:
            return self._fehler(404, f"Nicht gefunden: {pfad}")

        inhalt = ziel.read_bytes()
        art, _ = mimetypes.guess_type(str(ziel))
        self.send_response(200)
        self.send_header("Content-Type", art or "application/octet-stream")
        self.send_header("Content-Length", str(len(inhalt)))
        # Beim Entwickeln aendert sich die Oberflaeche laufend, also nicht
        # zwischenspeichern. Ausgenommen ist, was sich nie aendert: die
        # mitgelieferten Fremdpakete (KaTeX samt Schriften, MathLive, Pyodide)
        # -- 13 MB bei jedem Neuladen waeren laestig.
        unveraenderlich = "web/vendor/" in ziel.as_posix()
        self.send_header(
            "Cache-Control", "max-age=86400" if unveraenderlich else "no-cache")
        self.end_headers()
        self.wfile.write(inhalt)

    def log_message(self, format: str, *args: Any) -> None:
        # Nur Fehler melden; der Rest waere beim Arbeiten bloss Lärm.
        if args and str(args[1] if len(args) > 1 else "").startswith(("4", "5")):
            super().log_message(format, *args)


def starten(port: int = 8080, adresse: str = "127.0.0.1") -> None:
    if not (WURZEL / "web").is_dir():
        raise SystemExit(f"Der Ordner der Oberfläche fehlt: {WURZEL / 'web'}")

    server = ThreadingHTTPServer((adresse, port), Handler)
    print(f"OpenCivilToolkitSIA – Oberfläche läuft auf http://{adresse}:{port}")
    if finde_tex_maschine() is None:
        print("Hinweis: keine TeX-Maschine gefunden, der Bericht bleibt beim .tex.")
    print("Beenden mit Strg+C.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nBeendet.")
    finally:
        server.server_close()


if __name__ == "__main__":
    import argparse

    zerleger = argparse.ArgumentParser(description="Oberfläche für OpenCivilToolkitSIA")
    zerleger.add_argument("--port", type=int, default=8080)
    zerleger.add_argument("--adresse", default="127.0.0.1")
    argumente = zerleger.parse_args()
    starten(argumente.port, argumente.adresse)
