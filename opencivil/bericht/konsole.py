"""
opencivil/bericht/konsole.py -- Ausgabe einer Loesung auf der Konsole.

VERANTWORTUNG:
Macht das Backend fuer sich allein bedienbar. Die LaTeX-Formeln werden roh
ausgegeben -- nicht gesetzt, sondern als Quelltext, damit man sie lesen,
pruefen und direkt weiterverwenden kann.

Der Bericht ist reine Darstellung: was darin steht und in welcher Folge,
legt :func:`opencivil.bericht.gliederung.bericht` fest -- fuer die Konsole
wie fuer das LaTeX-Dokument. Hier wird es nur als Text gesetzt.

EIGENSTAENDIG NUTZBAR::

    from opencivil.bericht.konsole import drucke
    drucke(loesung, titel="Materialkennwerte C30/37")
"""

from __future__ import annotations

import shutil
from typing import TYPE_CHECKING, Iterable, List, Optional, TextIO

from opencivil.bericht.gliederung import bericht
from opencivil.core.protokoll import (
    GleichungBlock, HinweisArt, HinweisBlock, Protokoll, TabellenBlock, Tafel,
    TextBlock, TitelBlock, UnterprotokollBlock, darstellen,
)
from opencivil.core.latex import Mathe, Zelle
from opencivil.core.rechenwerk import Loesung
from opencivil.core.wert import Wert

if TYPE_CHECKING:
    from opencivil.bericht.zusammenfassung import Zusammenfassung
    from opencivil.projekt import Aufbau

_BREITE = min(shutil.get_terminal_size((100, 24)).columns, 100)


# ===========================================================================
# Hilfen
# ===========================================================================


def _linie(zeichen: str = "-") -> str:
    return zeichen * _BREITE


def _ueberschrift(text: str, zeichen: str = "=") -> List[str]:
    return [_linie(zeichen), text, _linie(zeichen)]


def _umbrechen(text: str, einzug: int = 0) -> List[str]:
    """Bricht Fliesstext auf die Terminalbreite um."""
    import textwrap

    breite = max(_BREITE - einzug, 20)
    return [
        " " * einzug + zeile
        for zeile in textwrap.wrap(text, breite) or [""]
    ]


# ===========================================================================
# Protokoll
# ===========================================================================


def protokoll_zeilen(protokoll: Protokoll, tiefe: int = 0) -> List[str]:
    """Wandelt eine Mitschrift in Konsolenzeilen um."""
    return [zeile for teil in darstellen(protokoll, TAFEL, tiefe) for zeile in teil]


def _vorspann(tiefe: int) -> str:
    """Ein Unterprotokoll steht je Stufe zwei Zeichen weiter innen."""
    return "  " * tiefe


def _titel(block: TitelBlock, tiefe: int) -> List[str]:
    if block.ebene <= 1:
        return [""] + _ueberschrift(block.text)
    vorspann = _vorspann(tiefe)
    return ["", f"{vorspann}{block.text}", f"{vorspann}{'-' * len(block.text)}"]


def _text(block: TextBlock, tiefe: int) -> List[str]:
    return [""] + _umbrechen(block.text, len(_vorspann(tiefe)))


def _gleichung(block: GleichungBlock, tiefe: int) -> List[str]:
    vorspann = _vorspann(tiefe)
    zeilen = [""]
    kopf = block.titel or block.wert_id
    if kopf:
        nachweis = f"   [{block.referenz}]" if block.referenz else ""
        zeilen.append(f"{vorspann}{kopf}{nachweis}")
    return zeilen + [f"{vorspann}    {teil}" for teil in block.latex.splitlines()]


def _tabelle(block: TabellenBlock, tiefe: int) -> List[str]:
    vorspann = _vorspann(tiefe)
    zeilen = [""] + ([f"{vorspann}{block.titel}"] if block.titel else [])
    return zeilen + _tabelle_zeilen(block, len(vorspann) + 4)


_MARKE = {HinweisArt.INFO: "i", HinweisArt.WARNUNG: "!", HinweisArt.ANNAHME: "*"}


def _hinweis(block: HinweisBlock, tiefe: int) -> List[str]:
    return _umbrechen(
        f"[{_MARKE[block.art]}] {block.art.beschriftung}: {block.text}",
        len(_vorspann(tiefe)))


def _unterprotokoll(block: UnterprotokollBlock, tiefe: int) -> List[str]:
    return (["", f"{_vorspann(tiefe)}> {block.titel}"]
            + protokoll_zeilen(block.protokoll, tiefe + 1))


#: Je Blockart, wie die Konsole sie setzt -- jede als Zeilen.
TAFEL: Tafel[List[str]] = {
    TitelBlock: _titel,
    TextBlock: _text,
    GleichungBlock: _gleichung,
    TabellenBlock: _tabelle,
    HinweisBlock: _hinweis,
    UnterprotokollBlock: _unterprotokoll,
}


def _tabelle_zeilen(block: TabellenBlock, einzug: int) -> List[str]:
    """
    Setzt die Tabelle als Text -- Spaltenbreiten nach dem laengsten Eintrag.

    Zahlen rechts, Text links, wenn die Tabelle es sagt (``ausrichtung`` wie
    in LaTeX, ``l``, ``c`` oder ``r`` je Spalte). Ohne Angabe alles rechts.
    Frueher galt immer rechts, auch wo die Tabelle ``l`` verlangte -- im
    LaTeX-Dokument stand sie richtig, auf der Konsole nicht.
    """
    setzen = {"l": str.ljust, "L": str.ljust, "c": str.center}
    alle = [[_zelle(z) for z in block.kopf]] + [[_zelle(z) for z in zeile]
                                                for zeile in block.zeilen]
    breiten = [max(len(z[i]) for z in alle) for i in range(len(block.kopf))]
    ausrichtung = (block.ausrichtung or "").ljust(len(breiten), "r")
    vorspann = " " * einzug

    def zeile(zellen: Iterable[str]) -> str:
        return (vorspann + "  ".join(
            setzen.get(a, str.rjust)(t, b)
            for t, b, a in zip(zellen, breiten, ausrichtung))).rstrip()

    ausgabe = [zeile(alle[0]), vorspann + "  ".join("-" * b for b in breiten)]
    ausgabe.extend(zeile(z) for z in alle[1:])
    return ausgabe


def _zelle(zelle: Zelle) -> str:
    """Text wie er ist; eine Formel als Quelltext, wie ueberall auf der Konsole."""
    return zelle.latex if isinstance(zelle, Mathe) else zelle


# ===========================================================================
# Zusammenfassung
# ===========================================================================


def _wert_text(wert: Optional[Wert]) -> str:
    """Zahl und Einheit, ohne Formelzeichen -- die Spalte sagt, was es ist."""
    if wert is None:
        return "–"
    einheit = wert.einheit.beschriftung if wert.einheit.name not in ("", "-") else ""
    return f"{wert.formatiert()} {einheit}".rstrip()


def zusammenfassung(zusammenfassung: "Zusammenfassung") -> str:
    """
    Je Platte eine Tabelle der Nachweise -- die Zusammenfassung der
    Oberflaeche, fuer die Konsole.

    Welche Zeilen dastehen, entscheidet
    :func:`opencivil.bericht.zusammenfassung.zusammenfassen`; hier wird nur
    gesetzt. Je Platte eine eigene Tabelle, weil die Urteilsnamen die Platte
    nicht nennen -- zwei Platten mit einer Kombination «Feld» stuenden sonst
    als zwei gleiche Zeilen da.
    """
    zeilen: List[str] = []
    for platte in zusammenfassung.platten:
        zeilen += [platte.name, "-" * len(platte.name)]
        if platte.zeilen:
            tabelle = TabellenBlock(
                kopf=["Nachweis", "Fall", "Widerstand", "Einwirkung", "α_eff", ""],
                zeilen=[[z.nachweis, z.fall or "–",
                         _wert_text(z.widerstand), _wert_text(z.einwirkung),
                         z.urteil.gradtext(),
                         "erfüllt" if z.urteil.erfuellt else "NICHT ERFÜLLT"]
                        for z in platte.zeilen],
                ausrichtung="llrrrl")
            zeilen += _tabelle_zeilen(tabelle, 2)
        else:
            zeilen.append("  Kein Nachweis geführt.")
        if platte.stille:
            zeilen += ["", "  Nicht geführt, geht aber nicht auf:"]
            zeilen += [f"    {z.nachweis}{f' – {z.fall}' if z.fall else ''}: "
                       f"α_eff = {z.urteil.gradtext()}" for z in platte.stille]
        zeilen.append("")

    if zusammenfassung.gefuehrt:
        zeilen.append("Alle geführten Nachweise erfüllt."
                      if zusammenfassung.erfuellt
                      else "Mindestens ein Nachweis ist NICHT erfüllt.")
    if zusammenfassung.warnungen:
        zeilen += ["", "Hinweise:"] + [f"  - {w}" for w in zusammenfassung.warnungen]
    return "\n".join(zeilen).rstrip() + "\n"


# ===========================================================================
# Ausgabe
# ===========================================================================


def als_text(
    loesung: Loesung,
    titel: str = "Berechnung",
    *,
    aufbau: Optional["Aufbau"] = None,
) -> str:
    """Der ganze Bericht als Text -- mit ``aufbau`` die Nachweise je Platte."""
    protokoll = bericht(loesung, titel=titel, aufbau=aufbau)
    return "\n".join(_ueberschrift(protokoll.kopftitel) + protokoll_zeilen(protokoll))


def drucke(
    loesung: Loesung,
    titel: str = "Berechnung",
    datei: Optional[TextIO] = None,
    *,
    aufbau: Optional["Aufbau"] = None,
) -> None:
    """Schreibt den Bericht auf die Konsole (oder einen anderen Datenstrom)."""
    print(als_text(loesung, titel, aufbau=aufbau), file=datei)
