---
erzeugt: ef425f26acc9
art: modul
tags: [modul]
---
> [!abstract] opencivil/bericht/markdown.py
> Ausgabe einer Loesung als Markdown.
> Paket [[opencivil.bericht]] · [Quelltext](../../opencivil/bericht/markdown.py)

## VERANTWORTUNG

Setzt den Bericht ([[opencivil.bericht.gliederung#bericht|opencivil.bericht.gliederung.bericht]]) als
Markdown -- fuer GitHub, Obsidian, Jupyter, Pandoc oder ein Wiki. Was darin
steht, entscheidet die Gliederung; hier wird es nur gesetzt, mit einer Tafel
wie beim Konsolenbericht und beim LaTeX-Dokument.


## FORMELN

Markdown hat keine eigene Formelsprache. Wer Formeln kann, liest LaTeX-Mathe
zwischen `$...$` und `$$...$$` -- also stehen die Formeln hier genau so
wie im LaTeX-Dokument. Nur Text und Tabellen sind Markdown.


## EIGENSTAENDIG NUTZBAR


```python
from opencivil.bericht.markdown import als_markdown
print(als_markdown(loesung, titel="Decke über EG"))
```

## Inhalt

### text_markdown

```python
def text_markdown(text: str) -> str
```

Maskiert Text, sodass er als Text dasteht und nicht als Auszeichnung.

### absatz_markdown

```python
def absatz_markdown(text: str) -> str
```

Wie [[opencivil.bericht.markdown#text_markdown|text_markdown]], fuer Text, der einen Absatz beginnt.

### formel_in_zelle

```python
def formel_in_zelle(latex: str) -> str
```

Eine Formel fuer eine Tabellenzelle, zwischen `$`.

Ein `|` teilte die Zelle auch mitten in einer Formel -- die Tabelle wird
zerlegt, bevor irgendwer die Formel liest. Darum als `\vert`.

### _zelle

```python
def _zelle(zelle: Zelle) -> str
```

Eine Tabellenzelle: Text maskiert, eine Formel zwischen `$`.

### _ueberschrift

```python
def _ueberschrift(stufe: int, text: str) -> List[str]
```

Markdown kennt sechs Stufen; tiefer bleibt es bei der sechsten.

### protokoll_zeilen

```python
def protokoll_zeilen(protokoll: Protokoll) -> List[str]
```

### block_markdown

```python
def block_markdown(block: Block) -> str
```

Ein einzelner Block, wie er im Markdown-Bericht steht -- fuer den
Kopierknopf an diesem Block. Aus derselben Tafel, damit Knopf und
Dokument dasselbe liefern.

### als_markdown

```python
def als_markdown(loesung: Loesung, titel: str='Berechnung', untertitel: str='', *, aufbau: Optional['Aufbau']=None) -> str
```

Der ganze Bericht als Markdown -- mit `aufbau` die Nachweise je Platte.


## Konstanten

- `_AUSZEICHNUNG = re.compile('([\\\\`*_<>$|])')` – Zeichen, die Markdown im Fliesstext als Auszeichnung liest. `$` gehoert dazu: wer Formeln kann, laese sonst zwischen zwei Betraegen eine Formel. Eckige Klammern nicht: ohne `(...)` dahinter sind sie ohnehin Text, und `\[` laese MathJax (etwa in Jupyter) als Anfang einer Formel.
- `_ZAHL_AM_ANFANG = re.compile('^(\\d+)\\.')` – Am Anfang eines Absatzes waere «2. Lage» eine nummerierte Liste, ein «-» oder «+» eine Aufzaehlung und ein «#» eine Ueberschrift.
- `_SPALTE = {'l': ':---', 'L': ':---', 'c': ':---:', 'r': '---:'}`
- `TAFEL = {TitelBlock: _titel, TextBlock: _text, GleichungBlock: _gleichung, Ta…` – Je Blockart, wie Markdown sie setzt -- jede als Zeilen, mit Leerzeile danach.

## Braucht

- [[opencivil.bericht.gliederung]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.projekt]]

## Gebraucht von

- [[opencivil.ergebnis]]
- [[opencivil.notizbuch.formelseiten]]
- [[opencivil.web.api]]
- [[opencivil.web.dienst]]
