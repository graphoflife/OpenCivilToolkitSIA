"""
opencivil/mcp/sitzung.py -- die offene Projektdatei, und wie sie sich aendert.

VERANTWORTUNG:
Die :class:`Sitzung` haelt, was die Seite im Browser haelt: die Mappe mit
ihren Projekten (:class:`~opencivil.projekt.mappe.Mappe`), welches gewaehlt
ist, aus welcher Datei sie kam und ob seither etwas ungespeichert ist.
Gerechnet und geoeffnet wird ueber den Rechendienst (:func:`dienst`), wie in
der Seite.

EINE TUER FUER JEDE AENDERUNG:
Ein Werkzeug aendert an einer Kopie des Projekts (:meth:`Sitzung.aendern`).
Gilt sie, ersetzt sie das Projekt; sonst bleibt alles, wie es war, und die
Meldung des Kerns geht unveraendert zurueck. Abgewiesen wird, was der Kern
nicht lesen kann -- ein Feld, das es nicht gibt, ein Text statt einer Zahl
--, und was das ganze Projekt anhielte, wo es vorher rechnete: zwei
Materialien mit demselben Namen. Was nur den Eintrag anhaelt -- eine Platte
ohne Bewehrung, eine Dicke von null --, gilt; der Rest rechnet weiter
(Benutzer, 2026-11-19), und die Antwort sagt gleich, was fehlt, in den Worten
des Kerns (:attr:`Geaendert.hinweise`).
"""

from __future__ import annotations

import copy
import difflib
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Mapping, NamedTuple, Optional

from opencivil.projekt import Mappe, Projekt, ProjektFehler
from opencivil.projekt.aufbau import BAUTEILE
from opencivil.projekt.eintraege import BauteilEintrag, MaterialEintrag
from opencivil.projekt.lesen import ort_von
from opencivil.projekt.netz import von_hand
from opencivil.projekt.projekt import APPLISTEN, naechster_name
from opencivil.web.dienst import bearbeite

#: Die Listen, deren Eintraege ein Werkzeug anspricht -- die Materialien und
#: die Apps --, je mit der Klasse ihrer Eintraege.
LISTEN: Dict[str, type] = {"materialien": MaterialEintrag,
                           **{liste: klasse for liste, (klasse, _) in APPLISTEN.items()}}

#: Die Listen, deren Eintraege rechnen: ohne Materialien und Skripte.
BAUTEILLISTEN = tuple(art.liste for art in BAUTEILE)


class Werkzeugfehler(Exception):
    """Was ein Werkzeug nicht tun kann -- ein Satz, der so zurueckgeht."""


class Fund(NamedTuple):
    """Ein Eintrag des gewaehlten Projekts: seine Liste, seine Stelle darin und er selbst."""

    liste: str
    stelle: int
    eintrag: Any


@dataclass
class Geaendert:
    """Was eine Aenderung hinterlaesst: den Eintrag und was der Kern zu ihm sagt."""

    eintrag: Any
    hinweise: List[str] = field(default_factory=list)
    """Die Hinweise des Aufbaus zu ihm, wie der Kern sie schreibt -- auch, was ihm fehlt."""

    projektfehler: str = ""
    """Warum das Projekt nicht rechnet -- nur, wo es das schon vorher nicht tat."""


@dataclass
class Sitzung:
    """Die offene Mappe, das gewaehlte Projekt darin, die Datei dazu."""

    mappe: Optional[Mappe] = None
    gewaehlt: int = 0
    pfad: Optional[Path] = None
    ungespeichert: bool = False

    # -- Datei --------------------------------------------------------------

    def oeffnen(self, pfad: str, *, verwerfen: bool = False) -> None:
        """
        Oeffnet eine Projektdatei wie «Öffnen» der Seite (Dienst
        ``mappe_oeffnen``): geprueft, mit den Sandboxen, wie gespeichert.
        """
        self._nichts_verlieren(verwerfen)
        ziel = dateipfad(pfad)
        try:
            roh = json.loads(ziel.read_text(encoding="utf-8"))
        except FileNotFoundError:
            raise Werkzeugfehler(f"Die Datei {ziel} gibt es nicht.") from None
        except (OSError, UnicodeDecodeError) as fehler:
            raise Werkzeugfehler(f"Die Datei {ziel} lässt sich nicht lesen: {fehler}.") from None
        except json.JSONDecodeError as fehler:
            raise Werkzeugfehler(f"In {ziel} steht kein JSON: {fehler}.") from None
        mappe = Mappe.aus_dict(dienst("mappe_oeffnen", {"mappe": roh})["mappe"])
        self.mappe, self.gewaehlt, self.pfad, self.ungespeichert = mappe, 0, ziel, False

    def neu(self, *, verwerfen: bool = False) -> None:
        """Eine neue Mappe mit einem neuen Projekt, noch ohne Datei."""
        self._nichts_verlieren(verwerfen)
        self.mappe, self.gewaehlt, self.pfad, self.ungespeichert = (
            Mappe([neues_projekt(())]), 0, None, False)

    def speichern(self, pfad: str = "", *, ueberschreiben: bool = False) -> Path:
        """
        Schreibt die Mappe, wie «Speichern» der Seite, mit den Sandboxen --
        ohne ``pfad`` in ihre Datei. Eine andere, die es schon gibt, nur mit
        ``ueberschreiben``.
        """
        mappe = self.offen()
        ziel = dateipfad(pfad) if pfad else self.pfad
        if ziel is None:
            raise Werkzeugfehler("Wohin? Die Mappe ist neu und hat noch keine Datei – pfad angeben.")
        schreiben(ziel, json.dumps(mappe.als_dict(), indent=2, ensure_ascii=False) + "\n",
                  ueberschreiben=ueberschreiben or ziel == self.pfad)
        self.pfad, self.ungespeichert = ziel, False
        return ziel

    def offen(self) -> Mappe:
        """Die offene Mappe -- ohne eine sagt der Fehler, wie man zu einer kommt."""
        if self.mappe is None:
            raise Werkzeugfehler("Noch ist keine Projektdatei offen – zuerst datei_oeffnen "
                                 "oder datei_neu.")
        return self.mappe

    def _nichts_verlieren(self, verwerfen: bool) -> None:
        if self.ungespeichert and not verwerfen:
            raise Werkzeugfehler("Die offene Mappe hat Änderungen, die noch nicht gespeichert "
                                 "sind – zuerst datei_speichern, oder mit verwerfen: true ohne sie "
                                 "weiter.")

    # -- Projekte -----------------------------------------------------------

    @property
    def projekt(self) -> Projekt:
        """Das gewaehlte Projekt -- in ihm arbeitet jedes Werkzeug."""
        return self.offen().projekte[self.gewaehlt]

    def waehlen(self, name: str) -> Projekt:
        namen = [p.name for p in self.offen().projekte]
        if name not in namen:
            raise Werkzeugfehler(unbekannt(f"Ein Projekt «{name}» gibt es in der Mappe nicht.",
                                           name, namen))
        self.gewaehlt = namen.index(name)
        return self.projekt

    def projekt_anlegen(self, name: str = "") -> Projekt:
        """Ein neues Projekt hinter den anderen, gleich gewaehlt -- wie «+» der Projektreihe."""
        mappe = self.offen()
        projekt = neues_projekt(p.name for p in mappe.projekte)
        if name:
            projekt.name = name
        Mappe([*mappe.projekte, projekt]).pruefen()
        mappe.projekte.append(projekt)
        self.gewaehlt, self.ungespeichert = len(mappe.projekte) - 1, True
        return projekt

    # -- Eintraege ----------------------------------------------------------

    def finden(self, eintrag: str, app: str = "") -> Fund:
        """
        Ein Eintrag des gewaehlten Projekts, nach seinem Namen oder seiner
        Kennung -- mit ``app`` nur in deren Liste. Heissen mehrere so, etwa
        die Sandboxen, sagt der Fehler, welche.
        """
        projekt = self.projekt
        listen = [liste_von(app)] if app else list(LISTEN)
        treffer = [Fund(liste, i, e) for liste in listen for i, e in enumerate(getattr(projekt, liste))
                   if eintrag in (e.kennung, name_von(e))]
        if len(treffer) == 1:
            return treffer[0]
        if treffer:
            raise Werkzeugfehler(f"«{eintrag}» heissen mehrere: "
                                 + ", ".join(f"{ort_von(t.eintrag)} ({t.eintrag.kennung})" for t in treffer)
                                 + " – mit app oder der Kennung sagen, welcher gemeint ist.")
        wo = f"in {LISTEN[listen[0]].BEZEICHNUNG}" if app else f"im Projekt «{projekt.name}»"
        raise Werkzeugfehler(unbekannt(f"Einen Eintrag «{eintrag}» gibt es {wo} nicht.", eintrag,
                                       (name_von(e) for liste in listen for e in getattr(projekt, liste))))

    def aendern(self, tun: Callable[[Projekt], Any]) -> Geaendert:
        """
        ``tun`` aendert eine Kopie des Projekts und gibt den Eintrag zurueck,
        den es angelegt oder geaendert hat. Gilt die Kopie (siehe Dateikopf),
        ersetzt sie das Projekt; sonst bleibt es, wie es war.
        """
        alt = self.projekt
        kopie = copy.deepcopy(alt)
        eintrag = tun(kopie)
        kopie.pruefen()
        try:
            aufbau = kopie.aufbauen()
        except ProjektFehler as fehler:
            if _rechnet(alt):
                raise
            aufbau, projektfehler = None, str(fehler)
        else:
            projektfehler = ""
        self.offen().projekte[self.gewaehlt] = kopie
        self.ungespeichert = True
        hinweise = [w.text for w in (aufbau.warnungen if aufbau else ())
                    if kennung_im_raum(w.raum) == eintrag.kennung]
        return Geaendert(eintrag, hinweise, projektfehler)

    def ersetzen(self, eintrag: str, app: str,
                 neu: Callable[[Dict[str, Any]], Any]) -> Geaendert:
        """
        Ersetzt einen Eintrag durch das, was ``neu`` aus seiner Datei-Form
        macht -- gelesen vom Leser des Kerns, wie eine Datei. Seine Kennung
        bleibt, auf sie zeigen andere; eine Kennung seiner Elemente kommt nie
        wieder (:func:`~opencivil.projekt.netz.von_hand`).
        """
        fund = self.finden(eintrag, app)

        def tun(projekt: Projekt) -> Any:
            alt = getattr(projekt, fund.liste)[fund.stelle]
            wo = ort_von(alt)
            roh = neu(datei_form(alt))
            if not isinstance(roh, dict):
                raise Werkzeugfehler(f"{wo}: ein Eintrag ist ein JSON-Objekt, nicht "
                                     f"{json.dumps(roh, ensure_ascii=False)[:60]}.")
            roh.setdefault("kennung", alt.kennung)
            ersatz = type(alt).aus_dict(roh, wo)
            if ersatz.kennung != alt.kennung:
                raise Werkzeugfehler(f"{wo}: die Kennung bleibt '{alt.kennung}' – auf sie zeigen "
                                     f"andere Einträge.")
            if isinstance(alt, BauteilEintrag):
                von_hand(alt, ersatz, wo)
            getattr(projekt, fund.liste)[fund.stelle] = ersatz
            return ersatz

        return self.aendern(tun)


# ===========================================================================
# Hilfen
# ===========================================================================


def dienst(name: str, rumpf: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Eine Anfrage an den Rechendienst, wie die Seite sie stellt
    (:func:`~opencivil.web.dienst.bearbeite`). Seine Fehlermeldung wird zum
    :class:`Werkzeugfehler`; die Spur eines unerwarteten geht nach stderr.
    """
    antwort = bearbeite(name, rumpf)
    if antwort.ist_fehler:
        if antwort.daten.get("spur"):
            print(antwort.daten["spur"], file=sys.stderr)
        raise Werkzeugfehler(antwort.daten["fehler"])
    return antwort.daten


def neues_projekt(namen: Iterable[str]) -> Projekt:
    """
    Ein neues Projekt, wie «+» der Projektreihe es anlegt (web/js/projekte.js):
    «Projekt 1» oder die naechste freie Nummer, mit dem ersten Beton und
    Stahl und mit den Sandboxen.
    """
    projekt = Projekt.neu(naechster_name(Projekt.STAMM, namen))
    projekt.sandboxen_anlegen()
    return projekt


def liste_von(app: str) -> str:
    """Die Liste einer App, gesagt mit ihr selbst («querschnitte») oder dem Namen ihrer Eintraege («Platte»)."""
    for liste, klasse in LISTEN.items():
        if app.casefold() in (liste.casefold(), klasse.BEZEICHNUNG.casefold()):
            return liste
    raise Werkzeugfehler(f"Eine App «{app}» gibt es nicht. Möglich sind: "
                         + ", ".join(f"{k.BEZEICHNUNG} ({liste})" for liste, k in LISTEN.items()) + ".")


def name_von(eintrag: Any) -> str:
    """Wie ein Eintrag heisst -- ein Material ohne eigenen Namen nach seiner Sorte."""
    return getattr(eintrag, "anzeigename", None) or eintrag.name


def kennung_im_raum(raum: str) -> str:
    """
    Die Kennung des Eintrags, dem ein Name im Rechenwerk gehoert: «q3» in
    «querschnitt.q3.nachweis.mn.x» -- wie ``inSandbox`` in web/js/zustand.js.
    """
    teile = raum.split(".")
    return teile[1] if len(teile) > 1 else ""


def datei_form(eintrag: Any) -> Dict[str, Any]:
    """Ein Eintrag, wie er in der Datei steht -- als JSON-Daten, eine Wahl als ihr Text."""
    return json.loads(json.dumps(eintrag.als_dict(), ensure_ascii=False))


def unbekannt(satz: str, name: str, namen: Iterable[str]) -> str:
    """``satz``, und wenn es einen gibt, der aehnlichste der ``namen`` -- wie der Leser des Kerns."""
    aehnlich = difflib.get_close_matches(name, list(namen), n=1)
    return satz + (f" Gemeint ist vielleicht «{aehnlich[0]}»?" if aehnlich else "")


def dateipfad(pfad: str) -> Path:
    """Ein Pfad, wie ein Werkzeug ihn bekommt -- ``~`` und Relatives vom Arbeitsverzeichnis aus aufgeloest."""
    return Path(pfad).expanduser().resolve()


def schreiben(ziel: Path, text: str, *, ueberschreiben: bool = False) -> None:
    """
    Schreibt ``text`` nach ``ziel`` -- eine Datei, die es schon gibt, nur mit
    ``ueberschreiben``. Erst ganz daneben, dann an ihren Ort: bricht etwas
    ab, bleibt die alte Datei heil.
    """
    if ziel.is_dir():
        raise Werkzeugfehler(f"{ziel} ist ein Ordner – einen Dateinamen angeben.")
    if ziel.exists() and not ueberschreiben:
        raise Werkzeugfehler(f"{ziel} gibt es schon. Überschreiben nur mit ueberschreiben: true.")
    zwischen = ziel.with_name(f".{ziel.name}.entsteht")
    try:
        ziel.parent.mkdir(parents=True, exist_ok=True)
        zwischen.write_text(text, encoding="utf-8")
        os.replace(zwischen, ziel)
    except OSError as fehler:
        zwischen.unlink(missing_ok=True)
        raise Werkzeugfehler(f"{ziel} lässt sich nicht schreiben: {fehler.strerror}.") from None


def _rechnet(projekt: Projekt) -> bool:
    """Ob der Kern das Projekt aufbauen kann -- ohne Fehler, der alles anhaelt."""
    try:
        projekt.aufbauen()
    except ProjektFehler:
        return False
    return True
