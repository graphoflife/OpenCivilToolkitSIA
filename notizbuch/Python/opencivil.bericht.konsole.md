---
erzeugt: f799fc612928
art: modul
tags: [modul]
---
> [!abstract] opencivil/bericht/konsole.py
> Ausgabe einer Loesung auf der Konsole.
> Paket [[opencivil.bericht]] · [Quelltext](../../opencivil/bericht/konsole.py)

## VERANTWORTUNG

Macht das Backend fuer sich allein bedienbar. Die LaTeX-Formeln werden roh
ausgegeben -- nicht gesetzt, sondern als Quelltext, damit man sie lesen,
pruefen und direkt weiterverwenden kann.

Der Bericht ist reine Darstellung: was darin steht und in welcher Folge,
legt [[opencivil.bericht.gliederung#bericht|opencivil.bericht.gliederung.bericht]] fest -- fuer die Konsole
wie fuer das LaTeX-Dokument. Hier wird es nur als Text gesetzt.


## EIGENSTAENDIG NUTZBAR


```python
from opencivil.bericht.konsole import drucke
drucke(loesung, titel="Materialkennwerte C30/37")
```

## Inhalt

### _umbrechen

```python
def _umbrechen(text: str, einzug: int=0) -> List[str]
```

Bricht Fliesstext auf die Terminalbreite um.

### protokoll_zeilen

```python
def protokoll_zeilen(protokoll: Protokoll) -> List[str]
```

Wandelt eine Mitschrift in Konsolenzeilen um.

### _tabelle_zeilen

```python
def _tabelle_zeilen(block: TabellenBlock, einzug: int) -> List[str]
```

Setzt die Tabelle als Text -- Spaltenbreiten nach dem laengsten Eintrag.

Zahlen rechts, Text links, wenn die Tabelle es sagt (`ausrichtung` wie
in LaTeX, `l`, `c` oder `r` je Spalte). Ohne Angabe alles rechts.
Frueher galt immer rechts, auch wo die Tabelle `l` verlangte -- im
LaTeX-Dokument stand sie richtig, auf der Konsole nicht.

### _zelle

```python
def _zelle(zelle: Zelle) -> str
```

Text wie er ist; eine Formel als Quelltext, wie ueberall auf der Konsole.

### _wert_text

```python
def _wert_text(wert: Optional[Wert]) -> str
```

Zahl und Einheit, ohne Formelzeichen -- die Spalte sagt, was es ist.

### zusammenfassung

```python
def zusammenfassung(zusammenfassung: 'Zusammenfassung') -> str
```

Je Platte eine Tabelle der Nachweise -- die Zusammenfassung der
Oberflaeche, fuer die Konsole.

Welche Zeilen dastehen, entscheidet
[[opencivil.bericht.zusammenfassung#zusammenfassen|opencivil.bericht.zusammenfassung.zusammenfassen]]; hier wird nur
gesetzt. Je Platte eine eigene Tabelle, weil die Urteilsnamen die Platte
nicht nennen -- zwei Platten mit einer Kombination «Feld» stuenden sonst
als zwei gleiche Zeilen da.

### als_text

```python
def als_text(loesung: Loesung, titel: str='Berechnung', *, aufbau: Optional['Aufbau']=None) -> str
```

Der ganze Bericht als Text -- mit `aufbau` die Nachweise je Platte.

### drucke

```python
def drucke(loesung: Loesung, titel: str='Berechnung', datei: Optional[TextIO]=None, *, aufbau: Optional['Aufbau']=None) -> None
```

Schreibt den Bericht auf die Konsole (oder einen anderen Datenstrom).


## Konstanten

- `_BREITE = min(shutil.get_terminal_size((100, 24)).columns, 100)`
- `_MARKE = {HinweisArt.INFO: 'i', HinweisArt.WARNUNG: '!', HinweisArt.ANNAHME: '…`
- `TAFEL = {TitelBlock: _titel, TextBlock: _text, GleichungBlock: _gleichung, Ta…` – Je Blockart, wie die Konsole sie setzt -- jede als Zeilen.

## Braucht

- [[opencivil.bericht.gliederung]]
- [[opencivil.bericht.zusammenfassung]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.core.wert]]
- [[opencivil.projekt]]

## Gebraucht von

- [[opencivil.ergebnis]]
