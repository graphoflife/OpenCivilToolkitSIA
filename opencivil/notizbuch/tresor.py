"""
opencivil/notizbuch/tresor.py -- erzeugte Seiten in den Ordner ``notizbuch/``.

VERANTWORTUNG:
Schreibt die Seiten, die aus dem Code entstehen, in den Tresor -- so, dass
nichts verloren geht, was von Hand dazukam. Und fuehrt das Verzeichnis, aus
dem die Oberflaeche erfaehrt, welche Seiten es gibt.

AUFBAU EINER ERZEUGTEN SEITE::

    ---
    erzeugt: 3f9a1c0b7d2e
    art: formel
    tags: [formel]
    ---
    der erzeugte Teil
    <!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->
    der eigene Teil, von Hand

``erzeugt`` ist die Pruefsumme ueber alles bis und mit der Linie, ohne die
eigene Zeile. Beim Neuerzeugen wird nur dieser Teil ersetzt; der eigene Teil
bleibt Zeichen fuer Zeichen. Seiten ohne eigenen Teil -- Modul- und
Verzeichnisseiten -- haben keine Linie: sie sind ganz erzeugt.

WER WAS ANFASSEN DARF:
Dem Generator gehoeren nur Dateien mit ``erzeugt:``. Eine Notiz ohne, wo
immer sie liegt, bleibt unberuehrt. Hat jemand oben in einer erzeugten Seite
etwas geaendert -- getippt, oder in Obsidian umbenannt, das die Links
nachfuehrt --, stimmt die Pruefsumme nicht mehr: dann schreibt der Generator
gar nichts und nennt die Dateien. Raten, was davon bleiben soll, waere
schlimmer.

ZWEI PHASEN:
Erst wird geplant und geprueft (:func:`planen`), dann geschrieben
(:func:`ausfuehren`). Ein Fehler in der dritten Datei laesst so nicht zwei
neue und eine alte zurueck.

VERWAIST:
Gibt es eine Formel nicht mehr, gibt es ihre Seite nicht mehr -- es sei denn,
unter der Linie steht etwas. Dann bleibt die Seite stehen, oben mit einem
Hinweis, bis der Text an der richtigen Seite steht; ein Test haelt das fest.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Optional, Sequence, Tuple

from opencivil.notizbuch.namen import sortierschluessel, vergleichsname

#: Die Linie zwischen erzeugtem und eigenem Teil -- in Obsidian und auf der
#: Seite unsichtbar, im Quelltext unuebersehbar.
LINIE = "<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->"

#: Die Ordner in der Reihenfolge, in der das Verzeichnis sie fuehrt.
ORDNER = ("", "Formelsammlung", "Formelsammlung/Themen", "Formelsammlung/Formeln",
          "Python", "Notizen")

#: Was im Tresor kein Inhalt ist: die Arbeitsdateien von Obsidian.
_VERBORGEN = re.compile(r"(^|/)\.")


class TresorFehler(Exception):
    """Der Generator wuerde etwas ueberschreiben, das ihm nicht gehoert."""


@dataclass(frozen=True)
class Seite:
    """Eine erzeugte Seite, bevor sie geschrieben ist."""

    pfad: str
    """Im Tresor, mit ``/`` getrennt: ``Formelsammlung/Formeln/Statische Höhe.md``."""

    art: str
    """``formel``, ``thema``, ``verzeichnis`` oder ``modul``."""

    rumpf: str
    """Der erzeugte Teil, ohne Kopf und ohne Linie."""

    eigenschaften: Tuple[Tuple[str, Any], ...] = ()
    """Weitere Eintraege des Kopfs, in dieser Folge -- Text oder Liste von Texten."""

    eigener_teil: bool = False
    """Ob unter einer Linie von Hand weitergeschrieben wird."""

    rang: int = 0
    """Wo die Seite im Verzeichnis steht, innerhalb ihres Ordners."""

    verzeichnis: Tuple[Tuple[str, Any], ...] = ()
    """Was das Verzeichnis zusaetzlich ueber die Seite weiss: Zeichen, Themen ..."""

    @property
    def name(self) -> str:
        return PurePosixPath(self.pfad).stem


@dataclass
class Datei:
    """Eine Seite, wie sie im Tresor liegt."""

    erzeugt: Optional[str]
    """Die abgelegte Pruefsumme -- ``None`` bei einer Notiz von Hand."""

    stimmt: bool
    """Ob die Pruefsumme zum Inhalt passt."""

    eigen: Optional[str]
    """Alles nach der Linie, oder ``None``, wenn es keine gibt."""

    eigenschaften: Dict[str, str] = field(default_factory=dict)


@dataclass
class Plan:
    """Was ein Lauf des Generators taete."""

    schreiben: Dict[str, str] = field(default_factory=dict)
    loeschen: List[str] = field(default_factory=list)
    verwaist: List[str] = field(default_factory=list)
    unveraendert: List[str] = field(default_factory=list)
    fehler: List[str] = field(default_factory=list)

    @property
    def nichts_zu_tun(self) -> bool:
        return not (self.schreiben or self.loeschen or self.fehler)


# ---------------------------------------------------------------------------
# Eine Datei
# ---------------------------------------------------------------------------


def pruefsumme(text: str) -> str:
    """Die ersten zwoelf Zeichen von SHA-256, Windows-Zeilenenden zaehlen nicht."""
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()[:12]


def _wert(wert: Any) -> str:
    """
    Ein Eintrag im Kopf, wie Obsidian ihn als Eigenschaft liest. Text in
    Anfuehrungszeichen, sobald er mehr als Buchstaben enthaelt: ein ``:`` mit
    Leerzeichen danach oder ein ``#`` hiesse sonst etwas anderes.
    """
    if isinstance(wert, bool):
        return "true" if wert else "false"
    if isinstance(wert, (list, tuple)):
        return "[" + ", ".join(_wert(w) for w in wert) + "]"
    text = str(wert)
    if re.fullmatch(r"[A-Za-zÄÖÜäöüß][\w\-]*", text):
        return text
    return json.dumps(text, ensure_ascii=False)


def text_der_seite(seite: Seite, eigen: str = "") -> str:
    """Die Datei, wie sie geschrieben wird -- mit dem eigenen Teil, wo es einen gibt."""
    kopf = "\n".join([f"art: {_wert(seite.art)}", f"tags: {_wert([seite.art])}",
                      *(f"{k}: {_wert(v)}" for k, v in seite.eigenschaften)])
    rumpf = seite.rumpf.strip("\n") + "\n"
    if seite.eigener_teil:
        rumpf += "\n" + LINIE + "\n"
    summe = pruefsumme(kopf + "\n---\n" + rumpf)
    text = f"---\nerzeugt: {summe}\n{kopf}\n---\n{rumpf}"
    return text + eigen if seite.eigener_teil else text


def zerlegen(text: str) -> Datei:
    """Liest Kopf, Pruefsumme und eigenen Teil einer Datei aus dem Tresor."""
    text = text.replace("\r\n", "\n")
    if not text.startswith("---\n"):
        return Datei(erzeugt=None, stimmt=False, eigen=None)
    ende = text.find("\n---\n", 3)
    if ende < 0:
        return Datei(erzeugt=None, stimmt=False, eigen=None)
    zeilen = text[4:ende].split("\n")
    eigenschaften = {}
    for zeile in zeilen:
        schluessel, _, wert = zeile.partition(":")
        eigenschaften[schluessel.strip()] = wert.strip()
    erzeugt = eigenschaften.pop("erzeugt", None)
    if erzeugt is None:
        return Datei(erzeugt=None, stimmt=False, eigen=None, eigenschaften=eigenschaften)
    kopf = "\n".join(z for z in zeilen if not z.startswith("erzeugt:"))
    rest = text[ende + 5:]
    stelle = rest.find("\n" + LINIE + "\n")
    if stelle >= 0:
        schnitt = stelle + len(LINIE) + 2
        rumpf, eigen = rest[:schnitt], rest[schnitt:]
    else:
        rumpf, eigen = rest, None
    return Datei(erzeugt=erzeugt, stimmt=pruefsumme(kopf + "\n---\n" + rumpf) == erzeugt,
                 eigen=eigen, eigenschaften=eigenschaften)


def _verwaist(pfad: str, art: str) -> Seite:
    return Seite(
        pfad=pfad, art=art, eigener_teil=True, eigenschaften=(("verwaist", True),),
        rumpf=("> [!warning] Verwaist\n"
               "> Im Code gibt es diese Seite nicht mehr. Den Text unter der Linie an die "
               "richtige Seite verschieben, dann diese Datei löschen."))


# ---------------------------------------------------------------------------
# Der Tresor
# ---------------------------------------------------------------------------


def vorhandene(wurzel: Path) -> Dict[str, str]:
    """Jede Markdown-Datei im Tresor, ohne die Arbeitsdateien von Obsidian."""
    if not wurzel.is_dir():
        return {}
    heraus = {}
    for pfad in sorted(wurzel.rglob("*.md")):
        relativ = pfad.relative_to(wurzel).as_posix()
        if not _VERBORGEN.search(relativ):
            heraus[relativ] = pfad.read_text(encoding="utf-8").replace("\r\n", "\n")
    return heraus


def planen(seiten: Sequence[Seite], wurzel: Path) -> Plan:
    """Was zu schreiben, zu loeschen und zu beanstanden waere -- ohne etwas anzufassen."""
    plan = Plan()
    neu = {s.pfad: s for s in seiten}
    if len(neu) != len(seiten):
        doppelt = sorted({s.pfad for s in seiten if sum(t.pfad == s.pfad for t in seiten) > 1})
        plan.fehler += [f"{p}: zweimal erzeugt." for p in doppelt]
    vorhanden = vorhandene(wurzel)
    namen = {vergleichsname(s.name): s.pfad for s in seiten}

    for pfad, alt in vorhanden.items():
        datei = zerlegen(alt)
        if datei.erzeugt is None:
            andere = namen.get(vergleichsname(PurePosixPath(pfad).stem))
            if andere is not None:
                plan.fehler.append(
                    f"{pfad}: eine Notiz von Hand heisst wie die erzeugte Seite {andere}.")
            continue
        if not datei.stimmt:
            plan.fehler.append(f"{pfad}: oben von Hand geändert – über der Linie "
                               "schreibt nur der Generator.")
            continue
        if pfad in neu:
            continue
        if datei.eigen is None or not datei.eigen.strip():
            plan.loeschen.append(pfad)
            continue
        plan.verwaist.append(pfad)
        text = text_der_seite(_verwaist(pfad, datei.eigenschaften.get("art", "")), datei.eigen)
        if text != alt:
            plan.schreiben[pfad] = text

    beanstandet = {f.split(":", 1)[0] for f in plan.fehler}
    for pfad, seite in neu.items():
        if pfad in beanstandet:
            continue
        alt = vorhanden.get(pfad)
        eigen = ""
        if alt is not None and seite.eigener_teil:
            eigen = zerlegen(alt).eigen
            if eigen is None:
                plan.fehler.append(f"{pfad}: die Linie fehlt – wo der eigene Teil "
                                   "beginnt, ist nicht mehr zu erkennen.")
                continue
        text = text_der_seite(seite, eigen)
        if text == alt:
            plan.unveraendert.append(pfad)
        else:
            plan.schreiben[pfad] = text
    return plan


def ausfuehren(plan: Plan, wurzel: Path) -> None:
    """Schreibt und loescht, was der Plan sagt -- nur, wenn er nichts beanstandet."""
    if plan.fehler:
        raise TresorFehler("Im Notizbuch wurde nichts geschrieben:\n  "
                           + "\n  ".join(plan.fehler))
    for pfad, text in plan.schreiben.items():
        ziel = wurzel / pfad
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_text(text, encoding="utf-8", newline="\n")
    for pfad in plan.loeschen:
        (wurzel / pfad).unlink()


# ---------------------------------------------------------------------------
# Das Verzeichnis fuer die Oberflaeche
# ---------------------------------------------------------------------------


def verzeichnis(seiten: Sequence[Seite], wurzel: Path) -> List[Dict[str, Any]]:
    """
    Jede Seite des Tresors, erzeugt oder von Hand, in der Folge des Baums:
    Start, Formelsammlung (Uebersicht, Themen in Rechenfolge, Formeln von A
    bis Z), Python, Notizen, dann alles andere. Eine Ordnerseite -- sie heisst
    wie ihr Ordner -- steht vor den uebrigen.
    """
    erzeugt = {s.pfad: s for s in seiten}
    eintraege = []
    for pfad in sorted(set(vorhandene(wurzel)) | set(erzeugt)):
        seite = erzeugt.get(pfad)
        name = PurePosixPath(pfad).stem
        eintrag: Dict[str, Any] = {"name": name, "pfad": pfad,
                                   "art": seite.art if seite else "notiz"}
        if seite is not None:
            eintrag.update(dict(seite.verzeichnis))
        eintraege.append((_folge(pfad, seite.rang if seite else 0), eintrag))
    return [e for _, e in sorted(eintraege, key=lambda paar: paar[0])]


def _folge(pfad: str, rang: int) -> tuple:
    teil = PurePosixPath(pfad)
    ordner = "" if str(teil.parent) == "." else teil.parent.as_posix()
    stelle = ORDNER.index(ordner) if ordner in ORDNER else len(ORDNER)
    ordnerseite = teil.stem == PurePosixPath(ordner).name
    return (stelle, sortierschluessel(ordner) if stelle == len(ORDNER) else "",
            not ordnerseite, rang, sortierschluessel(teil.stem))


def anhaenge(wurzel: Path) -> List[str]:
    """Was ausser Seiten im Tresor liegt -- Bilder, die eine Seite einbettet."""
    if not wurzel.is_dir():
        return []
    return sorted(p.relative_to(wurzel).as_posix() for p in wurzel.rglob("*")
                  if p.is_file() and p.suffix != ".md"
                  and not _VERBORGEN.search(p.relative_to(wurzel).as_posix()))
