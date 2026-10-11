---
erzeugt: 180f22de263e
art: modul
tags: [modul]
---
> [!abstract] opencivil/bericht/latex_dokument.py
> Ausgabe einer Loesung als LaTeX-Dokument.
> Paket [[opencivil.bericht]] · [Quelltext](../../opencivil/bericht/latex_dokument.py)

## VERANTWORTUNG

Schreibt aus einer [[opencivil.core.rechenwerk#Loesung|Loesung]] ein vollstaendiges, fuer sich uebersetzbares
`.tex`-Dokument und uebersetzt es zu PDF, sofern eine TeX-Maschine vorhanden
ist. Ist keine da, bleibt es beim `.tex` -- das laesst sich unveraendert in
Overleaf einfuegen.

Wie der Konsolenbericht rechnet auch dieser Baustein nichts: was im Bericht
steht, legt [[opencivil.bericht.gliederung#bericht|opencivil.bericht.gliederung.bericht]] fest, hier wird es
nur gesetzt.


## FORMELN FUER WORD

Word uebernimmt aus der Zwischenablage MathML als richtige, weiter
bearbeitbare Formel. Die Oberflaeche rendert die hier erzeugten LaTeX-Zeichen-
ketten ohnehin mit KaTeX, und KaTeX erzeugt neben der HTML-Darstellung auch
MathML -- der Kopierknopf braucht also nur diesen Teil in die Zwischenablage zu
legen. [[opencivil.bericht.latex_dokument#formeln_sammeln|formeln_sammeln]] liefert die dafuer noetige Liste.


## EIGENSTAENDIG NUTZBAR


```python
from opencivil.bericht.latex_dokument import schreibe
ergebnis = schreibe(loesung, "ausgabe/decke.tex", titel="Decke über EG")
print(ergebnis.pdf_pfad or ergebnis.meldung)
```

## Inhalt

### Ausgabeergebnis

```python
@dataclass
class Ausgabeergebnis
```

Was beim Schreiben (und allenfalls Uebersetzen) herauskam.

- `tex_pfad: Path`
- `pdf_pfad: Optional[Path] = None`
- `maschine: str = ''`
- `meldung: str = ''`

#### Ausgabeergebnis.hat_pdf

```python
@property
def hat_pdf(self) -> bool
```

### _stufe

```python
def _stufe(nummer: int) -> str
```

Die Gliederungsstufe; tiefer als die letzte geht es nicht.

### als_tex

```python
def als_tex(loesung: Loesung, titel: str='Berechnung', untertitel: str='', *, aufbau: Optional['Aufbau']=None) -> str
```

Baut das vollstaendige LaTeX-Dokument -- mit `aufbau` die Nachweise je Platte.

### finde_tex_maschine

```python
def finde_tex_maschine() -> Optional[tuple[str, Sequence[str]]]
```

Sucht eine verfuegbare TeX-Maschine. None, wenn keine da ist.

### uebersetze

```python
def uebersetze(tex_pfad: str | Path) -> Ausgabeergebnis
```

Uebersetzt ein vorhandenes `.tex` zu PDF, sofern eine Maschine da ist.

Fehlt jede TeX-Maschine, ist das kein Fehler: das `.tex` steht dann
trotzdem bereit und die Meldung sagt, was fehlt.

Eigener Schritt, weil das Bauen des Dokuments ueberall laeuft, das
Uebersetzen aber einen Unterprozess braucht -- und den gibt es im Browser
nicht. Dort endet der Weg beim `.tex`.

### schreibe

```python
def schreibe(loesung: Loesung, pfad: str | Path, *, titel: str='Berechnung', untertitel: str='', pdf: bool=True, aufbau: Optional['Aufbau']=None) -> Ausgabeergebnis
```

Schreibt das `.tex` und uebersetzt es, wenn moeglich, zu PDF.

### Formeleintrag

```python
@dataclass(frozen=True)
class Formeleintrag
```

Eine einzeln kopierbare Formel.

- `wert_id: str`
- `titel: str`
- `referenz: str`
- `latex: str`

### formeln_sammeln

```python
def formeln_sammeln(loesung: Loesung) -> List[Formeleintrag]
```

Liefert alle Formeln der Loesung einzeln.

Gedacht fuer die Oberflaeche: jeder Eintrag bekommt einen Kopierknopf. Das
LaTeX geht unveraendert in Overleaf oder in den Formeleditor von Word 365;
fuer eine in Word weiter bearbeitbare Formel legt die Oberflaeche statt-
dessen das von KaTeX miterzeugte MathML in die Zwischenablage.


## Konstanten

- `TEX_MASCHINEN = (('tectonic', ('tectonic', '--keep-logs', '--outdir')), ('latexmk', (…` – Uebersetzer in der Reihenfolge, in der sie versucht werden.
- `PRAEAMBEL = '\\documentclass[11pt,a4paper]{article}\n\\usepackage[utf8]{inputenc}…`
- `_STUFEN = ('section', 'subsection', 'subsubsection', 'paragraph')`
- `TAFEL = {TitelBlock: _titel, TextBlock: _text, GleichungBlock: _gleichung, Ta…` – Je Blockart, wie das LaTeX-Dokument sie setzt -- jede als Zeilen.

## Braucht

- [[opencivil.bericht.gliederung]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.projekt]]

## Gebraucht von

- [[opencivil.ergebnis]]
- [[opencivil.web.dienst]]
- [[opencivil.web.server]]
