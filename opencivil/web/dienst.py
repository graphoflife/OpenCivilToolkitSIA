"""
opencivil/web/dienst.py -- Der Rechendienst, unabhaengig vom Transportweg.

VERANTWORTUNG:
Nimmt eine Anfrage als gewoehnliches ``dict`` entgegen und gibt die Antwort als
``dict`` zurueck. Von HTTP weiss dieser Baustein nichts, vom Dateisystem auch
nichts, und einen Unterprozess startet er nie.

WARUM DAS WICHTIG IST:
Die Oberflaeche laeuft auf zwei Wegen -- auf dem Rechner ueber
:mod:`opencivil.web.server` mit CPython, im Browser ueber ``web/js/kern.js`` mit
Pyodide. Beide Wege sind bloss duenne Huellen um genau dieses Modul. Damit ist
baulich ausgeschlossen, dass im Browser etwas *nachgebaut* wird: es gibt nur
eine einzige Rechenimplementierung, und die ist Python.

Was eine Huelle beisteuern darf, ist alles, was ihre Umgebung eigen hat -- der
Server etwa die Uebersetzung des Berichts zu PDF, der Browser das Ablegen des
Projekts im Speicher des Browsers. Gerechnet wird in beiden Faellen hier.

EIGENSTAENDIG NUTZBAR::

    from opencivil.web.dienst import bearbeite
    antwort = bearbeite("rechnen", {"projekt": {...}})
    print(antwort.status, antwort.daten["werte"])
"""

from __future__ import annotations

import json
import traceback
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Mapping

from opencivil.bericht.latex_dokument import als_tex
from opencivil.core.rechenwerk import RechenwerkFehler
from opencivil.projekt import Projekt, ProjektFehler
from opencivil.web import api
from opencivil.web.api import endlich


class DienstFehler(Exception):
    """Fehler mit vorgegebenem Status, etwa fuer eine unbekannte Anfrage."""

    def __init__(self, status: int, meldung: str) -> None:
        self.status = status
        super().__init__(meldung)


@dataclass(frozen=True)
class Antwort:
    """Was der Dienst zurueckgibt: Nutzlast plus Status nach HTTP-Art."""

    daten: Dict[str, Any] = field(default_factory=dict)
    status: int = 200

    @property
    def ist_fehler(self) -> bool:
        return self.status >= 400


# ===========================================================================
# Die einzelnen Anfragen
# ===========================================================================


def _projekt(rumpf: Mapping[str, Any]) -> Projekt:
    """Baut das Projekt aus dem Anfragerumpf."""
    return Projekt.aus_dict(rumpf.get("projekt") or {})


def katalog(rumpf: Mapping[str, Any]) -> Dict[str, Any]:
    """Normsorten, Kennwertvorlagen und Einheiten -- alles, was fest steht."""
    return api.katalog()


def beispiel(rumpf: Mapping[str, Any]) -> Dict[str, Any]:
    """Das Beispielprojekt, mit dem eine leere Oberflaeche startet."""
    return Projekt.beispiel().als_dict()


#: Woran eine Projektdatei zu erkennen ist. Mindestens eines davon muss da sein.
KENNFELDER = ("name", "materialien", "querschnitte")


def pruefen(rumpf: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Prueft eine Projektbeschreibung und gibt sie aufgeraeumt zurueck.

    Dafuer gedacht, dass eine hochgeladene oder im Browser abgelegte Datei durch
    denselben Aufbau laeuft wie alles andere: fehlt ein Feld oder stammt die
    Datei aus einer aelteren Fassung, greifen hier die Wandlung des alten
    Formats und die Pruefungen aus :mod:`opencivil.projekt` -- nicht eine
    zweite, nachgebaute Pruefung in JavaScript.

    Die Vorpruefung auf :data:`KENNFELDER` ist noetig, weil
    ``Projekt.aus_dict`` mit Absicht nachsichtig ist: es nimmt jedes ``dict``
    und macht daraus notfalls ein leeres Projekt. Beim Laden einer Beschreibung
    ist das richtig -- beim Oeffnen einer Datei waere es verheerend. Wer eine
    beliebige JSON-Datei erwischt, bekaeme sonst wortlos ein leeres Projekt
    und haette seine Arbeit verloren.
    """
    roh = rumpf.get("projekt")
    if not isinstance(roh, Mapping):
        raise DienstFehler(400, "Die Beschreibung muss ein JSON-Objekt sein.")
    if not any(feld in roh for feld in KENNFELDER):
        raise DienstFehler(400, (
            "Das sieht nicht nach einem Projekt aus – keines der Felder "
            + ", ".join(KENNFELDER) + " ist vorhanden."))

    projekt = Projekt.aus_dict(roh)
    projekt.pruefen()
    return {"projekt": projekt.als_dict()}


def rechnen(rumpf: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Rechnet ein Projekt durch.

    Ohne ``ziele`` wird alles gerechnet, was die Nachweise brauchen. Mit
    ``ziele`` genau diese -- dann loest das Rechenwerk rueckwaerts auf und
    meldet, welche Eingabe fehlt.
    """
    projekt = _projekt(rumpf)
    aufbau = projekt.aufbauen()

    ziele = list(rumpf.get("ziele") or [])
    if not ziele:
        # Die Reihenfolge bestimmt den Aufbau der Herleitung: erst die
        # Baustoffe, dann die Bauteile.
        ziele = (aufbau.materialziele() + aufbau.eckwertziele()
                 + aufbau.alle_nachweisziele())
    if not ziele:
        # Kein Nachweis vorhanden -- dann wenigstens alle Materialkennwerte.
        return api.loesung_dict(aufbau.werk.loese_alles(), aufbau, ())

    unbekannt = [z for z in ziele if aufbau.werk.definition(z) is None]
    if unbekannt:
        raise DienstFehler(400, f"Unbekannte Ziele: {', '.join(unbekannt)}")

    return api.loesung_dict(aufbau.werk.loese(*ziele), aufbau, ziele)


def alles(rumpf: Mapping[str, Any]) -> Dict[str, Any]:
    """Rechnet alles, was sich aus den vorhandenen Eingaben ergibt."""
    aufbau = _projekt(rumpf).aufbauen()
    return api.loesung_dict(aufbau.werk.loese_alles(), aufbau, ())


def ziele(rumpf: Mapping[str, Any]) -> Dict[str, Any]:
    """Alle Werte, die sich als Rechenziel waehlen lassen."""
    aufbau = _projekt(rumpf).aufbauen()
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
                definition.einheit.beschriftung
                if definition.einheit.name not in ("", "-") else ""
            ),
            "referenz": definition.referenz,
            "namensraum": definition.namensraum,
        })
    return {"ziele": eintraege, "zuordnung": api.zuordnung(aufbau)}


def bericht(rumpf: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Baut das LaTeX-Dokument und gibt es als Zeichenkette zurueck.

    Geschrieben wird hier nichts. Der Browser macht daraus einen Download, der
    Server legt es zusaetzlich in ``ausgabe/`` ab und versucht die Uebersetzung
    zu PDF -- das ``.tex`` ist auf beiden Wegen dasselbe.
    """
    projekt = _projekt(rumpf)
    aufbau = projekt.aufbauen()
    gewuenscht = list(rumpf.get("ziele") or []) or (
        aufbau.alle_nachweisziele() + aufbau.eckwertziele()
    )
    loesung = (aufbau.werk.loese(*gewuenscht) if gewuenscht
               else aufbau.werk.loese_alles())

    return {
        "tex": als_tex(
            loesung,
            titel=projekt.name,
            untertitel="OpenCivilToolkitSIA – Berechnung nach SIA 262:2025",
        ),
        "dateiname": dateiname(projekt.name),
    }


def dateiname(name: str) -> str:
    """Macht aus einem Projektnamen einen brauchbaren Dateinamen."""
    gesaeubert = "".join(z if z.isalnum() or z in "-_" else "_" for z in name)
    return gesaeubert.strip("_") or "bericht"


#: Name der Anfrage -> Funktion. Diese Namen sind der ganze Vertrag zwischen
#: Oberflaeche und Kern; beide Huellen reichen sie unveraendert durch.
ANFRAGEN: Dict[str, Callable[[Mapping[str, Any]], Dict[str, Any]]] = {
    "katalog": katalog,
    "beispiel": beispiel,
    "pruefen": pruefen,
    "rechnen": rechnen,
    "alles": alles,
    "ziele": ziele,
    "bericht": bericht,
}


# ===========================================================================
# Einstieg
# ===========================================================================


def bearbeite(name: str, rumpf: Mapping[str, Any] | None = None) -> Antwort:
    """
    Fuehrt eine Anfrage aus. Wirft nicht -- Fehler kommen als Antwort zurueck.

    Dass auch der Fehlerfall eine gewoehnliche Antwort ist, haelt die beiden
    Huellen duenn: keine muss sich ueberlegen, welche Ausnahme welchen Status
    verdient.
    """
    funktion = ANFRAGEN.get(name)
    if funktion is None:
        bekannt = ", ".join(sorted(ANFRAGEN))
        return _fehler(404, f"Unbekannte Anfrage: {name} (bekannt sind: {bekannt})")

    try:
        return Antwort(funktion(rumpf or {}))
    except DienstFehler as exc:
        return _fehler(exc.status, str(exc))
    except (ProjektFehler, RechenwerkFehler) as exc:
        # Erwartbare Bedienfehler -- ohne Stapelspur, dafuer mit klarer Meldung.
        return _fehler(400, str(exc))
    except Exception as exc:  # noqa: BLE001 -- Notnagel, damit nichts stumm bricht
        return _fehler(500, f"{type(exc).__name__}: {exc}", traceback.format_exc())


def _fehler(status: int, meldung: str, spur: str = "") -> Antwort:
    return Antwort({"fehler": meldung, "spur": spur}, status)


def nach_json(daten: Any) -> str:
    """
    Wandelt eine Antwort in JSON.

    ``allow_nan=False`` ist Absicht: ``json.dumps`` schriebe sonst ``Infinity``
    und ``NaN``. Python liest das wieder, ``JSON.parse`` im Browser lehnt es ab
    -- die Antwort kaeme heil an und waere trotzdem unbrauchbar. Lieber hier
    laut scheitern als dort stumm. :func:`endlich` raeumt die Faelle vorher weg,
    sodass der Riegel nur zuschlaegt, wenn wirklich etwas Neues auftaucht.
    """
    return json.dumps(endlich(daten), ensure_ascii=False, allow_nan=False)


def bearbeite_json(name: str, rumpf_json: str = "{}") -> str:
    """
    Dasselbe wie :func:`bearbeite`, aber mit JSON hinein und heraus.

    Der Weg fuer den Browser. Dass hier dieselbe Wandlung nach JSON laeuft wie
    im Server, ist kein Zufall: so trifft die Oberflaeche auf beiden Wegen
    genau dieselben Daten, bis aufs Zeichen.

    Zurueck kommt ein Umschlag ``{"status": …, "daten": …}``; der Status
    entspricht dem, was der Server ueber HTTP melden wuerde.
    """
    try:
        rumpf = json.loads(rumpf_json or "{}")
    except json.JSONDecodeError as exc:
        antwort = _fehler(400, f"Ungültiges JSON: {exc}")
    else:
        if not isinstance(rumpf, dict):
            antwort = _fehler(400, "Der Rumpf der Anfrage muss ein Objekt sein.")
        else:
            antwort = bearbeite(name, rumpf)

    return nach_json({"status": antwort.status, "daten": antwort.daten})
