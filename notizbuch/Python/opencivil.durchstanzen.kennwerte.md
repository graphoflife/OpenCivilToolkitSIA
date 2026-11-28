---
erzeugt: a7e27a359e4f
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
Stahlpilz und Durchstanzbewehrung dazu, was sie sind und was sie tragen.
Ohne Einwirkung nur der Schnitt: ψ = 0 und k_r = 2 gälten nur ohne Last;
was die Stelle trägt, sagt die Kennzahl ([[opencivil.durchstanzen.kennzahl|.kennzahl]]). Bis 2026-11-27
stand dort V_Rd,c = 866.7 kN, wo die Kennzahl 503.6 kN sagt.


## Braucht

- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.durchstanzen.nachweis]]
- [[opencivil.durchstanzen.stelle]]
- [[opencivil.durchstanzen.weg]]

## Gebraucht von

- [[opencivil.bericht.zusammenfassung]]
