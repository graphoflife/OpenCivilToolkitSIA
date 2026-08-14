"""
opencivil/bericht/latex_dokument.py -- Ausgabe einer Loesung als LaTeX-Dokument.

VERANTWORTUNG:
Schreibt aus einer :class:`Loesung` ein vollstaendiges, fuer sich uebersetzbares
``.tex``-Dokument und uebersetzt es zu PDF, sofern eine TeX-Maschine vorhanden
ist. Ist keine da, bleibt es beim ``.tex`` -- das laesst sich unveraendert in
Overleaf einfuegen.

Wie der Konsolenbericht rechnet auch dieser Baustein nichts: er liest dieselbe
Loesung und stellt sie nur anders dar.

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
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from opencivil.core.latex import text_latex
from opencivil.core.protokoll import (
    GleichungBlock, HinweisArt, HinweisBlock, Protokoll, TabellenBlock, TextBlock,
    TitelBlock, UnterprotokollBlock,
)
from opencivil.core.rechenwerk import Loesung
from opencivil.core.wert import Quelle

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
\usepackage{longtable}
\usepackage{booktabs}
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


def _protokoll_tex(protokoll: Protokoll, ebene: int = 0) -> List[str]:
    zeilen: List[str] = []
    abschnitt = ("subsection", "subsubsection", "paragraph")

    for block in protokoll.bloecke:
        if isinstance(block, TitelBlock):
            stufe = abschnitt[min(max(block.ebene - 2, 0), len(abschnitt) - 1)]
            zeilen.append(rf"\{stufe}{{{text_latex(block.text)}}}")

        elif isinstance(block, TextBlock):
            zeilen.append(text_latex(block.text))
            zeilen.append("")

        elif isinstance(block, GleichungBlock):
            if block.titel:
                referenz = rf" \hfill \normref{{{text_latex(block.referenz)}}}" if block.referenz else ""
                zeilen.append(rf"\noindent\textbf{{{text_latex(block.titel)}}}{referenz}")
            zeilen.append(r"\begin{equation*}")
            zeilen.append(block.latex)
            zeilen.append(r"\end{equation*}")

        elif isinstance(block, TabellenBlock):
            if block.titel:
                zeilen.append(rf"\noindent\textbf{{{text_latex(block.titel)}}}")
            zeilen.append(r"\begin{equation*}")
            zeilen.append(block.als_latex())
            zeilen.append(r"\end{equation*}")

        elif isinstance(block, HinweisBlock):
            zeilen.append(
                rf"\hinweis{{{text_latex(block.art.beschriftung)}}}{{{text_latex(block.text)}}}"
            )

        elif isinstance(block, UnterprotokollBlock):
            stufe = abschnitt[min(ebene + 1, len(abschnitt) - 1)]
            zeilen.append(rf"\{stufe}{{{text_latex(block.titel)}}}")
            zeilen.extend(_protokoll_tex(block.protokoll, ebene + 1))

    return zeilen


def _werte_tex(loesung: Loesung) -> List[str]:
    if not loesung.werte:
        return []
    marken = {
        Quelle.EINGABE: "Eingabe",
        Quelle.VORGABE: "Vorgabe",
        Quelle.BERECHNET: "berechnet",
        Quelle.UEBERSCHRIEBEN: r"\textbf{überschrieben}",
    }
    zeilen = [
        r"\section{Werteübersicht}",
        r"\begin{longtable}{llrll}",
        r"\toprule",
        r"Bezeichnung & Symbol & Wert & Einheit & Herkunft \\",
        r"\midrule",
        r"\endhead",
    ]
    for wert_id in sorted(loesung.werte):
        wert = loesung.werte[wert_id]
        einheit = wert.einheit.name if wert.einheit.name not in ("", "-") else ""
        zeilen.append(
            f"{text_latex(wert.beschreibung or wert_id)} & ${wert.symbol}$ & "
            f"{wert.formatiert()} & {text_latex(einheit)} & {marken[wert.quelle]} \\\\"
        )
    zeilen += [r"\bottomrule", r"\end{longtable}"]
    return zeilen


def _nachweise_tex(loesung: Loesung) -> List[str]:
    if not loesung.urteile:
        return []
    zeilen = [
        r"\section{Zusammenstellung der Nachweise}",
        r"\begin{longtable}{lrl}",
        r"\toprule",
        r"Nachweis & Ausnutzung $\eta$ & Ergebnis \\",
        r"\midrule",
        r"\endhead",
    ]
    for urteil in loesung.urteile:
        ergebnis = (
            r"\textcolor{green!50!black}{erfüllt}"
            if urteil.erfuellt
            else r"\textcolor{red}{\textbf{nicht erfüllt}}"
        )
        zeilen.append(
            f"{text_latex(urteil.name)} & {urteil.ausnutzung.formatiert(3)} & {ergebnis} \\\\"
        )
    zeilen += [r"\bottomrule", r"\end{longtable}"]

    gesamt = (
        "Sämtliche Nachweise sind erfüllt."
        if loesung.alle_nachweise_erfuellt
        else r"\textbf{Mindestens ein Nachweis ist nicht erfüllt.}"
    )
    zeilen.append(rf"\noindent {gesamt}")
    return zeilen


def _luecken_tex(loesung: Loesung) -> List[str]:
    if loesung.vollstaendig:
        return []
    zeilen = [r"\section{Fehlende Eingaben}"]
    if loesung.fehlende:
        zeilen.append("Damit weitergerechnet werden kann, werden gebraucht:")
        zeilen.append(r"\begin{itemize}")
        for fehlend in loesung.fehlende:
            beschreibung = text_latex(fehlend.beschreibung)
            zeilen.append(
                rf"\item \texttt{{{text_latex(fehlend.id)}}} -- {beschreibung}"
            )
        zeilen.append(r"\end{itemize}")
    return zeilen


def als_tex(loesung: Loesung, titel: str = "Berechnung", untertitel: str = "") -> str:
    """Baut das vollstaendige LaTeX-Dokument."""
    kopf = [
        PRAEAMBEL,
        # Steht in der Praeambel; fancyhdr wertet den Befehl erst beim Setzen
        # der Seite aus, die Reihenfolge ist also unkritisch.
        rf"\newcommand{{\berichttitel}}{{{text_latex(titel)}}}",
        rf"\title{{{text_latex(titel)}}}",
        rf"\author{{{text_latex(untertitel)}}}" if untertitel else r"\author{}",
        r"\date{\today}",
        r"\begin{document}",
        r"\maketitle",
    ]
    koerper: List[str] = []
    if not loesung.protokoll.ist_leer:
        koerper.append(r"\section{Herleitung}")
        koerper.extend(_protokoll_tex(loesung.protokoll))
    koerper.extend(_nachweise_tex(loesung))
    koerper.extend(_werte_tex(loesung))
    koerper.extend(_luecken_tex(loesung))

    return "\n".join(kopf + koerper + [r"\end{document}", ""])


# ===========================================================================
# Schreiben und Uebersetzen
# ===========================================================================


def finde_tex_maschine() -> Optional[tuple[str, Sequence[str]]]:
    """Sucht eine verfuegbare TeX-Maschine. None, wenn keine da ist."""
    for name, befehl in TEX_MASCHINEN:
        if shutil.which(befehl[0]):
            return name, befehl
    return None


def schreibe(
    loesung: Loesung,
    pfad: str | Path,
    *,
    titel: str = "Berechnung",
    untertitel: str = "",
    pdf: bool = True,
) -> Ausgabeergebnis:
    """
    Schreibt das ``.tex`` und uebersetzt es, wenn moeglich, zu PDF.

    Fehlt jede TeX-Maschine, ist das kein Fehler: das ``.tex`` steht dann
    trotzdem bereit und die Meldung sagt, was fehlt.
    """
    tex_pfad = Path(pfad).with_suffix(".tex")
    tex_pfad.parent.mkdir(parents=True, exist_ok=True)
    tex_pfad.write_text(als_tex(loesung, titel, untertitel), encoding="utf-8")

    if not pdf:
        return Ausgabeergebnis(tex_pfad=tex_pfad, meldung="PDF war nicht verlangt.")

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
