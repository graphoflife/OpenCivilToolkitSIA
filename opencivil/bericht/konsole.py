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
from typing import Iterable, List, Optional, TextIO

from opencivil.core.protokoll import (
    Block, GleichungBlock, HinweisArt, HinweisBlock, Protokoll, TabellenBlock,
    TextBlock, TitelBlock, UnterprotokollBlock,
)
from opencivil.core.rechenwerk import Loesung
from opencivil.core.wert import Quelle

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


def protokoll_zeilen(protokoll: Protokoll, einzug: int = 0) -> List[str]:
    """Wandelt eine Mitschrift in Konsolenzeilen um."""
    zeilen: List[str] = []
    vorspann = " " * einzug

    for block in protokoll.nach_abschnitten():
        if isinstance(block, TitelBlock):
            zeilen.append("")
            zeilen.append(f"{vorspann}{block.text}")
            zeilen.append(f"{vorspann}{'-' * len(block.text)}")

        elif isinstance(block, TextBlock):
            zeilen.append("")
            zeilen.extend(_umbrechen(block.text, einzug))

        elif isinstance(block, GleichungBlock):
            zeilen.append("")
            kopf = block.titel or block.wert_id
            if kopf:
                nachweis = f"   [{block.referenz}]" if block.referenz else ""
                zeilen.append(f"{vorspann}{kopf}{nachweis}")
            for teil in block.latex.splitlines():
                zeilen.append(f"{vorspann}    {teil}")

        elif isinstance(block, TabellenBlock):
            zeilen.append("")
            if block.titel:
                zeilen.append(f"{vorspann}{block.titel}")
            zeilen.extend(_tabelle_zeilen(block, einzug + 4))

        elif isinstance(block, HinweisBlock):
            marke = {
                HinweisArt.INFO: "i",
                HinweisArt.WARNUNG: "!",
                HinweisArt.ANNAHME: "*",
            }[block.art]
            zeilen.extend(
                _umbrechen(f"[{marke}] {block.art.beschriftung}: {block.text}", einzug)
            )

        elif isinstance(block, UnterprotokollBlock):
            zeilen.append("")
            zeilen.append(f"{vorspann}> {block.titel}")
            zeilen.extend(protokoll_zeilen(block.protokoll, einzug + 2))

    return zeilen


def _tabelle_zeilen(block: TabellenBlock, einzug: int) -> List[str]:
    """Setzt die Tabelle als Text -- Spaltenbreiten nach dem laengsten Eintrag."""
    alle = [list(block.kopf)] + [list(z) for z in block.zeilen]
    breiten = [max(len(z[i]) for z in alle) for i in range(len(block.kopf))]
    vorspann = " " * einzug

    def zeile(zellen: Iterable[str]) -> str:
        return vorspann + "  ".join(t.rjust(b) for t, b in zip(zellen, breiten))

    ausgabe = [zeile(block.kopf), vorspann + "  ".join("-" * b for b in breiten)]
    ausgabe.extend(zeile(z) for z in block.zeilen)
    return ausgabe


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

    if maengel:
        zeilen.extend(["", "  Nicht geführt, geht aber nicht auf:"])
        for urteil in maengel:
            zeilen.append(
                f"    {urteil.name.ljust(38)} Erfüllungsgrad "
                f"{urteil.gradtext().rjust(8)}"
            )
    return zeilen


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
