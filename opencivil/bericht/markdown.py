"""
opencivil/bericht/markdown.py -- Ausgabe einer Loesung als Markdown.

VERANTWORTUNG:
Setzt den Bericht (:func:`opencivil.bericht.gliederung.bericht`) als
Markdown -- fuer GitHub, Obsidian, Jupyter, Pandoc oder ein Wiki. Was darin
steht, entscheidet die Gliederung; hier wird es nur gesetzt, mit einer Tafel
wie beim Konsolenbericht und beim LaTeX-Dokument.

FORMELN:
Markdown hat keine eigene Formelsprache. Wer Formeln kann, liest LaTeX-Mathe
zwischen ``$...$`` und ``$$...$$`` -- also stehen die Formeln hier genau so
wie im LaTeX-Dokument. Nur Text und Tabellen sind Markdown.

EIGENSTAENDIG NUTZBAR::

    from opencivil.bericht.markdown import als_markdown
    print(als_markdown(loesung, titel="Decke über EG"))
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, List, Optional

from opencivil.bericht.gliederung import bericht
from opencivil.core.latex import Mathe, Zelle
from opencivil.core.protokoll import (
    Block, GleichungBlock, HinweisBlock, Protokoll, TabellenBlock, Tafel,
    TextBlock, TitelBlock, UnterprotokollBlock, darstellen,
)
from opencivil.core.rechenwerk import Loesung

if TYPE_CHECKING:
    from opencivil.projekt import Aufbau

#: Zeichen, die Markdown im Fliesstext als Auszeichnung liest. ``$`` gehoert
#: dazu: wer Formeln kann, laese sonst zwischen zwei Betraegen eine Formel.
#: Eckige Klammern nicht: ohne ``(...)`` dahinter sind sie ohnehin Text, und
#: ``\[`` laese MathJax (etwa in Jupyter) als Anfang einer Formel.
_AUSZEICHNUNG = re.compile(r"([\\`*_<>$|])")

#: Am Anfang eines Absatzes waere «2. Lage» eine nummerierte Liste, ein
#: «-» oder «+» eine Aufzaehlung und ein «#» eine Ueberschrift.
_ZAHL_AM_ANFANG = re.compile(r"^(\d+)\.")


def text_markdown(text: str) -> str:
    """Maskiert Text, sodass er als Text dasteht und nicht als Auszeichnung."""
    return _AUSZEICHNUNG.sub(r"\\\1", text)


def absatz_markdown(text: str) -> str:
    """Wie :func:`text_markdown`, fuer Text, der einen Absatz beginnt."""
    text = _ZAHL_AM_ANFANG.sub(r"\1\\.", text_markdown(text))
    return "\\" + text if text[:1] in ("-", "+", "#") else text


def _zelle(zelle: Zelle) -> str:
    """
    Eine Tabellenzelle: Text maskiert, eine Formel zwischen ``$``.

    Ein ``|`` teilte die Zelle auch mitten in einer Formel -- die Tabelle wird
    zerlegt, bevor irgendwer die Formel liest. Darum als ``\\vert``.
    """
    if isinstance(zelle, Mathe):
        latex = zelle.latex.replace(r"\|", r"\Vert ").replace("|", r"\vert ")
        return f"${latex}$"
    return text_markdown(zelle)


_SPALTE = {"l": ":---", "L": ":---", "c": ":---:", "r": "---:"}


def _ueberschrift(stufe: int, text: str) -> List[str]:
    """Markdown kennt sechs Stufen; tiefer bleibt es bei der sechsten."""
    return [f"{'#' * min(stufe, 6)} {text_markdown(text)}", ""]


def _titel(block: TitelBlock, tiefe: int) -> List[str]:
    # Stufe 1 ist der Kopftitel des Berichts, die Abschnitte beginnen darunter.
    return _ueberschrift(block.ebene + 1, block.text)


def _text(block: TextBlock, tiefe: int) -> List[str]:
    return [absatz_markdown(block.text), ""]


def _gleichung(block: GleichungBlock, tiefe: int) -> List[str]:
    zeilen = []
    if block.titel:
        referenz = f" *({text_markdown(block.referenz)})*" if block.referenz else ""
        zeilen += [f"**{text_markdown(block.titel)}**{referenz}", ""]
    return zeilen + ["$$", block.latex, "$$", ""]


def _tabelle(block: TabellenBlock, tiefe: int) -> List[str]:
    spalten = block.ausrichtung or "r" * len(block.kopf)
    zeilen = [f"**{text_markdown(block.titel)}**", ""] if block.titel else []
    zeilen.append("| " + " | ".join(_zelle(z) for z in block.kopf) + " |")
    zeilen.append("| " + " | ".join(_SPALTE[a] for a in spalten) + " |")
    zeilen += ["| " + " | ".join(_zelle(z) for z in zeile) + " |"
               for zeile in block.zeilen]
    return zeilen + [""]


def _hinweis(block: HinweisBlock, tiefe: int) -> List[str]:
    return [f"> **{block.art.beschriftung}:** {text_markdown(block.text)}", ""]


def _unterprotokoll(block: UnterprotokollBlock, tiefe: int) -> List[str]:
    # Wie im LaTeX-Dokument eine Stufe unter den Zwischentiteln der Herleitung.
    return (_ueberschrift(tiefe + 4, block.titel)
            + protokoll_zeilen(block.protokoll, tiefe + 1))


#: Je Blockart, wie Markdown sie setzt -- jede als Zeilen, mit Leerzeile danach.
TAFEL: Tafel[List[str]] = {
    TitelBlock: _titel,
    TextBlock: _text,
    GleichungBlock: _gleichung,
    TabellenBlock: _tabelle,
    HinweisBlock: _hinweis,
    UnterprotokollBlock: _unterprotokoll,
}


def protokoll_zeilen(protokoll: Protokoll, tiefe: int = 0) -> List[str]:
    return [zeile for teil in darstellen(protokoll, TAFEL, tiefe) for zeile in teil]


def block_markdown(block: Block) -> str:
    """
    Ein einzelner Block, wie er im Markdown-Bericht steht -- fuer den
    Kopierknopf an diesem Block. Aus derselben Tafel, damit Knopf und
    Dokument dasselbe liefern.
    """
    return "\n".join(TAFEL[type(block)](block, 0)).strip("\n")


def als_markdown(
    loesung: Loesung,
    titel: str = "Berechnung",
    untertitel: str = "",
    *,
    aufbau: Optional["Aufbau"] = None,
) -> str:
    """Der ganze Bericht als Markdown -- mit ``aufbau`` die Nachweise je Platte."""
    protokoll = bericht(loesung, titel=titel, aufbau=aufbau)
    kopf = _ueberschrift(1, protokoll.kopftitel)
    if untertitel:
        kopf += [f"*{text_markdown(untertitel)}*", ""]
    return "\n".join(kopf + protokoll_zeilen(protokoll)).rstrip("\n") + "\n"
