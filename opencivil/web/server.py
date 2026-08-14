"""
opencivil/web/server.py -- Schlanker HTTP-Server fuer die Oberflaeche.

VERANTWORTUNG:
Stellt die Dateien der Oberflaeche bereit und bietet eine JSON-Schnittstelle zum
Rechenkern. Mehr nicht -- gerechnet wird ausschliesslich im Kern, der von diesem
Baustein nichts weiss.

Bewusst nur mit der Standardbibliothek gebaut. Der Rechenkern kommt ohne
Fremdpakete aus; das soll auch fuer den Server gelten, damit das ganze Werkzeug
mit einem blossen ``python3`` laeuft.

SICHERHEIT:
Der Server bindet sich nur an 127.0.0.1. Er ist ein Arbeitsgeraet fuer den
eigenen Rechner, nicht fuer ein Netz. Statische Dateien werden gegen
Pfadausbrueche geprueft.

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
from typing import Any, Callable, Dict, Optional, Tuple
from urllib.parse import urlparse

from opencivil.bericht.latex_dokument import schreibe
from opencivil.core.rechenwerk import RechenwerkFehler
from opencivil.projekt import Projekt, ProjektFehler
from opencivil.web import api

WURZEL = Path(__file__).resolve().parents[2]
WEB_ORDNER = WURZEL / "web"
PROJEKT_DATEI = WURZEL / "daten" / "projekt.json"
AUSGABE_ORDNER = WURZEL / "ausgabe"

mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("font/woff2", ".woff2")


class ApiFehler(Exception):
    """Fehler mit vorgegebenem HTTP-Status."""

    def __init__(self, status: int, meldung: str) -> None:
        self.status = status
        super().__init__(meldung)


# ===========================================================================
# Fachliche Endpunkte
# ===========================================================================


def projekt_laden() -> Projekt:
    """Laedt das gespeicherte Projekt, sonst das Beispiel."""
    if PROJEKT_DATEI.exists():
        try:
            return Projekt.laden(PROJEKT_DATEI)
        except Exception as exc:
            raise ApiFehler(
                500, f"Die gespeicherte Projektdatei ist unlesbar: {exc}"
            ) from exc
    return Projekt.beispiel()


def projekt_speichern(rumpf: Dict[str, Any]) -> dict:
    projekt = Projekt.aus_dict(rumpf)
    projekt.speichern(PROJEKT_DATEI)
    return {"gespeichert": str(PROJEKT_DATEI), "projekt": projekt.als_dict()}


def rechnen(rumpf: Dict[str, Any]) -> dict:
    """
    Rechnet ein Projekt durch.

    Ohne ``ziele`` werden alle Nachweise gerechnet. Mit ``ziele`` genau diese --
    dann loest das Rechenwerk rueckwaerts auf und meldet, was fehlt.
    """
    projekt = Projekt.aus_dict(rumpf.get("projekt") or {})
    aufbau = projekt.aufbauen()

    ziele = list(rumpf.get("ziele") or [])
    if not ziele:
        ziele = aufbau.alle_nachweisziele() + aufbau.eckwertziele()
    if not ziele:
        # Kein Nachweis vorhanden -- dann wenigstens alle Materialkennwerte.
        loesung = aufbau.werk.loese_alles()
        return api.loesung_dict(loesung, aufbau, ())

    unbekannt = [z for z in ziele if aufbau.werk.definition(z) is None]
    if unbekannt:
        raise ApiFehler(400, f"Unbekannte Ziele: {', '.join(unbekannt)}")

    loesung = aufbau.werk.loese(*ziele)
    return api.loesung_dict(loesung, aufbau, ziele)


def alles_rechnen(rumpf: Dict[str, Any]) -> dict:
    """Rechnet alles, was sich aus den vorhandenen Eingaben ergibt."""
    projekt = Projekt.aus_dict(rumpf.get("projekt") or {})
    aufbau = projekt.aufbauen()
    return api.loesung_dict(aufbau.werk.loese_alles(), aufbau, ())


def ziele_auflisten(rumpf: Dict[str, Any]) -> dict:
    """Alle Werte, die als Rechenziel gewaehlt werden koennen."""
    projekt = Projekt.aus_dict(rumpf.get("projekt") or {})
    aufbau = projekt.aufbauen()
    eintraege = []
    for wert_id in aufbau.werk.moegliche_ziele():
        definition = aufbau.werk.definition(wert_id)
        if definition is None:
            continue
        eintraege.append({
            "id": wert_id,
            "symbol": definition.symbol,
            "beschreibung": definition.beschreibung,
            "einheit": (
                definition.einheit.name
                if definition.einheit.name not in ("", "-") else ""
            ),
            "referenz": definition.referenz,
            "namensraum": definition.namensraum,
        })
    return {"ziele": eintraege, "zuordnung": api.zuordnung(aufbau)}


def bericht(rumpf: Dict[str, Any]) -> dict:
    """Schreibt das LaTeX-Dokument und uebersetzt es, wenn moeglich."""
    projekt = Projekt.aus_dict(rumpf.get("projekt") or {})
    aufbau = projekt.aufbauen()
    ziele = list(rumpf.get("ziele") or []) or (
        aufbau.alle_nachweisziele() + aufbau.eckwertziele()
    )
    loesung = aufbau.werk.loese(*ziele) if ziele else aufbau.werk.loese_alles()

    name = "".join(z if z.isalnum() or z in "-_" else "_" for z in projekt.name) or "bericht"
    ergebnis = schreibe(
        loesung,
        AUSGABE_ORDNER / name,
        titel=projekt.name,
        untertitel="OpenCivilToolkitSIA – Berechnung nach SIA 262:2025",
        pdf=bool(rumpf.get("pdf", True)),
    )
    return {
        "tex_pfad": str(ergebnis.tex_pfad),
        "tex": ergebnis.tex_pfad.read_text(encoding="utf-8"),
        "pdf_pfad": str(ergebnis.pdf_pfad) if ergebnis.hat_pdf else "",
        "maschine": ergebnis.maschine,
        "meldung": ergebnis.meldung,
    }


#: Endpunkt -> (Methode, Funktion). ``None`` als Funktion = Sonderbehandlung.
ENDPUNKTE: Dict[Tuple[str, str], Callable[[Dict[str, Any]], dict]] = {
    ("POST", "/api/rechnen"): rechnen,
    ("POST", "/api/alles"): alles_rechnen,
    ("POST", "/api/ziele"): ziele_auflisten,
    ("POST", "/api/bericht"): bericht,
    ("PUT", "/api/projekt"): projekt_speichern,
}


# ===========================================================================
# HTTP
# ===========================================================================


class Handler(BaseHTTPRequestHandler):
    server_version = "OpenCivilToolkitSIA"
    protocol_version = "HTTP/1.1"

    # -- Antworten ----------------------------------------------------------

    def _json(self, daten: Any, status: int = 200) -> None:
        rumpf = json.dumps(daten, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(rumpf)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(rumpf)

    def _fehler(self, status: int, meldung: str, spur: str = "") -> None:
        self._json({"fehler": meldung, "spur": spur}, status)

    # -- Verteilung ---------------------------------------------------------

    def do_GET(self) -> None:  # noqa: N802
        pfad = urlparse(self.path).path
        try:
            if pfad == "/api/katalog":
                return self._json(api.katalog())
            if pfad == "/api/projekt":
                return self._json(projekt_laden().als_dict())
            return self._statisch(pfad)
        except ApiFehler as exc:
            return self._fehler(exc.status, str(exc))
        except Exception as exc:  # pragma: no cover -- Notnagel
            return self._fehler(500, str(exc), traceback.format_exc())

    def do_PUT(self) -> None:  # noqa: N802
        self._mit_rumpf("PUT")

    def do_POST(self) -> None:  # noqa: N802
        self._mit_rumpf("POST")

    def _mit_rumpf(self, methode: str) -> None:
        pfad = urlparse(self.path).path
        funktion = ENDPUNKTE.get((methode, pfad))
        if funktion is None:
            return self._fehler(404, f"Unbekannter Endpunkt: {methode} {pfad}")
        try:
            laenge = int(self.headers.get("Content-Length") or 0)
            roh = self.rfile.read(laenge) if laenge else b"{}"
            rumpf = json.loads(roh.decode("utf-8") or "{}")
            return self._json(funktion(rumpf))
        except json.JSONDecodeError as exc:
            return self._fehler(400, f"Ungültiges JSON: {exc}")
        except (ProjektFehler, RechenwerkFehler) as exc:
            # Erwartbare Bedienfehler -- ohne Stapelspur, dafuer mit klarer Meldung.
            return self._fehler(400, str(exc))
        except ApiFehler as exc:
            return self._fehler(exc.status, str(exc))
        except Exception as exc:
            return self._fehler(500, f"{type(exc).__name__}: {exc}", traceback.format_exc())

    # -- Statische Dateien --------------------------------------------------

    def _statisch(self, pfad: str) -> None:
        if pfad in ("/", ""):
            pfad = "/index.html"
        ziel = (WEB_ORDNER / pfad.lstrip("/")).resolve()
        # Pfadausbruch verhindern.
        if not str(ziel).startswith(str(WEB_ORDNER.resolve())) or not ziel.is_file():
            return self._fehler(404, f"Nicht gefunden: {pfad}")

        inhalt = ziel.read_bytes()
        art, _ = mimetypes.guess_type(str(ziel))
        self.send_response(200)
        self.send_header("Content-Type", art or "application/octet-stream")
        self.send_header("Content-Length", str(len(inhalt)))
        # Die Oberflaeche wird beim Entwickeln laufend geaendert -- nicht zwischenspeichern.
        self.send_header("Cache-Control", "no-cache" if ziel.suffix != ".woff2" else "max-age=86400")
        self.end_headers()
        self.wfile.write(inhalt)

    def log_message(self, format: str, *args: Any) -> None:
        # Nur Fehler melden; der Rest waere beim Arbeiten bloss Lärm.
        if args and str(args[1] if len(args) > 1 else "").startswith(("4", "5")):
            super().log_message(format, *args)


def starten(port: int = 8080, adresse: str = "127.0.0.1") -> None:
    if not WEB_ORDNER.is_dir():
        raise SystemExit(f"Der Ordner der Oberfläche fehlt: {WEB_ORDNER}")
    server = ThreadingHTTPServer((adresse, port), Handler)
    print(f"OpenCivilToolkitSIA – Oberfläche läuft auf http://{adresse}:{port}")
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
