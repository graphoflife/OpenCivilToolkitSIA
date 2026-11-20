"""
opencivil/mcp/werkzeuge.py -- was eine KI mit dem Werkzeug tun kann, und mit welchen Angaben.

Jedes Werkzeug ist eine Funktion mit Titel, Beschreibung und Eingaben
(:func:`werkzeug`). Was es annimmt, sagt seine Unterschrift: ein Argument
ohne Vorgabe ist Pflicht, und die Eingaben muessen in Namen und Folge zu ihr
passen -- so laufen Beschreibung und Funktion nicht auseinander. Jedes gibt
Text zurueck. Was es nicht kann, meldet es als Fehler des Werkzeugs
(``isError``), mit dem Satz des Kerns; ein Werkzeug, das aendert, aendert
dann nichts (:meth:`~opencivil.mcp.sitzung.Sitzung.aendern`).
"""

from __future__ import annotations

import inspect
import json
import traceback
from dataclasses import dataclass
from typing import Any, Callable, Dict, Mapping, Tuple

from opencivil.material.arten import MATERIALARTEN
from opencivil.material.beton import ERSTER_BETON
from opencivil.material.betonstahl import ERSTER_STAHL
from opencivil.mcp import ausgabe, zeiger
from opencivil.mcp.sitzung import (
    BAUTEILLISTEN, LISTEN, Geaendert, Sitzung, Werkzeugfehler, dateipfad, datei_form, dienst,
    liste_von, schreiben, unbekannt,
)
from opencivil.projekt import ProjektFehler
from opencivil.projekt.lesen import feldangaben, feldtypen, katalogname, ort_von
from opencivil.projekt.projekt import APPLISTEN
from opencivil.web.api import klassen


@dataclass(frozen=True)
class Werkzeug:
    """Ein Werkzeug, wie ``tools/list`` es nennt und ``tools/call`` es ruft."""

    name: str
    titel: str
    beschreibung: str
    eingaben: Mapping[str, Mapping[str, Any]]
    pflicht: Tuple[str, ...]
    lesend: bool
    """Ob es nur liest -- dann aendert es weder die Mappe noch eine Datei."""

    tun: Callable[..., str]

    def verzeichnis(self) -> Dict[str, Any]:
        """Wie ``tools/list`` es nennt, mit dem JSON-Schema seiner Eingaben."""
        return {
            "name": self.name, "title": self.titel, "description": self.beschreibung,
            "inputSchema": {"type": "object", "properties": dict(self.eingaben),
                            "required": list(self.pflicht), "additionalProperties": False},
            "annotations": {"readOnlyHint": self.lesend, "openWorldHint": False},
        }

    def aufrufen(self, sitzung: Sitzung, argumente: Any) -> Dict[str, Any]:
        """``tools/call``: sein Ergebnis als Text -- ein Fehler mit ``isError``, wie MCP es will."""
        try:
            _pruefen(self, argumente)
            return _ergebnis(self.tun(sitzung, **argumente))
        except (Werkzeugfehler, ProjektFehler) as fehler:
            return _ergebnis(str(fehler), fehler=True)
        except Exception as fehler:  # noqa: BLE001 -- wie dienst.bearbeite: nichts bricht stumm
            traceback.print_exc()
            return _ergebnis(f"Unerwarteter Fehler in {self.name}: {type(fehler).__name__}: "
                             f"{fehler}", fehler=True)


#: Die Werkzeuge unter ihrem Namen, in der Folge, in der ``tools/list`` sie nennt.
WERKZEUGE: Dict[str, Werkzeug] = {}


def werkzeug(titel: str, beschreibung: str, *, lesend: bool = False,
             **eingaben: Mapping[str, Any]) -> Callable[[Callable[..., str]], Callable[..., str]]:
    """
    Traegt die Funktion darunter als Werkzeug ein, unter ihrem Namen. Ihr
    erstes Argument ist die Sitzung; die uebrigen sind die ``eingaben``, je
    mit ihrem JSON-Schema, in derselben Folge.
    """
    def eintragen(tun: Callable[..., str]) -> Callable[..., str]:
        parameter = list(inspect.signature(tun).parameters.values())[1:]
        if [p.name for p in parameter] != list(eingaben):
            raise TypeError(f"{tun.__name__}: die Eingaben {list(eingaben)} passen nicht zur "
                            f"Unterschrift {[p.name for p in parameter]}.")
        pflicht = tuple(p.name for p in parameter if p.default is inspect.Parameter.empty)
        WERKZEUGE[tun.__name__] = Werkzeug(tun.__name__, titel, beschreibung, eingaben, pflicht,
                                           lesend, tun)
        return tun
    return eintragen


def _text(beschreibung: str, **mehr: Any) -> Dict[str, Any]:
    return {"type": "string", "description": beschreibung, **mehr}


def _ja_nein(beschreibung: str) -> Dict[str, Any]:
    return {"type": "boolean", "description": beschreibung}


EINTRAG = _text("Name oder Kennung des Eintrags, wie eintraege sie nennt – «Decke über EG» "
                "oder «q3».")
APP = _text("Die App, wenn der Name in mehreren steht wie «Sandbox»: ihre Liste "
            "(«querschnitte») oder der Name ihrer Einträge («Platte») – arten nennt alle.")
DATEI = _text("Pfad der Projektdatei (.json), absolut oder vom Arbeitsverzeichnis aus.")
VERWERFEN = _ja_nein("true: Änderungen der offenen Mappe, die noch nicht gespeichert sind, "
                     "verwerfen.")
UEBERSCHREIBEN = _ja_nein("true: eine Datei, die es dort schon gibt, überschreiben.")
AUSGABE = _text("In diese Datei schreiben, statt den Text zurückzugeben.")


# ===========================================================================
# Datei und Projekte
# ===========================================================================


@werkzeug("Projektdatei öffnen",
          "Öffnet eine Projektdatei (eine Mappe mit einem oder mehreren Projekten) wie «Öffnen» "
          "der Seite: geprüft, mit den Sandboxen, wie gespeichert. Danach ist das erste Projekt "
          "gewählt; in ihm arbeiten alle anderen Werkzeuge.",
          pfad=DATEI, verwerfen=VERWERFEN)
def datei_oeffnen(sitzung: Sitzung, pfad: str, verwerfen: bool = False) -> str:
    sitzung.oeffnen(pfad, verwerfen=verwerfen)
    return f"Geöffnet. {ausgabe.ueberblick(sitzung)}"


@werkzeug("Neue Projektdatei",
          f"Eine neue Mappe mit einem Projekt «Projekt 1» – mit {ERSTER_BETON} und {ERSTER_STAHL} "
          f"und einer Sandbox je App, noch ohne Datei: datei_speichern mit pfad schreibt sie.",
          verwerfen=VERWERFEN)
def datei_neu(sitzung: Sitzung, verwerfen: bool = False) -> str:
    sitzung.neu(verwerfen=verwerfen)
    return f"Neu angelegt. {ausgabe.ueberblick(sitzung)}"


@werkzeug("Projektdatei speichern",
          "Schreibt die Mappe mit allen Projekten und ihren Sandboxen, wie «Speichern» der Seite "
          "– ohne pfad in die offene Datei.",
          pfad=_text("Wohin – ohne Angabe in die offene Datei."), ueberschreiben=UEBERSCHREIBEN)
def datei_speichern(sitzung: Sitzung, pfad: str = "", ueberschreiben: bool = False) -> str:
    return f"Gespeichert: {sitzung.speichern(pfad, ueberschreiben=ueberschreiben)}."


@werkzeug("Projekte", "Die Projekte der Mappe und welches gewählt ist.", lesend=True)
def projekte(sitzung: Sitzung) -> str:
    return ausgabe.ueberblick(sitzung)


@werkzeug("Projekt wählen", "Wählt ein Projekt der Mappe – in ihm arbeiten danach alle "
          "anderen Werkzeuge.", name=_text("Der Name des Projekts."))
def projekt_waehlen(sitzung: Sitzung, name: str) -> str:
    sitzung.waehlen(name)
    return ausgabe.eintraege(sitzung, LISTEN)


@werkzeug("Projekt anlegen",
          f"Ein neues Projekt hinter den anderen, gleich gewählt – wie «+» der Projektreihe: mit "
          f"{ERSTER_BETON}, {ERSTER_STAHL} und einer Sandbox je App.",
          name=_text("Sein Name – ohne Angabe «Projekt 2» oder die nächste freie Nummer."))
def projekt_anlegen(sitzung: Sitzung, name: str = "") -> str:
    sitzung.projekt_anlegen(name)
    return f"Angelegt und gewählt.\n\n{ausgabe.eintraege(sitzung, LISTEN)}"


# ===========================================================================
# Was es gibt
# ===========================================================================


@werkzeug("Apps", "Die Apps, je mit ihrer Liste – so heisst «app» in den anderen Werkzeugen – "
          "und dem Namen ihrer Felder für felder; dazu die Sorten der Materialien. Braucht keine "
          "offene Datei.", lesend=True)
def arten(sitzung: Sitzung) -> str:
    return ausgabe.arten()


@werkzeug("Felder",
          "Was eine Art von Eintrag hält, je Feld: «art» (zahl, ganz, text, ja/nein, wahl mit "
          "ihren Werten, eintrag, liste oder zuordnung), «leer», wo auch nichts stehen darf, "
          "Einheit und Grenzen; dazu unter «neu», wie ein neuer aussieht. Elemente darin – "
          "Lastfälle, Lagen, Schichten – mit dem Namen, den «klasse» nennt.",
          lesend=True,
          art=_text("Eine App – ihre Liste («querschnitte») oder der Name ihrer Einträge "
                    "(«Platte») – oder eine Klasse, wie «klasse» sie nennt («kombination»)."))
def felder(sitzung: Sitzung, art: str) -> str:
    klasse = _klasse(art)
    angaben = feldangaben(klasse)
    beschrieben = {name: {**typ, **angaben.get(name, {})} for name, typ in feldtypen(klasse).items()}
    return json.dumps({"klasse": katalogname(klasse), "felder": beschrieben,
                       "neu": datei_form(klasse.frisch())}, ensure_ascii=False, indent=1)


def _klasse(art: str) -> type:
    """Die Klasse von Eintraegen, die ``art`` nennt -- ueber ihren Namen im Katalog oder ihre App."""
    nach_namen = klassen()
    if art in nach_namen:
        return nach_namen[art]
    try:
        return LISTEN[liste_von(art)]
    except Werkzeugfehler:
        raise Werkzeugfehler(unbekannt(f"Eine Art «{art}» gibt es nicht – gemeint ist eine App "
                                       f"(arten) oder eine Klasse, wie felder sie unter «klasse» "
                                       f"nennt.", art, [*nach_namen, *LISTEN])) from None


@werkzeug("Einträge",
          "Die Einträge des gewählten Projekts je App, mit Kennung. Die Sandbox jeder App ist zum "
          "Ausprobieren: sie kommt nicht in den Bericht und lässt sich nicht löschen, nur "
          "zurücksetzen.",
          lesend=True, app=_text("Nur diese App – ohne Angabe alle."))
def eintraege(sitzung: Sitzung, app: str = "") -> str:
    return ausgabe.eintraege(sitzung, [liste_von(app)] if app else LISTEN)


# ===========================================================================
# Eintraege
# ===========================================================================


@werkzeug("Eintrag lesen",
          "Ein Eintrag, wie er in der Projektdatei steht, als JSON – die Form, die eintrag_setzen "
          "nimmt und in die die Pfade von eintrag_aendern zeigen.",
          lesend=True, eintrag=EINTRAG, app=APP)
def eintrag_lesen(sitzung: Sitzung, eintrag: str, app: str = "") -> str:
    return json.dumps(datei_form(sitzung.finden(eintrag, app).eintrag), ensure_ascii=False, indent=1)


@werkzeug("Eintrag setzen",
          "Ersetzt einen Eintrag ganz durch inhalt, in der Form von eintrag_lesen. Der Kern liest "
          "ihn wie eine Datei; was er nicht lesen kann, ändert nichts, und seine Meldung kommt "
          "zurück. Die Kennung bleibt. Elemente darin – Lastfälle, Knoten – tragen eigene "
          "Kennungen, und eine gelöschte kommt nie wieder.",
          eintrag=EINTRAG, inhalt={"type": "object", "description": "Der ganze Eintrag."}, app=APP)
def eintrag_setzen(sitzung: Sitzung, eintrag: str, inhalt: Dict[str, Any], app: str = "") -> str:
    return _gemeldet("Ersetzt", sitzung.ersetzen(eintrag, app, lambda _alt: inhalt))


@werkzeug("Eintrag ändern",
          "Ändert Felder eines Eintrags über Pfade in seine Form von eintrag_lesen: «/h», "
          "«/lastfaelle/0/M_Ed»; «-» am Ende einer Liste hängt an. Die Änderungen gelten alle "
          "zusammen oder keine. Der Kern prüft sie sofort; was er nicht lesen kann, ändert "
          "nichts, und seine Meldung kommt zurück.",
          eintrag=EINTRAG,
          aenderungen={
              "type": "array", "description": "Die Änderungen, der Reihe nach.",
              "items": {"type": "object", "additionalProperties": False, "required": ["pfad"],
                        "properties": {
                            "pfad": _text("Wohin, nach RFC 6901: «/h», «/lastfaelle/0/M_Ed», "
                                          "«/lastfaelle/-» hängt an; «» ist der ganze Eintrag."),
                            "wert": {"description": "Der neue Wert – Zahl, Text, true/false, "
                                                    "Liste oder Objekt."},
                            "entfernen": _ja_nein("true statt wert: aus der Liste nehmen, ein "
                                                  "Feld auf seine Vorgabe zurück."),
                        }},
          },
          app=APP)
def eintrag_aendern(sitzung: Sitzung, eintrag: str, aenderungen: list, app: str = "") -> str:
    return _gemeldet("Geändert", sitzung.ersetzen(eintrag, app,
                                                  lambda roh: zeiger.anwenden(roh, aenderungen)))


@werkzeug("Eintrag anlegen",
          "«+» einer App: ein neuer Eintrag nach der Vorlage des Kerns, am Ende der Liste, mit dem "
          "ersten Material jeder Art, das er nimmt. Er heisst wie in der Seite – «Platte 1» – "
          "oder name.",
          app=_text("Die App: ihre Liste («querschnitte») oder der Name ihrer Einträge "
                    "(«Platte»). Materialien legt material_anlegen an."),
          name=_text("Sein Name – ohne Angabe der nächste freie, «Platte 2»."))
def eintrag_anlegen(sitzung: Sitzung, app: str, name: str = "") -> str:
    liste = liste_von(app)
    if liste not in APPLISTEN:
        raise Werkzeugfehler("Ein Material legt material_anlegen an – mit Art und Sorte.")

    def tun(projekt: Any) -> Any:
        neu = projekt.eintrag_anlegen(liste)
        if name:
            neu.name = name
        return neu

    return _gemeldet("Angelegt", sitzung.aendern(tun))


@werkzeug("Material anlegen",
          "«+ Material»: eine Normsorte, wie sie ist – oder mit eigen ein eigenes Material mit ihr "
          "als Vorlage, dessen Kennwerte sich ändern lassen.",
          art=_text("Die Art des Materials.", enum=list(MATERIALARTEN)),
          sorte=_text("Die Sorte – «C30/37», «B500B», «S355»; arten nennt alle."),
          eigen=_ja_nein("true: ein eigenes Material nach der Sorte."))
def material_anlegen(sitzung: Sitzung, art: str, sorte: str, eigen: bool = False) -> str:
    return _gemeldet("Angelegt", sitzung.aendern(
        lambda projekt: projekt.material_anlegen(art, sorte, eigen=eigen)))


@werkzeug("Eintrag kopieren",
          "⧉: eine Kopie gleich hinter dem Original, alles wie dort – «Decke (Kopie)». Die Kopie "
          "der Sandbox ist ein gewöhnlicher Eintrag und heisst wie ein neuer.",
          eintrag=EINTRAG, app=APP)
def eintrag_kopieren(sitzung: Sitzung, eintrag: str, app: str = "") -> str:
    kennung = sitzung.finden(eintrag, app).eintrag.kennung
    return _gemeldet("Kopiert", sitzung.aendern(lambda projekt: projekt.eintrag_kopieren(kennung)))


@werkzeug("Eintrag löschen",
          "×: ein Eintrag oder ein Material geht – nicht die Sandbox, und nicht, solange ein "
          "Bauteil darauf zeigt; die Meldung nennt es dann.",
          eintrag=EINTRAG, app=APP)
def eintrag_loeschen(sitzung: Sitzung, eintrag: str, app: str = "") -> str:
    kennung = sitzung.finden(eintrag, app).eintrag.kennung
    weg = sitzung.aendern(lambda projekt: projekt.eintrag_loeschen(kennung)).eintrag
    return f"Gelöscht: {ort_von(weg)} ({weg.kennung})."


@werkzeug("Sandbox zurücksetzen",
          "↺: die Sandbox einer App beginnt neu, nach der Vorlage und mit dem ersten Material "
          "jeder Art. Wer auf sie zeigt, zeigt weiter auf sie.",
          app=_text("Die App: ihre Liste («querschnitte») oder der Name ihrer Einträge "
                    "(«Platte»)."))
def sandbox_zuruecksetzen(sitzung: Sitzung, app: str) -> str:
    liste = liste_von(app)
    return _gemeldet("Zurückgesetzt", sitzung.aendern(
        lambda projekt: projekt.sandbox_zuruecksetzen(liste)))


def _gemeldet(was: str, geaendert: Geaendert) -> str:
    """Was eine Aenderung zurueckgibt: den Eintrag und, in den Worten des Kerns, was ihm fehlt."""
    e = geaendert.eintrag
    zeilen = [f"{was}: {ort_von(e)} ({e.kennung}).", *(f"- {h}" for h in geaendert.hinweise)]
    if geaendert.projektfehler:
        zeilen.append(f"Das Projekt rechnet weiterhin nicht: {geaendert.projektfehler}")
    return "\n".join(zeilen)


# ===========================================================================
# Rechnen und Bericht
# ===========================================================================


@werkzeug("Rechnen",
          "Rechnet das gewählte Projekt – ohne die Sandboxen, wie der Bericht – oder mit eintrag "
          "nur dieses Bauteil, auch eine Sandbox. Zurück kommt je Bauteil die Tabelle seiner "
          "Nachweise mit dem Erfüllungsgrad, wie die Zusammenfassung der Seite, und was der Kern "
          "dazu sagt – auch, was noch fehlt.",
          lesend=True, eintrag=_text("Nur dieses Bauteil, Name oder Kennung – ohne Angabe alle."),
          app=APP)
def rechnen(sitzung: Sitzung, eintrag: str = "", app: str = "") -> str:
    kennung = _bauteil(sitzung, eintrag, app) if eintrag else ""
    gerechnet = sitzung.projekt.nur(kennung) if kennung else sitzung.projekt.ohne_sandboxen()
    return ausgabe.rechnung(dienst("rechnen", {"projekt": gerechnet.als_dict()}), gerechnet,
                            nur=kennung)


@werkzeug("Herleitung",
          "Die Herleitung eines Bauteils als Markdown mit LaTeX, wie die rechte Spalte der Seite – "
          "mit seinen Materialien und den Bauteilen, deren Querschnitt es nimmt. Sie ist lang: "
          "mit pfad in eine Datei.",
          eintrag=EINTRAG, app=APP, pfad=AUSGABE, ueberschreiben=UEBERSCHREIBEN)
def herleitung(sitzung: Sitzung, eintrag: str, app: str = "", pfad: str = "",
               ueberschreiben: bool = False) -> str:
    rumpf = {"projekt": sitzung.projekt.als_dict(), "nur": _bauteil(sitzung, eintrag, app)}
    return _ausgeben(dienst("bericht", rumpf)["markdown"], pfad, ueberschreiben)


@werkzeug("Bericht",
          "Der Bericht des gewählten Projekts, ohne die Sandboxen – als Markdown oder als "
          "LaTeX-Dokument, wie «Bericht» der Seite. Er ist lang: mit pfad in eine Datei.",
          als=_text("markdown oder latex.", enum=["markdown", "latex"]),
          pfad=AUSGABE, ueberschreiben=UEBERSCHREIBEN)
def bericht(sitzung: Sitzung, als: str = "markdown", pfad: str = "",
            ueberschreiben: bool = False) -> str:
    daten = dienst("bericht", {"projekt": sitzung.projekt.als_dict()})
    return _ausgeben(daten["tex" if als == "latex" else "markdown"], pfad, ueberschreiben)


def _bauteil(sitzung: Sitzung, eintrag: str, app: str) -> str:
    """Die Kennung des Bauteils, das ``eintrag`` nennt -- ein Material oder Skript rechnet nicht fuer sich."""
    fund = sitzung.finden(eintrag, app)
    if fund.liste not in BAUTEILLISTEN:
        raise Werkzeugfehler(f"{ort_von(fund.eintrag)} rechnet nicht für sich: " + (
            "ein Material rechnet in den Bauteilen, die es nehmen." if fund.liste == "materialien"
            else "ein Skript läuft in der Konsole der Seite, nicht hier."))
    return fund.eintrag.kennung


def _ausgeben(text: str, pfad: str, ueberschreiben: bool) -> str:
    """``text`` zurueck -- oder mit ``pfad`` in diese Datei, und zurueck, wohin."""
    if not pfad:
        return text
    ziel = dateipfad(pfad)
    schreiben(ziel, text, ueberschreiben=ueberschreiben)
    return f"Geschrieben: {ziel} ({len(text)} Zeichen)."


# ===========================================================================
# Pruefen der Argumente
# ===========================================================================


#: Je Typ des JSON-Schemas, was ihn in Python traegt, und wie er in einer Meldung heisst.
_TYPEN = {"string": (str, "Text"), "boolean": (bool, "true oder false"),
          "integer": (int, "eine ganze Zahl"), "number": ((int, float), "eine Zahl"),
          "array": (list, "eine Liste"), "object": (dict, "ein Objekt")}


def _pruefen(w: Werkzeug, argumente: Any) -> None:
    """Die Argumente gegen die Eingaben des Werkzeugs -- vor dem Aufruf, mit Satz statt Ausnahme."""
    if not isinstance(argumente, dict):
        raise Werkzeugfehler(f"Die Argumente von {w.name} sind ein JSON-Objekt, nicht "
                             f"{json.dumps(argumente, ensure_ascii=False)[:60]}.")
    _wert_pruefen({"type": "object", "properties": w.eingaben, "required": w.pflicht},
                  argumente, w.name)


def _wert_pruefen(schema: Mapping[str, Any], wert: Any, wo: str) -> None:
    typ = schema.get("type")
    if typ is not None:
        traeger, wort = _TYPEN[typ]
        if not isinstance(wert, traeger) or (isinstance(wert, bool) and typ != "boolean"):
            raise Werkzeugfehler(f"{wo} ist {wort}, nicht {json.dumps(wert, ensure_ascii=False)[:60]}.")
    if "enum" in schema and wert not in schema["enum"]:
        raise Werkzeugfehler(f"{wo} ist eines von {', '.join(schema['enum'])}, nicht «{wert}».")
    if typ == "array":
        for i, teil in enumerate(wert):
            _wert_pruefen(schema["items"], teil, f"{wo} Nr. {i}")
    if typ == "object" and "properties" in schema:
        bekannt = schema["properties"]
        for name in wert:
            if name not in bekannt:
                raise Werkzeugfehler(unbekannt(f"{wo}: ein Argument «{name}» gibt es nicht.", name,
                                               bekannt)
                                     + f" Möglich sind: {', '.join(bekannt) or 'keine'}.")
        for name in schema.get("required", ()):
            if name not in wert:
                raise Werkzeugfehler(f"{wo}: es fehlt «{name}» – {bekannt[name]['description']}")
        for name, teil in wert.items():
            _wert_pruefen(bekannt[name], teil, f"«{name}»")


def _ergebnis(text: str, *, fehler: bool = False) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": text}], "isError": fehler}
