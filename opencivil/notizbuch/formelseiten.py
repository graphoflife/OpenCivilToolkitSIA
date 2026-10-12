"""
opencivil/notizbuch/formelseiten.py -- die Formelsammlung als Seiten.

VERANTWORTUNG:
Je Formel eine Seite, je Thema eine, dazu die Uebersicht -- aus denselben
Laeufen wie die Formelsammlung (:func:`opencivil.bericht.formelsammlung.laeufe`),
die zusammen jede Formel des Werkzeugs schreiben. Welche Formel hineingehoert
und wie sie heisst, sagt die Formelsammlung; hier wird nur gesetzt.

WAS EINE FORMELSEITE ZEIGT:
Die Formel ohne Zahlen -- in jeder Fassung, wenn es mehrere gibt --, ihre
Normstelle oder dass sie fehlt, die Groessen samt Herkunft, dieselbe Formel
mit den Zahlen eines Projekts, welche Formeln sie brauchen, wo sie im Code
steht und zu welchen Themen sie gehoert. Darunter, von Hand, die Theorie.

WOHER EINE GROESSE KOMMT:
Aus der Rechnung selbst: je Lauf merkt sich :func:`sammeln`, welche Formel
einen Wert zuletzt geschrieben hat. Braucht eine spaetere Formel ihn, ist
das ihre Herkunft -- als Link. Schrieb ihn keine Formel der Sammlung, sagt
der Wert selbst, woher er kommt: Eingabe, Vorgabe oder Zwischenwert.
Die Laeufe bleiben getrennt: ``querschnitt.q1`` meint in jedem Projekt eine
andere Platte.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

from opencivil.bericht import formelsammlung as fs
from opencivil.bericht.markdown import absatz_markdown, formel_in_zelle, text_markdown
from opencivil.core.latex import ohne_namen_im_index
from opencivil.core.protokoll import GleichungBlock
from opencivil.core.wert import Quelle, Wert
from opencivil.notizbuch.namen import sortierschluessel
from opencivil.notizbuch.tresor import Seite

FORMELN = "Formelsammlung/Formeln"
THEMEN = "Formelsammlung/Themen"
UEBERSICHT = "Formelsammlung/Formelsammlung.md"

#: Wie die Uebersicht die Themen gruppiert -- nach dem Bestandteil, zu dem
#: sie gehoeren (``Thema.art`` der Formelsammlung).
BEREICHE = {"beton": "Baustoffe", "betonstahl": "Baustoffe", "querschnitt": "Platte",
            "querschnittsanalyse": "Querschnittsanalyse", "balkensystem": "Balkensysteme"}

#: Woher ein Wert kommt, den keine Formel der Sammlung geschrieben hat.
ANGABEN = {Quelle.EINGABE: "Eingabe", Quelle.UEBERSCHRIEBEN: "Eingabe",
           Quelle.VORGABE: "Vorgabe", Quelle.BERECHNET: "Zwischenwert"}


@dataclass
class Groessenzeile:
    """Eine Zeile der Tabelle «Groessen»."""

    zeichen: str
    bedeutung: str = ""
    einheit: str = ""
    woher: Dict[Tuple[str, str], None] = field(default_factory=dict)
    """Geordnete Menge: ``("seite", Name)`` oder ``("angabe", Text)``."""


@dataclass
class Fassung:
    """Eine Formel, wie sie zum ersten Mal dasteht -- mit allem, was ihre Vorkommen sagen."""

    block: GleichungBlock
    projekt: str
    groessen: Dict[str, Groessenzeile] = field(default_factory=dict)
    """Je Platzhalter der Vorlage."""


@dataclass
class Formel:
    """Alles zu einem Formelnamen, ueber alle Laeufe."""

    name: str
    fassungen: Dict[tuple, Fassung] = field(default_factory=dict)
    themen: Dict[str, None] = field(default_factory=dict)
    codestellen: Dict[str, None] = field(default_factory=dict)
    gebraucht_von: Dict[str, None] = field(default_factory=dict)

    @property
    def referenzen(self) -> List[str]:
        return list(dict.fromkeys(f.block.referenz for f in self.fassungen.values()
                                  if f.block.referenz))

    @property
    def zeichen(self) -> List[str]:
        return list(dict.fromkeys(z for z in (fs.ergebniszeichen(f.block)
                                              for f in self.fassungen.values()) if z))


@dataclass
class Thema:
    name: str
    bereich: str
    formeln: Dict[str, None] = field(default_factory=dict)
    erklaerungen: List[str] = field(default_factory=list)


def sammeln() -> Tuple[Dict[str, Formel], Dict[str, Thema]]:
    """Jede Formel und jedes Thema der Sammlung, in der Folge ihres ersten Auftretens."""
    formeln: Dict[str, Formel] = {}
    themen: Dict[str, Thema] = {}
    for lauf in fs.laeufe():
        zuletzt: Dict[str, str] = {}
        for block in lauf.alle_bloecke():
            if not isinstance(block, GleichungBlock):
                continue
            if fs.in_sammlung(block):
                _vorkommen(block, lauf.kopftitel, formeln, zuletzt)
                thema = themen.setdefault(block.thema, Thema(block.thema, ""))
                thema.formeln[fs.formelname(block)] = None
            if block.wert_id:
                zuletzt[block.wert_id] = fs.formelname(block) if fs.in_sammlung(block) else ""
    for thema in fs.vollstaendig():
        if thema.name in themen:
            themen[thema.name].bereich = BEREICHE.get(thema.art, "")
            themen[thema.name].erklaerungen = [e.text for e in thema.erklaerungen]
    return formeln, themen


def _vorkommen(block: GleichungBlock, projekt: str, formeln: Dict[str, Formel],
               zuletzt: Dict[str, str]) -> None:
    name = fs.formelname(block)
    formel = formeln.setdefault(name, Formel(name))
    fassung = formel.fassungen.setdefault(fs.schluessel(block), Fassung(block, projekt))
    formel.themen[block.thema] = None
    formel.codestellen[block.codestelle] = None
    if block.formelzeile is None:
        return
    for platzhalter, wert in block.formelzeile.eingaben:
        groesse = fassung.groessen.setdefault(platzhalter, Groessenzeile(
            ohne_namen_im_index(wert.symbol), einheit=wert.einheit.beschriftung or ""))
        if ohne_namen_im_index(wert.symbol) != groesse.zeichen:
            # Derselbe Platzhalter mit einem anderen Wert -- f_yd statt f_yk:
            # die Zeile spricht vom gezeigten Zeichen.
            continue
        groesse.bedeutung = groesse.bedeutung or wert.beschreibung
        quelle = zuletzt.get(wert.id, "")
        if quelle == name:
            continue
        if quelle:
            groesse.woher[("seite", quelle)] = None
            formeln[quelle].gebraucht_von[name] = None
        else:
            groesse.woher[("angabe", _angabe(wert))] = None


def _angabe(wert: Wert) -> str:
    return ANGABEN.get(wert.quelle, "Zwischenwert")


# ---------------------------------------------------------------------------
# Seiten
# ---------------------------------------------------------------------------


def seiten(formeln: Optional[Dict[str, Formel]] = None,
           themen: Optional[Dict[str, Thema]] = None,
           codestelle: Optional[Callable[[str], str]] = None) -> List[Seite]:
    """
    Die Uebersicht, je Thema eine Seite und je Formel eine. ``codestelle``
    macht aus ``modul:Funktion`` einen Link auf die Seite des Moduls -- ohne
    steht die Stelle als Code da.
    """
    if formeln is None or themen is None:
        formeln, themen = sammeln()
    codestelle = codestelle or (lambda stelle: f"`{stelle}`")
    heraus = [_uebersicht(formeln, themen, codestelle)]
    heraus += [_themenseite(t, rang) for rang, t in enumerate(themen.values())]
    heraus += [_formelseite(f, codestelle) for f in formeln.values()]
    return heraus


def _formelseite(formel: Formel, codestelle: Callable[[str], str]) -> Seite:
    # Was ohne Zahlen gleich aussieht, ist dieselbe Formel -- wie in der
    # Formelsammlung steht sie einmal da.
    gesetzt: Dict[str, Fassung] = {}
    for fassung in formel.fassungen.values():
        gesetzt.setdefault(fs.symbolisch(fassung.block).latex, fassung)
    fassungen = list(gesetzt.values())
    referenzen = formel.referenzen
    zeilen: List[str] = []
    if referenzen:
        kopf = "Normstelle" if len(referenzen) == 1 else "Normstellen"
        zeilen += [f"> [!info] {kopf}", "> " + " · ".join(map(text_markdown, referenzen)), ""]
    else:
        zeilen += ["> [!warning] Normstelle fehlt noch",
                   "> Sie kommt vom Benutzer und wird im Code eingetragen – von dort "
                   "steht sie im Bericht und hier.", ""]

    for fassung in fassungen:
        titel = fs.ohne_zahlenangabe(fassung.block.titel)
        if len(fassungen) > 1 or titel != formel.name:
            zeilen += [f"*In der Herleitung: «{text_markdown(titel)}»*", ""]
        zeilen += ["$$", fs.symbolisch(fassung.block).latex, "$$", ""]

    groessen = _groessen(fassungen)
    if groessen:
        zeilen += ["## Grössen", "", "| Zeichen | Bedeutung | Einheit | Woher |",
                   "| --- | --- | --- | --- |", *groessen, ""]

    mit_zahlen = [f for f in fassungen if not f.block.ansatz]
    if mit_zahlen:
        zeilen += ["## Beispiel", ""]
        for fassung in mit_zahlen:
            zeilen += [f"Mit den Zahlen aus dem {text_markdown(fassung.projekt)}:", "",
                       "$$", fassung.block.latex, "$$", ""]

    if formel.gebraucht_von:
        zeilen += ["## Gebraucht von", "",
                   *(f"- [[{n}]]" for n in sorted(formel.gebraucht_von, key=sortierschluessel)),
                   ""]
    zeilen += ["## Im Code", "", *(f"- {codestelle(c)}" for c in sorted(formel.codestellen)), ""]
    zeilen += ["## Themen", "", *(f"- [[{t}]]" for t in formel.themen), ""]

    eigenschaften = []
    if referenzen:
        eigenschaften.append(("normstelle", referenzen[0] if len(referenzen) == 1
                              else referenzen))
    return Seite(
        pfad=f"{FORMELN}/{formel.name}.md", art="formel", rumpf="\n".join(zeilen),
        eigenschaften=tuple(eigenschaften), eigener_teil=True,
        verzeichnis=(("zeichen", formel.zeichen), ("themen", list(formel.themen))))


def _groessen(fassungen: List[Fassung]) -> List[str]:
    """Die Zeilen der Tabelle -- dieselbe Groessenzeile in mehreren Fassungen einmal."""
    zeilen: Dict[str, Groessenzeile] = {}
    for fassung in fassungen:
        for groesse in fassung.groessen.values():
            ziel = zeilen.setdefault(groesse.zeichen, Groessenzeile(groesse.zeichen,
                                                              einheit=groesse.einheit))
            ziel.bedeutung = ziel.bedeutung or groesse.bedeutung
            ziel.woher.update(groesse.woher)
    return [f"| {formel_in_zelle(g.zeichen)} | {text_markdown(g.bedeutung) or '–'} | "
            f"{text_markdown(g.einheit) or '–'} | {_woher(g)} |"
            for g in zeilen.values()]


def _woher(groesse: Groessenzeile) -> str:
    teile = [f"[[{wert}]]" if art == "seite" else wert for art, wert in groesse.woher]
    return ", ".join(teile) or "–"


def _themenseite(thema: Thema, rang: int) -> Seite:
    anzahl = len(thema.formeln)
    zeilen = [f"> [!abstract] {thema.bereich or 'Thema'}",
              f"> {anzahl} {'Formel' if anzahl == 1 else 'Formeln'}, in der Folge, "
              "in der gerechnet wird.", ""]
    if thema.erklaerungen:
        zeilen += ["## Was die Rechnung dazu sagt", ""]
        for text in thema.erklaerungen:
            zeilen += [absatz_markdown(text), ""]
    zeilen += ["## Formeln", "", *(f"{i}. [[{n}]]" for i, n in enumerate(thema.formeln, 1)),
               ""]
    return Seite(pfad=f"{THEMEN}/{thema.name}.md", art="thema", rumpf="\n".join(zeilen),
                 eigener_teil=True, rang=rang,
                 verzeichnis=(("bereich", thema.bereich),))


def _uebersicht(formeln: Dict[str, Formel], themen: Dict[str, Thema],
                codestelle: Callable[[str], str]) -> Seite:
    zeilen = [
        "Jede Formel des Werkzeugs steht auf einer eigenen Seite: die Formel, ihre "
        "Normstelle, die Grössen mit ihrer Herkunft, ein Zahlenbeispiel, die Stelle "
        "im Code – und darunter, von Hand, die Theorie. Gesammelt aus dem "
        "Beispielprojekt und dem Prüfprojekt «Jeder Nachweis», die zusammen jeden "
        "Nachweis rechnen; geschrieben von `python3 -m opencivil.web.bruecke`.",
        "", "## Themen", ""]
    bereiche: Dict[str, List[Thema]] = {}
    for thema in themen.values():
        bereiche.setdefault(thema.bereich or "Weitere", []).append(thema)
    for bereich, liste in bereiche.items():
        zeilen += [f"**{bereich}**", ""]
        zeilen += [f"- [[{t.name}]] · {len(t.formeln)}" for t in liste]
        zeilen += [""]

    zeilen += ["## Formeln von A bis Z", ""]
    for name in sorted(formeln, key=sortierschluessel):
        zeichen = formeln[name].zeichen
        zeilen.append(f"- [[{name}]]" + (f" · ${zeichen[0]}$" if zeichen else ""))
    zeilen += [""]

    offen = [f for f in formeln.values() if not f.referenzen]
    zeilen += ["## Normstelle fehlt noch", "",
               f"{len(offen)} von {len(formeln)} Formeln haben im Code keine Normstelle. "
               "Die Stellen in SIA 262 liefert der Benutzer; eingetragen werden sie im "
               "Code, an der genannten Stelle – von dort kommen sie in Bericht und "
               "Notizbuch.", ""]
    for formel in sorted(offen, key=lambda f: sortierschluessel(f.name)):
        stellen = ", ".join(codestelle(c) for c in sorted(formel.codestellen))
        zeilen.append(f"- [[{formel.name}]] · {stellen}")
    return Seite(pfad=UEBERSICHT, art="verzeichnis", rumpf="\n".join(zeilen))
