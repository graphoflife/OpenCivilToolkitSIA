"""
opencivil/bericht/latex_dokument.py -- Ausgabe einer Loesung als LaTeX-Dokument.

VERANTWORTUNG:
Schreibt aus einer :class:`Loesung` ein vollstaendiges, fuer sich uebersetzbares
``.tex``-Dokument und uebersetzt es zu PDF, sofern eine TeX-Maschine vorhanden
ist. Ist keine da, bleibt es beim ``.tex`` -- das laesst sich unveraendert in
Overleaf einfuegen.

Wie der Konsolenbericht rechnet auch dieser Baustein nichts: was im Bericht
steht, legt :func:`opencivil.bericht.gliederung.bericht` fest, hier wird es
nur gesetzt.

FORMELN FUER WORD:
Word uebernimmt aus der Zwischenablage MathML als richtige, weiter
bearbeitbare Formel. Die Oberflaeche rendert die hier erzeugten LaTeX-Zeichen-
ketten ohnehin mit KaTeX, und KaTeX erzeugt neben der HTML-Darstellung auch
MathML -- der Kopierknopf braucht also nur diesen Teil in die Zwischenablage zu
legen. :func:`formeln_sammeln` liefert die dafuer noetige Liste.

EIGENSTAENDIG NUTZBAR::

    from opencivil.bericht.latex_dokument import schreibe
    ergebnis = schreibe(loesung, "ausgabe/decke.tex", titel="Decke über EG")
    print(ergebnis.pdf_pfad or ergebnis.meldung)
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, Sequence

from opencivil.bericht.gliederung import bericht
from opencivil.core.latex import tabelle, text_latex
from opencivil.core.protokoll import (
    GleichungBlock, HinweisBlock, Protokoll, TabellenBlock, Tafel, TextBlock,
    TitelBlock, UnterprotokollBlock, darstellen,
)
from opencivil.core.rechenwerk import Loesung

if TYPE_CHECKING:
    from opencivil.projekt import Aufbau

#: Uebersetzer in der Reihenfolge, in der sie versucht werden.
TEX_MASCHINEN: Sequence[tuple[str, Sequence[str]]] = (
    ("tectonic", ("tectonic", "--keep-logs", "--outdir")),
    ("latexmk", ("latexmk", "-pdf", "-interaction=nonstopmode", "-outdir")),
    ("pdflatex", ("pdflatex", "-interaction=nonstopmode", "-output-directory")),
)

PRAEAMBEL = r"""\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[ngerman]{babel}
\usepackage{amsmath,amssymb}
\usepackage[a4paper,margin=25mm]{geometry}
% longtable und tabularx in einem: Tabellen laufen ueber Seiten, und
% Textspalten, die umbrechen duerfen, nehmen die Zeilenbreite ein.
\usepackage{xltabular}
\usepackage{xcolor}
\usepackage{textcomp}
\usepackage{fancyhdr}

\newcommand{\normref}[1]{{\small\textcolor{gray}{#1}}}
\newcommand{\hinweis}[2]{\par\noindent\textcolor{gray}{\textit{#1:}} \textit{#2}\par}

\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\berichttitel}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.6ex}
"""


@dataclass
class Ausgabeergebnis:
    """Was beim Schreiben (und allenfalls Uebersetzen) herauskam."""

    tex_pfad: Path
    pdf_pfad: Optional[Path] = None
    maschine: str = ""
    meldung: str = ""

    @property
    def hat_pdf(self) -> bool:
        return self.pdf_pfad is not None and self.pdf_pfad.exists()

    def __str__(self) -> str:
        if self.hat_pdf:
            return f"PDF erzeugt mit {self.maschine}: {self.pdf_pfad}"
        return f"LaTeX geschrieben: {self.tex_pfad} ({self.meldung})"


# ===========================================================================
# Dokumentaufbau
# ===========================================================================


def _protokoll_tex(protokoll: Protokoll, tiefe: int = 0) -> List[str]:
    return [zeile for teil in darstellen(protokoll, TAFEL, tiefe) for zeile in teil]


_STUFEN = ("section", "subsection", "subsubsection", "paragraph")


def _stufe(nummer: int) -> str:
    """Die Gliederungsstufe; tiefer als die letzte geht es nicht."""
    return _STUFEN[min(max(nummer, 0), len(_STUFEN) - 1)]


def _titel(block: TitelBlock, tiefe: int) -> List[str]:
    return [rf"\{_stufe(block.ebene - 1)}{{{text_latex(block.text)}}}"]


def _text(block: TextBlock, tiefe: int) -> List[str]:
    return [text_latex(block.text), ""]


def _gleichung(block: GleichungBlock, tiefe: int) -> List[str]:
    zeilen = []
    if block.titel:
        referenz = (rf" \hfill \normref{{{text_latex(block.referenz)}}}"
                    if block.referenz else "")
        zeilen.append(rf"\noindent\textbf{{{text_latex(block.titel)}}}{referenz}")
    return zeilen + [r"\begin{equation*}", block.latex, r"\end{equation*}"]


def _tabelle(block: TabellenBlock, tiefe: int) -> List[str]:
    zeilen = ([rf"\noindent\textbf{{{text_latex(block.titel)}}}"]
              if block.titel else [])
    return zeilen + [tabelle(block.kopf, block.zeilen, block.ausrichtung, lang=True)]


def _hinweis(block: HinweisBlock, tiefe: int) -> List[str]:
    return [rf"\hinweis{{{text_latex(block.art.beschriftung)}}}"
            rf"{{{text_latex(block.text)}}}"]


def _unterprotokoll(block: UnterprotokollBlock, tiefe: int) -> List[str]:
    return ([rf"\{_stufe(tiefe + 2)}{{{text_latex(block.titel)}}}"]
            + _protokoll_tex(block.protokoll, tiefe + 1))


#: Je Blockart, wie das LaTeX-Dokument sie setzt -- jede als Zeilen.
TAFEL: Tafel[List[str]] = {
    TitelBlock: _titel,
    TextBlock: _text,
    GleichungBlock: _gleichung,
    TabellenBlock: _tabelle,
    HinweisBlock: _hinweis,
    UnterprotokollBlock: _unterprotokoll,
}


def als_tex(
    loesung: Loesung,
    titel: str = "Berechnung",
    untertitel: str = "",
    *,
    aufbau: Optional["Aufbau"] = None,
) -> str:
    """Baut das vollstaendige LaTeX-Dokument -- mit ``aufbau`` die Nachweise je Platte."""
    protokoll = bericht(loesung, titel=titel, aufbau=aufbau)
    kopf = [
        PRAEAMBEL,
        # Steht in der Praeambel; fancyhdr wertet den Befehl erst beim Setzen
        # der Seite aus, die Reihenfolge ist also unkritisch.
        rf"\newcommand{{\berichttitel}}{{{text_latex(protokoll.kopftitel)}}}",
        rf"\title{{{text_latex(protokoll.kopftitel)}}}",
        rf"\author{{{text_latex(untertitel)}}}" if untertitel else r"\author{}",
        r"\date{\today}",
        r"\begin{document}",
        r"\maketitle",
    ]
    return "\n".join(kopf + _protokoll_tex(protokoll) + [r"\end{document}", ""])


# ===========================================================================
# Schreiben und Uebersetzen
# ===========================================================================


def finde_tex_maschine() -> Optional[tuple[str, Sequence[str]]]:
    """Sucht eine verfuegbare TeX-Maschine. None, wenn keine da ist."""
    for name, befehl in TEX_MASCHINEN:
        if shutil.which(befehl[0]):
            return name, befehl
    return None


def uebersetze(tex_pfad: str | Path) -> Ausgabeergebnis:
    """
    Uebersetzt ein vorhandenes ``.tex`` zu PDF, sofern eine Maschine da ist.

    Fehlt jede TeX-Maschine, ist das kein Fehler: das ``.tex`` steht dann
    trotzdem bereit und die Meldung sagt, was fehlt.

    Eigener Schritt, weil das Bauen des Dokuments ueberall laeuft, das
    Uebersetzen aber einen Unterprozess braucht -- und den gibt es im Browser
    nicht. Dort endet der Weg beim ``.tex``.
    """
    tex_pfad = Path(tex_pfad)
    maschine = finde_tex_maschine()
    if maschine is None:
        return Ausgabeergebnis(
            tex_pfad=tex_pfad,
            meldung=(
                "keine TeX-Maschine gefunden (gesucht wurde nach "
                + ", ".join(name for name, _ in TEX_MASCHINEN)
                + "); das .tex lässt sich unverändert in Overleaf einfügen"
            ),
        )

    name, befehl = maschine
    try:
        lauf = subprocess.run(
            [*befehl, str(tex_pfad.parent), str(tex_pfad)],
            capture_output=True,
            text=True,
            timeout=180,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return Ausgabeergebnis(
            tex_pfad=tex_pfad, maschine=name, meldung=f"{name} nicht ausführbar: {exc}"
        )

    pdf_pfad = tex_pfad.with_suffix(".pdf")
    if pdf_pfad.exists():
        return Ausgabeergebnis(tex_pfad=tex_pfad, pdf_pfad=pdf_pfad, maschine=name)
    letzte = (lauf.stderr or lauf.stdout or "").strip().splitlines()
    return Ausgabeergebnis(
        tex_pfad=tex_pfad,
        maschine=name,
        meldung=f"{name} lieferte kein PDF: {letzte[-1] if letzte else 'keine Ausgabe'}",
    )


def schreibe(
    loesung: Loesung,
    pfad: str | Path,
    *,
    titel: str = "Berechnung",
    untertitel: str = "",
    pdf: bool = True,
    aufbau: Optional["Aufbau"] = None,
) -> Ausgabeergebnis:
    """Schreibt das ``.tex`` und uebersetzt es, wenn moeglich, zu PDF."""
    tex_pfad = Path(pfad).with_suffix(".tex")
    tex_pfad.parent.mkdir(parents=True, exist_ok=True)
    tex_pfad.write_text(als_tex(loesung, titel, untertitel, aufbau=aufbau),
                        encoding="utf-8")

    if not pdf:
        return Ausgabeergebnis(tex_pfad=tex_pfad, meldung="PDF war nicht verlangt.")
    return uebersetze(tex_pfad)


# ===========================================================================
# Formeln fuer die Zwischenablage
# ===========================================================================


@dataclass(frozen=True)
class Formeleintrag:
    """Eine einzeln kopierbare Formel."""

    wert_id: str
    titel: str
    referenz: str
    latex: str


def formeln_sammeln(loesung: Loesung) -> List[Formeleintrag]:
    """
    Liefert alle Formeln der Loesung einzeln.

    Gedacht fuer die Oberflaeche: jeder Eintrag bekommt einen Kopierknopf. Das
    LaTeX geht unveraendert in Overleaf oder in den Formeleditor von Word 365;
    fuer eine in Word weiter bearbeitbare Formel legt die Oberflaeche statt-
    dessen das von KaTeX miterzeugte MathML in die Zwischenablage.
    """
    return [
        Formeleintrag(
            wert_id=block.wert_id,
            titel=block.titel,
            referenz=block.referenz,
            latex=block.latex,
        )
        for block in loesung.protokoll.alle_bloecke()
        if isinstance(block, GleichungBlock)
    ]
