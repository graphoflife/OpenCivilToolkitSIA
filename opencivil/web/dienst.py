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

from opencivil import bewehrungssuche
from opencivil.bericht.latex_dokument import als_tex
from opencivil.bericht.markdown import als_markdown
from opencivil.core.rechenwerk import Loesung, RechenwerkFehler
from opencivil.projekt import (
    DeckeEintrag, FachwerkmodellEintrag, Mappe, MauerwerkEintrag, Projekt, ProjektFehler,
)
from opencivil.projekt.blechdecken import BlechdeckeEintrag
from opencivil.projekt.lesen import inhalt_pruefen
from opencivil.projekt.mappe import projekt_aus_datei
from opencivil.projekt.staebe import MitStaeben
from opencivil.querschnitt import profilblech, vorlagen
from opencivil.querschnitt.widerstandsflaeche import GROESSEN
from opencivil.stahlprofile import lage as profillage
from opencivil.web import (
    api, balkendaten, deckendaten, diagrammdaten, fachwerkdaten, mauerwerkdaten, speicher,
    zeichengeometrie,
)
from opencivil.web.umschlag import endlich, fehlerdaten, umschlag
from opencivil.web.zeichendaten import ZEICHENDATEN

#: Das Gedaechtnis zwischen zwei Anfragen -- siehe :mod:`opencivil.web.speicher`.
#: Im Modul und damit im Prozess: beim Server die laufende Sitzung, im Browser
#: der offene Reiter.
SPEICHER: speicher.Ergebnisspeicher[Loesung] = speicher.Ergebnisspeicher()

#: Dasselbe fuer die Zeichendaten der Spannung-Dehnung-Analysen, je Bauteil
#: unter demselben Abdruck wie seine Loesung (:func:`_analysen`).
ANALYSEN: speicher.Ergebnisspeicher[list] = speicher.Ergebnisspeicher()

#: Und fuer die Diagramme einer Querschnittsanalyse, unter ihrem Abdruck und
#: dem Schnitt (:func:`analysediagramme`). Die Oberflaeche fragt nach jeder
#: Aenderung am Projekt neu, gleich wo; ob sich fuer diese Analyse etwas
#: geaendert hat, entscheidet erst der Abdruck hier.
DIAGRAMME: speicher.Ergebnisspeicher[dict] = speicher.Ergebnisspeicher()


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
    """Das Beispielprojekt, mit dem eine leere Oberflaeche startet -- mit den Sandboxen."""
    projekt = Projekt.beispiel()
    projekt.sandboxen_anlegen()
    return projekt.als_dict()


def pruefen(rumpf: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Prueft ein Projekt, wie es in einer Datei steht, und gibt es aufgeraeumt
    zurueck (:func:`~opencivil.projekt.mappe.projekt_aus_datei`).
    """
    return {"projekt": projekt_aus_datei(rumpf.get("projekt")).als_dict()}


def mappe_oeffnen(rumpf: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Eine Mappe, wie die Oberflaeche sie zeigt -- die Projekte, die sie im
    Browser ablegt, speichert und oeffnet: geprueft, aufgeraeumt und in jedem
    Projekt mit allen Sandboxen. Mit ``frisch`` beginnt jede Sandbox neu, wie
    beim Laden der Seite; sonst stehen sie da, wie gespeichert (Benutzer,
    2026-11-20). Eine Datei mit einem einzelnen Projekt, wie bis 2026-11-20
    gespeichert, kommt als Mappe mit diesem einen zurueck
    (:meth:`~opencivil.projekt.mappe.Mappe.aus_dict`).
    """
    mappe = Mappe.aus_dict(rumpf.get("mappe"))
    for projekt in mappe.projekte:
        projekt.sandboxen_anlegen(frisch=bool(rumpf.get("frisch")))
    return {"mappe": mappe.als_dict()}


def sandbox_zuruecksetzen(rumpf: Mapping[str, Any]) -> Dict[str, Any]:
    """
    ↺ an der Sandbox einer App: ``{projekt, liste}`` hinein, die frische
    Sandbox hinaus -- mit ihrer Kennung, an ihrem Platz
    (:meth:`~opencivil.projekt.projekt.Projekt.sandbox_zuruecksetzen`).
    """
    projekt = _projekt(rumpf)
    return {"eintrag": projekt.sandbox_zuruecksetzen(str(rumpf.get("liste") or "")).als_dict()}


def rechnen(rumpf: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Rechnet ein Projekt durch.

    Ohne ``ziele`` wird alles gerechnet, was die Nachweise brauchen. Mit
    ``ziele`` genau diese -- dann loest das Rechenwerk rueckwaerts auf und
    meldet, welche Eingabe fehlt; ``kurzform`` sind dann ihre Formeln in
    zwei, drei Zeilen (:mod:`opencivil.core.kurzform`).
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
        # Dazu die Kurzform: das Auge zeigt sie ueber der Herleitung.
        loesung = aufbau.werk.loese(*gewaehlt)
        return {**api.loesung_dict(loesung, aufbau),
                "kurzform": api.kurzform_liste(loesung.protokoll, gewaehlt)}

    beschreibung = projekt.als_dict()
    if not aufbau.alle_ziele():
        # Kein Nachweis vorhanden -- dann wenigstens alle Materialkennwerte.
        loesung = aufbau.werk.loese_alles()
    else:
        loesung = _stromabwaerts(projekt, aufbau, beschreibung)
    analysen = _analysen(projekt, beschreibung, aufbau, loesung)
    return {**api.loesung_dict(loesung, aufbau, spannungsanalysen=analysen),
            "obergrenzen": api.obergrenzen(projekt)}


def _stromabwaerts(projekt: Projekt, aufbau, beschreibung: Mapping[str, Any]) -> Loesung:
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
    SPEICHER.aufraeumen(projekt.name, [e.kennung for e in projekt.bauteile()])

    materialziele = aufbau.materialziele()
    gesamt = aufbau.werk.loese(*materialziele)
    bekannt = dict(gesamt.werte)

    for kennung, eigene in aufbau.ziele_je_bauteil():
        if not eigene:
            continue
        stempel = _abdruck(projekt, beschreibung, aufbau, kennung)
        teil = SPEICHER.hole(projekt.name, kennung, stempel)
        if teil is None:
            teil = aufbau.werk.loese(*eigene, bekannt=bekannt)
            SPEICHER.merken(projekt.name, kennung, stempel, teil)
        gesamt.anhaengen(teil)
        bekannt.update(teil.werte)
    return gesamt


def _analysen(projekt: Projekt, beschreibung: Mapping[str, Any], aufbau,
              loesung: Loesung) -> Dict[str, list]:
    """
    Die Zeichendaten der Spannung-Dehnung-Analysen, je Bauteil -- aus dem
    Speicher, solange sein Abdruck derselbe ist wie bei seiner Loesung: eine
    Analyse liest nur den Eintrag ihres Bauteils, die Materialien und die
    Werte, die daraus folgen. Gerechnet werden nur die uebrigen, in einem
    Lauf. Bis 2026-10-18 rechnete jede Rechnung alle Analysen neu, auch die
    unveraenderter Bauteile -- am Pruefprojekt «jeder Nachweis» zwei Drittel
    jeder Rechnung.
    """
    ANALYSEN.aufraeumen(projekt.name, aufbau.spannungsfaelle)
    stempel = {k: _abdruck(projekt, beschreibung, aufbau, k) for k in aufbau.spannungsfaelle}
    daten = {k: ANALYSEN.hole(projekt.name, k, s) for k, s in stempel.items()}
    neu = diagrammdaten.spannungsanalysen(
        aufbau, loesung, nur={k for k, d in daten.items() if d is None})
    for kennung, d in neu.items():
        ANALYSEN.merken(projekt.name, kennung, stempel[kennung], d)
    return {**daten, **neu}


def _abdruck(projekt: Projekt, beschreibung: Mapping[str, Any], aufbau, kennung: str) -> str:
    """
    Der Fingerabdruck eines Bauteils -- mit den Bauteilen, deren Werte es
    liest, auch ueber mehrere Stufen (:meth:`~opencivil.projekt.projekt.Projekt.bezuege_von`).
    ``beschreibung`` ist ``projekt.als_dict()``, einmal gebildet. Einem
    Bauteil, dem noch etwas fehlt, sagt der Fehler, was (:meth:`Aufbau.bauteil`).
    """
    aufbau.bauteil(kennung)
    return speicher.abdruck(beschreibung, kennung, projekt.bezuege_von(kennung))


def _bauteil_rechnen(projekt: Projekt, aufbau, kennung: str) -> Loesung:
    """
    Ein Bauteil gerechnet: aus dem Zwischenspeicher, wenn er es zu genau
    dieser Beschreibung noch hat -- nach einer Rechnung ist das der Fall --,
    sonst dieses eine, ohne Herleitung: wer hier fragt, will Werte und
    Bilder, und die Zeichnung fragt nach jeder Eingabe.
    """
    teil = SPEICHER.hole(projekt.name, kennung,
                         _abdruck(projekt, projekt.als_dict(), aufbau, kennung))
    if teil is None:
        return aufbau.werk.loese(*aufbau.materialziele(), *aufbau.ziele_von(kennung), ohne_herleitung=True)
    return teil


def bericht(rumpf: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Baut den Bericht als LaTeX-Dokument und als Markdown, beide als
    Zeichenkette.

    Geschrieben wird hier nichts. Der Browser macht daraus einen Download, der
    Server legt es zusaetzlich in ``ausgabe/`` ab und versucht die Uebersetzung
    zu PDF -- das ``.tex`` ist auf beiden Wegen dasselbe.

    Mit ``nur``, der Kennung eines Bauteils, steht nur dieses darin, mit den
    Materialien (:meth:`~opencivil.projekt.projekt.Projekt.nur`) -- auch eine
    Sandbox: wer nach ihr fragt, meint sie. So holt der MCP-Zugang die
    Herleitung eines Eintrags.
    """
    projekt = _projekt(rumpf)
    nur = str(rumpf.get("nur") or "")
    # Sonst ohne die Sandboxen: sie sind zum Ausprobieren da (Benutzer, 2026-11-20).
    projekt = projekt.nur(nur) if nur else projekt.ohne_sandboxen()
    aufbau = projekt.aufbauen()
    gewuenscht = aufbau.berichtsziele()
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


def bewehrung_suchen(rumpf: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Sucht zu einer Platte die kleinste Bewehrung und gibt sie zurueck -- mit
    «Plattendicke optimieren» auch die duennste Platte dazu.

    Gerechnet, nicht gesetzt: zurueck kommt das gefundene Projekt, und ob die
    Oberflaeche es uebernimmt, entscheidet sie. So bleibt der Knopf ein
    einzelner Schritt, den man sieht und rueckgaengig machen kann -- und
    nicht eine Bewehrung, die sich bei jeder Eingabe im Hintergrund aendert.

    Wie gesucht wird, steht an der Platte und nur dort. Frueher liess sich
    jede Einstellung mit dem Rumpf uebersteuern, per ``rumpf.get(...) or
    eintrag...`` -- und das ``or`` las eine Null als «nicht angegeben»: ein
    Mindestdurchmesser 0, also «kein Minimum», wurde still zur Vorgabe der
    Platte. Zwei Quellen fuer dieselbe Zahl, und die Oberflaeche benutzte die
    zweite ohnehin nie.
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
    # Der Modus ist beim Lesen geprueft. Die Teilungen prueft ihr Feld, vor
    # jeder Suche (:func:`~opencivil.bewehrungssuche.bewertung.vorab_pruefen`);
    # bis 2026-11-20 tat es hier ein zweites Mal ein eigener Satz.
    modus = eintrag.automatik_modus

    wie = {"teilungen": eintrag.automatik_teilungen,
           "mindestdurchmesser": eintrag.automatik_mindestdurchmesser}
    # Mit «Bügel mitsuchen» tragen die Querkraft die Buegel, die die
    # Buegelsuche danach findet: die Laengssuche prueft sie nicht (Benutzer,
    # 2026-11-19), auch ohne Buegel nicht -- sonst hinge ihr Ergebnis daran,
    # ob vorher welche lagen. Bis dahin scheiterte sie bei V_Ed = 400 kN/m an
    # der Querkraft, mit den alten Buegeln ⌀10@200 wie ohne, und erst ein
    # zweiter Klick fand die Laengsbewehrung zu den neuen.
    laengs = projekt
    if eintrag.automatik_querkraft:
        laengs = projekt.nur(kennung)
        laengs.querschnitt(kennung).ohne_querkraft()
    dicke = None
    if eintrag.automatik_dicke:
        dicke = bewehrungssuche.dicke_suchen(laengs, kennung, modus=modus, **wie)
        ergebnis = dicke.suche or bewehrungssuche.Suchergebnis(modus=modus)
    else:
        ergebnis = bewehrungssuche.suche(laengs, kennung, modus=modus, **wie)
    # Nur, was jemand liest: die Oberflaeche nimmt gefunden, Begruendung,
    # Duktilitaet, Buegel, Dicke und das fertige Projekt.
    antwort: Dict[str, Any] = {
        "gefunden": ergebnis.gefunden and (dicke is None or dicke.gefunden),
        "begruendung": (dicke or ergebnis).begruendung,
        # Gesucht wird ohne Duktilitaet -- sie wird durch mehr Stahl
        # schlechter. Verschwiegen wird sie darum nicht; ``None``: nichts
        # zu sagen.
        "duktilitaet": ergebnis.duktilitaet,
        "duktilitaet_erfuellt": ergebnis.duktilitaet_erfuellt,
    }
    if dicke is not None:
        antwort["dicke"] = {
            "h": dicke.h,
            "versuche": [{"h": v.h, "geht": v.geht} for v in dicke.versuche],
        }
    if antwort["gefunden"]:
        if dicke is not None:
            eintrag.h = dicke.h
        bewehrungssuche.uebernehmen(projekt, kennung, ergebnis.beste)

    # Die Buegel erst danach, gegen die Querkraft: sie haengen an der
    # Laengsbewehrung, weil die statische Hoehe in den Querkraftwiderstand
    # eingeht.
    if eintrag.automatik_querkraft:
        buegel = bewehrungssuche.buegel_suchen(
            projekt, kennung, teilungen=eintrag.automatik_querkraft_teilungen)
        antwort["buegel"] = {
            "gefunden": buegel.gefunden, "durchmesser": buegel.durchmesser,
            "teilung": buegel.teilung, "begruendung": buegel.begruendung,
        }
        if buegel.gefunden:
            bewehrungssuche.buegel_uebernehmen(projekt, kennung, buegel)

    antwort["projekt"] = projekt.als_dict()
    return antwort


def verweise(rumpf: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Wer auf einen Eintrag zeigt: ``{projekt, kennung}`` hinein, die Bauteile
    mit Kennung und Name hinaus (:meth:`~opencivil.projekt.projekt.Projekt.verweise`).
    Die Oberflaeche fragt, bevor sie ein Material oder Bauteil loescht --
    eine eigene Liste dort kannte den Buegelstahl nicht.
    """
    projekt = _projekt(rumpf)
    kennung = rumpf.get("kennung")
    if not isinstance(kennung, str) or not kennung:
        raise DienstFehler(400, "Es fehlt die Kennung des Eintrags.")
    return {"verweise": [{"kennung": e.kennung, "name": e.name}
                         for e in projekt.verweise(kennung)]}


def fallname(rumpf: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Ob ein Fall so heissen darf: ``{projekt, kennung, pfad, index, name}``
    hinein -- das Bauteil, die Liste darin (``knickfaelle``,
    ``verformung.faelle``), der Fall und der neue Name --, ``{grund}`` hinaus,
    leer, wenn er darf. Das Namensfeld fragt, bevor es einen Namen
    uebernimmt; die Regel ist dieselbe wie vor dem Rechnen
    (:mod:`~opencivil.projekt.fallnamen`).
    """
    bauteil = _projekt(rumpf).bauteil(str(rumpf.get("kennung") or ""))
    pfad, index, name = rumpf.get("pfad"), rumpf.get("index"), rumpf.get("name")
    if not isinstance(index, int) or not isinstance(name, str):
        raise DienstFehler(400, "Es fehlen der Fall und sein neuer Name.")
    for liste in bauteil.fallnamen():
        if liste.pfad == pfad and 0 <= index < len(liste.namen):
            return {"grund": liste.grund(index, name)}
    raise DienstFehler(400, f"Einen Fall {index + 1} unter '{pfad}' hat {bauteil.name} nicht.")


def geometrie(rumpf: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Was das Zeichenfenster einer Querschnittsanalyse zeigt -- ohne Nachweise.

    Stablagen und tatsaechliche Teilungen, Schwerpunkt, Zellen der
    Schubwaende und jede Meldung zur Zeichnung, am Element, das sie betrifft.
    Schnell genug fuer jede Aenderung: gerechnet wird nur Geometrie.
    """
    projekt = _projekt(rumpf)
    return zeichengeometrie.geometrie(
        projekt.querschnittsanalyse(str(rumpf.get("kennung") or "")), projekt)


def analysediagramme(rumpf: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Die Diagramme einer Querschnittsanalyse -- erst, wenn jemand sie sehen will.

    Die M_y-M_z-Kurven brauchen je Lastfall siebzig Bruchzustaende, die kein
    Nachweis braucht. Mit jeder Rechnung mitgeliefert, machten sie jede
    Eingabe langsamer, auch bei geschlossenem Reiter. Darum eine eigene
    Anfrage, wie die M-V-Kurven.

    Die Nachweise selbst rechnen nicht noch einmal, wenn der Zwischenspeicher
    sie zu genau dieser Beschreibung noch hat -- nach einer Rechnung ist das
    der Fall. Sonst wird das eine Bauteil gerechnet. Die Diagramme selbst
    kommen aus :data:`DIAGRAMME`, solange Abdruck und Schnitt dieselben sind.
    """
    projekt = _projekt(rumpf)
    kennung = str(rumpf.get("kennung") or "")
    projekt.querschnittsanalyse(kennung)   # ob es sie gibt
    # Wo das Interaktionsdiagramm schneidet: welche Groesse fest ist und mit
    # welchem Wert, in kN bzw. kNm. Ohne Angabe bei M_z = 0.
    wahl = rumpf.get("schnitt") or {}
    fest = str(wahl.get("fest") or "M_z")
    if fest not in GROESSEN:
        raise DienstFehler(400, f"Geschnitten wird bei {', '.join(GROESSEN)}, nicht bei '{fest}'.")
    try:
        wert = float(wahl.get("wert") or 0.0)
    except (TypeError, ValueError):
        raise DienstFehler(400, f"Der Wert des Schnitts ist keine Zahl: {wahl.get('wert')!r}.") from None
    aufbau = projekt.aufbauen()
    # Einer unfertigen Analyse sagt schon der Abdruck, was fehlt (Aufbau.bauteil).
    stempel = f"{_abdruck(projekt, projekt.als_dict(), aufbau, kennung)}|{fest}|{wert!r}"
    daten = DIAGRAMME.hole(projekt.name, kennung, stempel)
    if daten is None:
        loesung = _bauteil_rechnen(projekt, aufbau, kennung)
        daten = endlich(diagrammdaten.analyse(aufbau, loesung, kennung, (fest, wert)))
        DIAGRAMME.merken(projekt.name, kennung, stempel, daten)
    return {"diagramme": daten}


def _balkensystem(projekt: Projekt, rumpf: Mapping[str, Any]) -> MitStaeben:
    """Ein Balkensystem, eben oder im Raum -- beide bedienen dieselben Anfragen."""
    kennung = str(rumpf.get("kennung") or "")
    eintrag = projekt.bauteil(kennung)
    if not isinstance(eintrag, MitStaeben):
        raise DienstFehler(400, f"'{kennung}' ist kein Balkensystem.")
    return eintrag


def balkensystem_verlauf(rumpf: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Die Bilder eines Balkensystems in einem Fall: je Stab die
    Schnittgroessen und die Verschiebung, je Knoten seine Verschiebung. Eine eigene Anfrage wie die
    Diagramme der Querschnittsanalyse -- gross, und nur gebraucht, wenn
    jemand hinsieht. Gerechnet wird aus dem Zwischenspeicher, wenn er das
    System zu dieser Beschreibung noch hat.

    Ein System, das sich nicht rechnen laesst, ist keine falsche Anfrage:
    dann ist ``verlauf`` leer, und die Uebersicht sagt warum. Ohne ``fall``
    kommen nur die Zeichendaten des Systems (:mod:`opencivil.web.zeichendaten`)
    -- was das Zeichenfenster nach jeder Aenderung braucht: Meldungen, Knoten
    ohne Drehsteifigkeit, was sich bewegt, die Achsen der Linien.
    """
    projekt = _projekt(rumpf)
    eintrag = _balkensystem(projekt, rumpf)
    aufbau = projekt.aufbauen()
    teil = aufbau.bauteil(eintrag.kennung)
    loesung = _bauteil_rechnen(projekt, aufbau, eintrag.kennung)
    daten = endlich(ZEICHENDATEN[teil.art.name](aufbau, eintrag.kennung, loesung))
    befund = loesung.befunde.get(teil.objekt.rechnung.id)
    fall = str(rumpf.get("fall") or "")
    gerechnet = balkendaten.faelle(befund)
    if not fall or not gerechnet:
        return {"verlauf": None, **daten}
    if fall not in gerechnet:
        raise DienstFehler(400, f"Einen Fall «{fall}» gibt es in «{eintrag.name}» nicht. "
                                f"Gerechnet sind: {', '.join(gerechnet)}.")
    return {"verlauf": endlich(balkendaten.verlauf(befund, fall)), **daten}


def _decke(projekt: Projekt, rumpf: Mapping[str, Any]) -> DeckeEintrag:
    kennung = str(rumpf.get("kennung") or "")
    eintrag = projekt.bauteil(kennung)
    if not isinstance(eintrag, DeckeEintrag):
        raise DienstFehler(400, f"'{kennung}' ist keine Decke.")
    return eintrag


def decke_zeichnung(rumpf: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Was das Zeichenfenster einer Decke unter ihre Teile legt -- die Streifen,
    wie die Last auf die Richtungen geht, die Meldungen
    (:func:`deckendaten.uebersicht`). Eine eigene Anfrage wie die Uebersicht
    des Balkensystems: gebraucht nach jeder Aenderung, ohne auf die Rechnung
    des ganzen Projekts zu warten. Gerechnet wird die eine Decke, aus dem
    Zwischenspeicher, wenn er sie zu dieser Beschreibung noch hat.
    """
    projekt = _projekt(rumpf)
    kennung = _decke(projekt, rumpf).kennung
    aufbau = projekt.aufbauen()
    loesung = _bauteil_rechnen(projekt, aufbau, kennung)
    return {"uebersicht": endlich(deckendaten.zeichnung(aufbau, kennung, loesung))}


def fachwerk_zeichnung(rumpf: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Was das Zeichenfenster eines Fachwerkmodells unter seine Teile legt --
    seine Meldungen (:func:`fachwerkdaten.uebersicht`). Wie bei der Decke
    eine eigene Anfrage, gebraucht nach jeder Aenderung; gerechnet wird das
    eine Modell, aus dem Zwischenspeicher, wenn er es zu dieser
    Beschreibung noch hat.
    """
    projekt = _projekt(rumpf)
    kennung = _fachwerkmodell(projekt, rumpf).kennung
    aufbau = projekt.aufbauen()
    loesung = _bauteil_rechnen(projekt, aufbau, kennung)
    return {"uebersicht": endlich(fachwerkdaten.zeichnung(aufbau, kennung, loesung))}


def fachwerk_suchen(rumpf: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Eine Runde der Suche nach einem Fachwerk (:func:`fachwerkdaten.suchen`):
    der Zustand der letzten Runde hinein, der naechste, das Fachwerk und der
    Stand heraus -- gleich fuer Server und Pyodide. Die Seite fragt Runde um
    Runde an, bis die Suche fertig ist oder jemand anhaelt; sie rechnet
    dabei nichts. Ohne ``zustand`` beginnt die Suche von vorn, ebenso, wenn
    er zu einem anderen Stand des Modells gehoert. Mit ``abschliessen``
    liest das Verfahren SIMP sein Fachwerk aus der Form, wie sie ist.
    """
    projekt = _projekt(rumpf)
    return endlich(fachwerkdaten.suchen(_fachwerkmodell(projekt, rumpf), rumpf.get("zustand"),
                                        bool(rumpf.get("abschliessen"))))


def _fachwerkmodell(projekt: Projekt, rumpf: Mapping[str, Any]) -> FachwerkmodellEintrag:
    """Das Fachwerkmodell, das ``kennung`` nennt -- sonst ist die Anfrage falsch."""
    kennung = str(rumpf.get("kennung") or "")
    eintrag = projekt.bauteil(kennung)
    if not isinstance(eintrag, FachwerkmodellEintrag):
        raise DienstFehler(400, f"'{kennung}' ist kein Fachwerkmodell.")
    return eintrag


def mauerwerk_zeichnung(rumpf: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Was das Zeichenfenster einer Wand aus Mauerwerk unter ihre Teile legt --
    Meldungen, Pfeiler, Stuerze (:func:`mauerwerkdaten.uebersicht`). Wie beim
    Fachwerkmodell eine eigene Anfrage nach jeder Aenderung. Fehlt der Wand
    noch etwas, das sie gar nicht rechnen laesst -- ihr Mauerwerk --, sagt es
    eine graue Meldung unter der Zeichnung (:func:`mauerwerkdaten.unfertig`).
    """
    projekt = _projekt(rumpf)
    eintrag = projekt.bauteil(str(rumpf.get("kennung") or ""))
    if not isinstance(eintrag, MauerwerkEintrag):
        raise DienstFehler(400, f"'{eintrag.kennung}' ist kein Mauerwerk.")
    aufbau = projekt.aufbauen()
    unfertig = aufbau.unfertige.get(eintrag.kennung)
    if unfertig is not None:
        return {"uebersicht": mauerwerkdaten.unfertig(unfertig.grund)}
    loesung = _bauteil_rechnen(projekt, aufbau, eintrag.kennung)
    return {"uebersicht": endlich(mauerwerkdaten.zeichnung(aufbau, eintrag.kennung, loesung))}


def decke_ergebnis(rumpf: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Die Bilder einer Decke in einem Fall: Momente und Querkraefte in Zellen,
    ihre groessten Werte, die Kraefte der Lager und die Verlaeufe laengs der
    Schnitte (:func:`deckendaten.ergebnis`).
    Eine eigene Anfrage wie der Verlauf des Balkensystems -- gross, und nur
    gebraucht, wenn jemand hinsieht.

    Eine Decke, die sich nicht rechnen laesst, ist keine falsche Anfrage:
    dann ist ``ergebnis`` leer, und die Uebersicht sagt warum.
    """
    projekt = _projekt(rumpf)
    decke = _decke(projekt, rumpf)
    kennung = decke.kennung
    aufbau = projekt.aufbauen()
    loesung = _bauteil_rechnen(projekt, aufbau, kennung)
    befund = loesung.befunde.get(aufbau.decken[kennung].rechnung.id)
    uebersicht = endlich(deckendaten.uebersicht(befund))
    fall = str(rumpf.get("fall") or "")
    gerechnet = deckendaten.faelle(befund)
    if not fall or not gerechnet:
        return {"ergebnis": None, "uebersicht": uebersicht}
    if fall not in gerechnet:
        raise DienstFehler(400, f"Einen Fall «{fall}» gibt es in «{projekt.bauteil(kennung).name}» "
                                f"nicht. Gerechnet sind: {', '.join(gerechnet)}.")
    return {"ergebnis": endlich(deckendaten.ergebnis(befund, fall, decke.schnittlinien())),
            "uebersicht": uebersicht}


def balkensystem_bearbeiten(rumpf: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Teilt eine Linie oder kehrt Linien um -- im Kern, weil dabei Lastwerte
    entstehen: der Wert einer Trapezlast am Schnitt, gespiegelte Stellen.
    Zurueck kommt das ganze System und die Kennung einer neuen Linie; die
    Oberflaeche uebernimmt es in einem Schritt, den man rueckgaengig machen
    kann.

    ``teilen``: ``linie`` und die Stelle -- ``stelle`` in m ab dem Anfang,
    ein ``anteil`` der Laenge (0.5: in der Mitte) oder ein ``punkt`` mit
    einer Koordinate je Achse -- [x, z] in der Ebene, [x, y, z] im Raum --,
    der auf die Linie gelotet wird.
    ``umkehren``: ``linien``, eine oder mehrere.
    """
    projekt = _projekt(rumpf)
    eintrag = _balkensystem(projekt, rumpf)
    aktion = str(rumpf.get("aktion") or "")
    neu = []
    try:
        if aktion == "teilen":
            linie = str(rumpf.get("linie") or "")
            if rumpf.get("punkt") is not None:
                punkt = tuple(float(c) for c in rumpf["punkt"])
                if len(punkt) != len(eintrag.ACHSEN):
                    raise ValueError
                stelle = eintrag.stelle_auf(linie, punkt)
            elif rumpf.get("anteil") is not None:
                stelle = float(rumpf["anteil"]) * eintrag.laenge(eintrag.linie_von(linie))
            else:
                stelle = float(rumpf.get("stelle"))
            neu.append(eintrag.teilen(linie, stelle).kennung)
        elif aktion == "umkehren":
            for linie in rumpf.get("linien") or []:
                eintrag.umkehren(str(linie))
        else:
            raise DienstFehler(400, f"Ein Balkensystem lässt sich «teilen» oder «umkehren», "
                                    f"nicht «{aktion}».")
    except (TypeError, ValueError, IndexError):
        raise DienstFehler(400, f"Die Stelle zum Teilen muss eine Zahl sein oder ein Punkt "
                                f"mit {len(eintrag.ACHSEN)} Zahlen.") from None
    return {"balkensystem": eintrag.als_dict(), "neu": neu}


def _vorlagenwahl(rumpf: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Was die Oberflaeche zu einer Vorlage eingestellt hat: die Masse -- auch
    Ueberdeckung, Lagen und Buegel -- und die zwei Schalter.
    """
    wahl = rumpf.get("wahl") or {}
    try:
        masse = {str(k): float(v) for k, v in (wahl.get("masse") or {}).items()
                 if v is not None and v != ""}
    except (TypeError, ValueError):
        raise DienstFehler(400, "Die Masse einer Vorlage müssen Zahlen sein.") from None
    return {"masse": masse, "bewehrung": bool(wahl.get("bewehrung", True)),
            "schubwaende": bool(wahl.get("schubwaende", True))}


def _vorlage(rumpf: Mapping[str, Any]) -> vorlagen.Vorlage:
    try:
        return vorlagen.vorlage(str((rumpf.get("wahl") or {}).get("art") or ""))
    except ValueError as fehler:
        raise DienstFehler(400, str(fehler)) from None


def vorlage(rumpf: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Die Teile einer Vorlage zu den eingestellten Massen -- fuer die Skizze,
    waehrend man tippt. Passen die Masse nicht zueinander, steht der Grund in
    ``fehler`` und es gibt keine Teile: das ist keine falsche Anfrage, nur
    eine unfertige Eingabe. Beim Stahlprofil das Profil (:func:`_profilskizze`),
    bei der Blechverbunddecke die Decke (:func:`_deckenskizze`).
    """
    wahl = rumpf.get("wahl") or {}
    if wahl.get("art") == profillage.VORLAGE:
        return _profilskizze(wahl)
    if wahl.get("art") == profilblech.VORLAGE:
        return _deckenskizze(wahl)
    try:
        teile = _vorlage(rumpf).bauen(**_vorlagenwahl(rumpf))
    except ValueError as fehler:
        return {"fehler": str(fehler), "teile": None}
    return {"fehler": None, "teile": teile.als_dict()}


def _profilskizze(wahl: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Die Skizze eines Stahlprofils, gedreht und gespiegelt, mit seinen zwei
    Massen von aussen -- und ob Drehen und Spiegeln es aendern: sonst zeigt
    das Fenster die Schalter dafuer nicht. Eingesetzt wird es von der
    Oberflaeche, wie jedes Element eines Werkzeugs: es ist ein Eintrag an
    einem Knoten.
    """
    name = str(wahl.get("profil") or "")
    drehung = wahl.get("drehung", 0)
    if drehung not in profillage.DREHUNGEN:
        raise DienstFehler(400, f"Ein Profil dreht sich um "
                                f"{', '.join(map(str, profillage.DREHUNGEN))} Grad.")
    try:
        teile = profillage.skizze(name, drehung, bool(wahl.get("gespiegelt")))
    except KeyError as grund:
        return {"fehler": grund.args[0], "teile": None}
    return {"fehler": None, "teile": teile.als_dict(), "drehbar": profillage.drehbar(name),
            "spiegelbar": profillage.spiegelbar(name)}


#: Was die Skizze einer Blechverbunddecke von ihrer Wahl liest: ihre Masse.
BLECHMASSE = ("h", "rippen", "h_p", "b_s", "b_o", "b_u", "A_p")


def _deckenskizze(wahl: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Die Skizze einer Blechverbunddecke zu den eingestellten Massen: die ganze
    Decke in ``teile``, eine Rippe mit ihren Massen in ``rippe``
    (:func:`~opencivil.querschnitt.profilblech.skizze`). Passen die Masse
    nicht zueinander, sagt ``fehler`` es mit den Worten der Felder. Eingesetzt
    wird sie von der Oberflaeche, wie ein Profil: sie ist ein Eintrag an
    einem Knoten.
    """
    wo = "Vorlage «Blechverbunddecke»"
    masse = {k: v for k, v in wahl.items() if k in BLECHMASSE}
    try:
        decke = BlechdeckeEintrag.aus_dict(masse, wo)
        inhalt_pruefen(decke, wo)
    except ProjektFehler as fehler:
        return {"fehler": fehler.grund, "teile": None}
    form = decke.form((0.0, 0.0))
    return {"fehler": None, "teile": profilblech.skizze(form).als_dict(),
            "rippe": profilblech.rippenskizze(form).als_dict()}


def vorlage_einsetzen(rumpf: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Setzt eine Vorlage in eine Querschnittsanalyse ein, mit dem Baukasten
    des Kerns (:meth:`QuerschnittsanalyseEintrag.vorlage_einsetzen`). Zurueck
    kommen ihre Elementlisten und die Kennungen der neuen Elemente -- die
    Oberflaeche uebernimmt sie in einem Schritt, den man rueckgaengig machen
    kann.
    """
    projekt = _projekt(rumpf)
    eintrag = projekt.querschnittsanalyse(str(rumpf.get("kennung") or ""))
    ursprung = rumpf.get("ursprung") or [0.0, 0.0]
    try:
        ursprung = (float(ursprung[0]), float(ursprung[1]))
    except (TypeError, ValueError, IndexError):
        raise DienstFehler(400, "Der Einsetzpunkt muss zwei Zahlen haben.") from None
    # Das zweite Material, das eine Vorlage zur Wahl stellt -- der Aufbeton.
    stoffe = {str(k): str(v) for k, v in ((rumpf.get("wahl") or {}).get("stoffe") or {}).items()}
    try:
        neu = eintrag.vorlage_einsetzen(
            _vorlage(rumpf).schluessel, material=str(rumpf.get("material") or ""),
            stahl=str(rumpf.get("stahl") or ""), stoffe=stoffe, ursprung=ursprung,
            **_vorlagenwahl(rumpf))
    except ValueError as fehler:
        raise DienstFehler(400, str(fehler)) from None
    d = eintrag.als_dict()
    listen = ("knoten", "flaechen", "staebe", "stablinien", "schubwaende", "hilfslinien")
    return {"neu": neu, "elemente": {liste: d[liste] for liste in listen}}


#: Name der Anfrage -> Funktion. Diese Namen sind der ganze Vertrag zwischen
#: Oberflaeche und Kern; beide Huellen reichen sie unveraendert durch.
ANFRAGEN: Dict[str, Callable[[Mapping[str, Any]], Dict[str, Any]]] = {
    "katalog": katalog,
    "beispiel": beispiel,
    "pruefen": pruefen,
    "mappe_oeffnen": mappe_oeffnen,
    "sandbox_zuruecksetzen": sandbox_zuruecksetzen,
    "verweise": verweise,
    "fallname": fallname,
    "rechnen": rechnen,
    "bericht": bericht,
    "bewehrung_suchen": bewehrung_suchen,
    "geometrie": geometrie,
    "analysediagramme": analysediagramme,
    "balkensystem_verlauf": balkensystem_verlauf,
    "balkensystem_bearbeiten": balkensystem_bearbeiten,
    "decke_zeichnung": decke_zeichnung,
    "decke_ergebnis": decke_ergebnis,
    "fachwerk_zeichnung": fachwerk_zeichnung,
    "fachwerk_suchen": fachwerk_suchen,
    "mauerwerk_zeichnung": mauerwerk_zeichnung,
    "vorlage": vorlage,
    "vorlage_einsetzen": vorlage_einsetzen,
}


# ===========================================================================
# Einstieg
# ===========================================================================


def bearbeite(name: str, rumpf: Mapping[str, Any] | None = None) -> Antwort:
    """
    Fuehrt eine Anfrage aus. Wirft nicht -- Fehler kommen als Antwort zurueck.

    Dass auch der Fehlerfall eine gewoehnliche Antwort ist, haelt die beiden
    Huellen duenn: keine muss sich ueberlegen, welche Ausnahme welchen Status
    verdient. Ein :class:`ProjektFehler` -- ein unbekanntes Bauteil, ein
    falscher Eintrag -- wird hier zur 400; die Anfragen fangen ihn darum
    nicht selbst (bis 2026-11-10 taten es vier, mit derselben Folge).
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
    return Antwort(fehlerdaten(meldung, spur), status)


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

    return umschlag(antwort.status, antwort.daten)
