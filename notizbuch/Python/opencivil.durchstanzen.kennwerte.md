---
erzeugt: c42930a0e3b5
art: modul
tags: [modul]
---
> [!abstract] opencivil/durchstanzen/kennwerte.py
> was die Zusammenfassung einer
> Paket [[opencivil.durchstanzen]] · [Quelltext](../../opencivil/durchstanzen/kennwerte.py)

Durchstanzstelle über ihrer Tabelle und in ihr zeigt.


## VERANTWORTUNG

Die Angaben zur Stelle – Lage, Platte, Beton und die Masse, wie gerechnet
– und die Tabelle der Grössen, aus denen der Widerstand entsteht, aus dem
Befund des Nachweises ([[opencivil.durchstanzen.nachweis#Durchstanzbefund|.nachweis.Durchstanzbefund]]). Bis 2026-11-28
standen beide am Ende von [[opencivil.durchstanzen.nachweis|.nachweis]]; die Datei wurde zu lang.

## Inhalt

### angaben

```python
def angaben(stelle: Durchstanzstelle, werte: Dict[str, Wert]) -> GleichungBlock
```

Was über der Tabelle steht: Lage, Platte, Beton und die Masse, wie gerechnet.

### kennwerttabelle

```python
def kennwerttabelle(befund: Durchstanzbefund) -> TabellenBlock
```

Die Grössen, aus denen der Widerstand entsteht – eine Zeile je Grösse. Mit
Stahlpilz und Durchstanzbewehrung dazu, was sie sind und was sie tragen,
auch die Leisten an den Stufen der Bereiche.
Ohne Einwirkung nur der Schnitt: ψ = 0 und k_r = 2 gälten nur ohne Last;
was die Stelle trägt, sagt die Kennzahl ([[opencivil.durchstanzen.kennzahl|.kennzahl]]). Bis 2026-11-27
stand dort V_Rd,c = 866.7 kN, wo die Kennzahl 503.6 kN sagt.

### _leistenzeilen

```python
def _leistenzeilen(leisten: Leistenpruefung, titel: str, abstaende: str, ix: str='') -> list
```

Die Zeilen einer Durchstanzbewehrung – `ix` hängt an den Zeichen, «,B1» an einer Stufe.

### _zeile

```python
def _zeile(text: str, zeichen: str, wert: str, einheit: str) -> list
```

Eine Zeile der Tabelle: Text, Zeichen und Wert als Formel, Einheit.

### _kraft

```python
def _kraft(x: float) -> str
```

Eine Kraft der Tabelle: kN mit einer Stelle.


## Braucht

- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.durchstanzen.nachweis]]
- [[opencivil.durchstanzen.pruefung]]
- [[opencivil.durchstanzen.stelle]]
- [[opencivil.durchstanzen.weg]]

## Gebraucht von

- [[opencivil.bericht.zusammenfassung]]
