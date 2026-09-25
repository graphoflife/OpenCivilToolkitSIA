"""
opencivil/bericht/konsole.py -- Ausgabe einer Loesung auf der Konsole.

VERANTWORTUNG:
Macht das Backend fuer sich allein bedienbar. Die LaTeX-Formeln werden roh
ausgegeben -- nicht gesetzt, sondern als Quelltext, damit man sie lesen,
pruefen und direkt weiterverwenden kann.

Der Bericht ist reine Darstellung: er liest eine :class:`Loesung` und erzeugt
Text. Er rechnet nichts und weiss nichts ueber Beton oder Stahl. Genau darum
ist er austauschbar -- das LaTeX-Dokument nutzt dieselbe Loesung.

EIGENSTAENDIG NUTZBAR::

    from opencivil.bericht.konsole import drucke
    drucke(loesung, titel="Materialkennwerte C30/37")
"""

from __future__ import annotations

import shutil
from typing import TYPE_CHECKING, Iterable, List, Optional, Sequence, TextIO

from opencivil.core.protokoll import (
    GleichungBlock, HinweisArt, HinweisBlock, Protokoll, TabellenBlock, Tafel,
    TextBlock, TitelBlock, UnterprotokollBlock, darstellen,
)
from opencivil.core.berechnung import NachweisUrteil
from opencivil.core.latex import Mathe, Zelle
from opencivil.core.rechenwerk import Loesung
from opencivil.core.wert import Quelle, Wert

if TYPE_CHECKING:
    from opencivil.bericht.zusammenfassung import Zusammenfassung

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
    setzen = {"l": str.ljust, "c": str.center}
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
# Loesung
# ===========================================================================


def loesung_zeilen(loesung: Loesung, titel: str = "Berechnung") -> List[str]:
    """Baut den vollstaendigen Konsolenbericht einer Loesung."""
    zeilen = _ueberschrift(titel)

    zeilen.append("")
    zeilen.append(
        f"{len(loesung.reihenfolge)} Berechnungen ausgeführt, "
        f"{len(loesung.werte)} Werte bestimmt."
    )

    zeilen.extend(_abschnitt_herleitung(loesung))
    zeilen.extend(_abschnitt_werte(loesung))
    zeilen.extend(_abschnitt_nachweise(loesung))
    zeilen.extend(_abschnitt_luecken(loesung))
    return zeilen


def _abschnitt_herleitung(loesung: Loesung) -> List[str]:
    if loesung.protokoll.ist_leer:
        return []
    zeilen = [""] + _ueberschrift("Herleitung", "=")
    zeilen.extend(protokoll_zeilen(loesung.protokoll))
    return zeilen


def _abschnitt_werte(loesung: Loesung) -> List[str]:
    if not loesung.werte:
        return []
    zeilen = ["", ""] + _ueberschrift("Werte", "=") + [""]

    namen = sorted(loesung.werte)
    breite_id = max(len(n) for n in namen)
    for name in namen:
        wert = loesung.werte[name]
        einheit = wert.einheit.name if wert.einheit.name not in ("", "-") else ""
        marke = {
            Quelle.EINGABE: "Eingabe",
            Quelle.VORGABE: "Vorgabe",
            Quelle.BERECHNET: "",
            Quelle.UEBERSCHRIEBEN: "ÜBERSCHRIEBEN",
        }[wert.quelle]
        zeilen.append(
            f"  {name.ljust(breite_id)}  {wert.formatiert().rjust(12)} {einheit.ljust(8)}"
            f" {marke}".rstrip()
        )
    return zeilen


def _abschnitt_nachweise(loesung: Loesung) -> List[str]:
    # Nur die gefuehrten. Ein ausgeschalteter Nachweis stand hier als
    # «NICHT ERFÜLLT» und darunter die Zeile «Alle Nachweise erfüllt» -- die
    # zaehlt die stillen naemlich schon immer nicht mit.
    gefuehrt = loesung.gefuehrte_urteile
    maengel = loesung.stille_maengel
    if not gefuehrt and not maengel:
        return []
    zeilen = ["", ""] + _ueberschrift("Nachweise", "=") + [""]
    for urteil in gefuehrt:
        zustand = "erfüllt" if urteil.erfuellt else "NICHT ERFÜLLT"
        zeilen.append(
            f"  {urteil.name.ljust(40)} Erfüllungsgrad "
            f"{urteil.gradtext().rjust(8)}   {zustand}"
        )
        if urteil.begruendung:
            zeilen.extend(_umbrechen(urteil.begruendung, 6))
    if gefuehrt:
        gesamt = ("Alle geführten Nachweise erfüllt."
                  if loesung.alle_nachweise_erfuellt
                  else "Mindestens ein Nachweis ist nicht erfüllt.")
        zeilen.extend(["", f"  {gesamt}"])

    return zeilen + _maengelzeilen(maengel)


def _maengelzeilen(maengel: Sequence[NachweisUrteil]) -> List[str]:
    """Was ausgeschaltet ist und nicht aufgeht -- unter der Liste der gefuehrten."""
    if not maengel:
        return []
    zeilen = ["", "  Nicht geführt, geht aber nicht auf:"]
    for urteil in maengel:
        zeilen.append(
            f"    {urteil.name.ljust(38)} Erfüllungsgrad "
            f"{urteil.gradtext().rjust(8)}"
        )
    return zeilen


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


def _abschnitt_luecken(loesung: Loesung) -> List[str]:
    if loesung.vollstaendig:
        return []
    zeilen = ["", ""] + _ueberschrift("Fehlende Eingaben", "=") + [""]

    if loesung.fehlende:
        zeilen.append("  Damit weitergerechnet werden kann, werden gebraucht:")
        zeilen.append("")
        for fehlend in loesung.fehlende:
            einheit = ""
            if fehlend.definition is not None:
                e = fehlend.definition.einheit
                einheit = f" [{e.beschriftung}]" if e.name not in ("", "-") else ""
            zeilen.append(f"    - {fehlend.id}{einheit}")
            zeilen.extend(_umbrechen(fehlend.beschreibung, 8))
            if fehlend.pfad:
                zeilen.append(f"        benötigt für: {' -> '.join(fehlend.pfad)}")

    nicht_erreicht = [z for z in loesung.nicht_berechenbar if z not in loesung.werte]
    if nicht_erreicht:
        zeilen.extend(["", "  Nicht berechenbare Ziele:", ""])
        for ziel in nicht_erreicht:
            scheitern = loesung.nicht_berechenbar[ziel]
            zeilen.append(f"    - {ziel}")
            for bid, grund in scheitern.verworfene_varianten:
                zeilen.append(f"        Variante '{bid}': {grund}")
    return zeilen


# ===========================================================================
# Ausgabe
# ===========================================================================


def als_text(loesung: Loesung, titel: str = "Berechnung") -> str:
    return "\n".join(loesung_zeilen(loesung, titel))


def drucke(
    loesung: Loesung,
    titel: str = "Berechnung",
    datei: Optional[TextIO] = None,
) -> None:
    """Schreibt den Bericht auf die Konsole (oder einen anderen Datenstrom)."""
    print(als_text(loesung, titel), file=datei)
