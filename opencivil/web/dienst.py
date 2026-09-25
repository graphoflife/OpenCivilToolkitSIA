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
import math
import traceback
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Mapping

from opencivil import bewehrungssuche
from opencivil.bericht.latex_dokument import als_tex
from opencivil.bericht.markdown import als_markdown
from opencivil.core.rechenwerk import RechenwerkFehler
from opencivil.projekt import Projekt, ProjektFehler
from opencivil.web import api, diagrammdaten, speicher
from opencivil.web.api import endlich

#: Das Gedaechtnis zwischen zwei Anfragen -- siehe :mod:`opencivil.web.speicher`.
#: Im Modul und damit im Prozess: beim Server die laufende Sitzung, im Browser
#: der offene Reiter.
SPEICHER = speicher.Ergebnisspeicher()


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

    gewaehlt = list(rumpf.get("ziele") or [])
    if gewaehlt:
        unbekannt = [z for z in gewaehlt if aufbau.werk.definition(z) is None]
        if unbekannt:
            raise DienstFehler(400, f"Unbekannte Ziele: {', '.join(unbekannt)}")
        # Rueckverfolgung: genau diese Ziele, ohne Zwischenspeicher. Ein
        # Teillauf darf den Speicher weder fuellen noch benutzen -- er rechnet
        # absichtlich nicht alles, und ein halbes Ergebnis als ganzes
        # aufzubewahren waere der Weg zu Zahlen, die niemand erklaeren kann.
        return api.loesung_dict(aufbau.werk.loese(*gewaehlt), aufbau, gewaehlt)

    if not aufbau.alle_ziele():
        # Kein Nachweis vorhanden -- dann wenigstens alle Materialkennwerte.
        return api.loesung_dict(aufbau.werk.loese_alles(), aufbau, ())

    loesung, ziele = _stromabwaerts(projekt, aufbau)
    return api.loesung_dict(loesung, aufbau, ziele)


def _stromabwaerts(projekt: Projekt, aufbau) -> tuple:
    """
    Alles rechnen -- aber nur, was sich geaendert hat.

    Zuerst die Baustoffe: sie stehen am Anfang jeder Herleitung und jede
    Platte braucht sie. Dann Platte fuer Platte, jede in einem eigenen Lauf,
    der die schon bekannten Werte mitbekommt und sie darum weder erneut
    rechnet noch erneut herleitet. Eine Platte, deren Abdruck seit dem letzten
    Mal derselbe ist, wird gar nicht erst angefasst; ihr Beitrag kommt
    fertig aus dem Speicher.

    Die Reihenfolge ist dieselbe wie vorher -- erst die Baustoffe, dann die
    Bauteile in der Reihenfolge der Beschreibung --, und daran haengt der
    Aufbau des Protokolls. Ein Zwischenspeicher, der die Reihenfolge
    verschoebe, aenderte den Bericht, und das waere keine Beschleunigung mehr,
    sondern eine andere Ausgabe.
    """
    kennungen = [q.kennung for q in projekt.querschnitte]
    SPEICHER.aufraeumen(kennungen)

    materialziele = aufbau.materialziele()
    gesamt = aufbau.werk.loese(*materialziele)
    bekannt = dict(gesamt.werte)
    ziele = list(materialziele)

    for kennung, eigene in aufbau.ziele_je_platte():
        if not eigene:
            continue
        ziele += eigene
        stempel = speicher.abdruck(projekt.als_dict(), kennung)
        teil = SPEICHER.hole(kennung, stempel)
        if teil is None:
            lauf = aufbau.werk.loese(*eigene, bekannt=bekannt)
            teil = speicher.als_teil(lauf, aufbau.teile_von(kennung),
                                     ohne=bekannt)
            SPEICHER.merken(kennung, stempel, teil)
        else:
            # Die Nachweise haben sich beim Rechnen mehr gemerkt als ihre
            # Ausgabewerte; die Schnittstelle liest es aus den Objekten. Also
            # wandern die Objekte von damals zurueck in den Aufbau.
            aufbau.teile_setzen(kennung, teil.teile)
        speicher.verschmelzen(gesamt, teil)
        bekannt.update(teil.werte)

    return gesamt, ziele


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


def querkraftkurven(rumpf: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Die M-V-Kurven fuer selbst gewaehlte Normalkraefte.

    Der Querkraftwiderstand haengt ueber ``m_Rd(N_Ed)`` von der Normalkraft ab.
    Unter jedem Diagramm laesst sich eine einstellen; ``n_ed`` bildet die
    Kennung der Kurve auf diese Normalkraft in kN ab.

    Eine eigene Anfrage, weil es eine eigene Frage ist -- und weil die
    Oberflaeche die Formel sonst ein zweites Mal enthalten muesste, um die
    Kurve selbst zu zeichnen. Gerechnet wird an genau einer Stelle.
    """
    aufbau = _projekt(rumpf).aufbauen()
    aufbau.werk.loese(*aufbau.alle_nachweisziele(), ohne_herleitung=True)

    gewaehlt = {}
    for kennung, wert in (rumpf.get("n_ed") or {}).items():
        if wert is None or wert == "":
            continue
        try:
            gewaehlt[str(kennung)] = float(wert)
        except (TypeError, ValueError):
            # Nicht durchreichen: ein roher ValueError kaeme als Absturz beim
            # Benutzer an. Die Anfrage kommt zwar aus der eigenen Oberflaeche,
            # aber das ist keine Zusicherung -- sie steht offen im Netz.
            raise DienstFehler(
                400, f"Die Normalkraft der Kurve '{kennung}' ist keine Zahl, "
                     f"sondern {wert!r}.")

    return {"querkraftkurven": diagrammdaten.querkraftkurven(aufbau, gewaehlt)}


def bericht(rumpf: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Baut den Bericht als LaTeX-Dokument und als Markdown, beide als
    Zeichenkette.

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

    untertitel = "OpenCivilToolkitSIA – Berechnung nach SIA 262:2025"
    return {
        "tex": als_tex(loesung, titel=projekt.name, untertitel=untertitel,
                       aufbau=aufbau),
        "markdown": als_markdown(loesung, titel=projekt.name,
                                 untertitel=untertitel, aufbau=aufbau),
        "dateiname": dateiname(projekt.name),
    }


def dateiname(name: str) -> str:
    """Macht aus einem Projektnamen einen brauchbaren Dateinamen."""
    gesaeubert = "".join(z if z.isalnum() or z in "-_" else "_" for z in name)
    return gesaeubert.strip("_") or "bericht"


#: Name der Anfrage -> Funktion. Diese Namen sind der ganze Vertrag zwischen
def bewehrung_suchen(rumpf: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Sucht zu einer Platte die kleinste Bewehrung und gibt sie zurueck.

    Gerechnet, nicht gesetzt: zurueck kommt das gefundene Projekt, und ob die
    Oberflaeche es uebernimmt, entscheidet sie. So bleibt der Knopf ein
    einzelner Schritt, den man sieht und rueckgaengig machen kann -- und
    nicht eine Bewehrung, die sich bei jeder Eingabe im Hintergrund aendert.
    """
    projekt = _projekt(rumpf)
    kennung = rumpf.get("kennung")
    if not kennung:
        raise DienstFehler(400, "Es fehlt die Kennung der Platte.")
    try:
        projekt.querschnitt(kennung)
    except Exception:
        raise DienstFehler(404, f"Keine Platte mit der Kennung '{kennung}'.") from None

    eintrag = projekt.querschnitt(kennung)
    modus = rumpf.get("modus") or eintrag.automatik_modus
    teilungen = rumpf.get("teilungen") or eintrag.automatik_teilungen
    try:
        modus = bewehrungssuche.Suchmodus(modus)
    except ValueError:
        moeglich = ", ".join(m.value for m in bewehrungssuche.Suchmodus)
        raise DienstFehler(400, f"Unbekannter Suchmodus '{modus}'. "
                                f"Möglich sind: {moeglich}.") from None

    ergebnis = bewehrungssuche.suche(
        projekt, kennung, modus=modus, teilungen=teilungen,
        mindestdurchmesser=(rumpf.get("mindestdurchmesser")
                            or eintrag.automatik_mindestdurchmesser))
    antwort: Dict[str, Any] = {
        "gefunden": ergebnis.gefunden,
        "modus": modus.value,
        "modus_text": modus.beschriftung,
        "begruendung": ergebnis.begruendung,
        # Gesucht wird ohne Duktilitaet -- sie wird durch mehr Stahl
        # schlechter. Verschwiegen wird sie darum nicht.
        "duktilitaet": ergebnis.duktilitaet,
        "loesungen": [
            {"teilung": l.teilung, "gefunden": l.gefunden,
             "durchmesser": l.durchmesser, "stahlflaeche": l.stahlflaeche,
             "schlechtester": (l.schlechtester
                               if math.isfinite(l.schlechtester) else None),
             "nachweis": l.nachweis, "begruendung": l.begruendung,
             "runden": len(l.schritte)}
            for l in ergebnis.loesungen
        ],
    }
    if ergebnis.beste:
        bewehrungssuche.uebernehmen(projekt, kennung, ergebnis.beste)

    # Die Buegel erst danach: sie haengen an der Laengsbewehrung, weil die
    # statische Hoehe in den Querkraftwiderstand eingeht.
    if eintrag.automatik_querkraft:
        buegel = bewehrungssuche.buegel_suchen(
            projekt, kennung,
            teilungen=(rumpf.get("querkraft_teilungen")
                       or eintrag.automatik_querkraft_teilungen))
        antwort["buegel"] = {
            "gefunden": buegel.gefunden, "durchmesser": buegel.durchmesser,
            "teilung": buegel.teilung, "begruendung": buegel.begruendung,
        }
        if buegel.gefunden:
            bewehrungssuche.buegel_uebernehmen(projekt, kennung, buegel)

    antwort["projekt"] = projekt.als_dict()
    return antwort


#: Oberflaeche und Kern; beide Huellen reichen sie unveraendert durch.
ANFRAGEN: Dict[str, Callable[[Mapping[str, Any]], Dict[str, Any]]] = {
    "katalog": katalog,
    "beispiel": beispiel,
    "pruefen": pruefen,
    "rechnen": rechnen,
    "alles": alles,
    "ziele": ziele,
    "querkraftkurven": querkraftkurven,
    "bericht": bericht,
    "bewehrung_suchen": bewehrung_suchen,
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
