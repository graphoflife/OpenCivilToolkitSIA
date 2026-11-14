---
erzeugt: 2eb5dada7a63
art: modul
tags: [modul]
---
> [!abstract] opencivil/pfahl/uebersicht.py
> was über der Nachweistabelle eines Pfahls steht.
> Paket [[opencivil.pfahl]] · [Quelltext](../../opencivil/pfahl/uebersicht.py)

## VERANTWORTUNG

Die Angaben zum Pfahl, aus den Werten der Lösung ([[opencivil.pfahl.uebersicht#angaben|angaben]]), und die
Widerstände beider Nachweise nebeneinander, auf Druck und auf Zug -- vom
Mantel bis zum Bemessungswert ([[opencivil.pfahl.uebersicht#widerstandstabelle|widerstandstabelle]]). Gerechnet wird
hier nichts: die Zahlen stehen in den Befunden.

## Inhalt

### angaben

```python
def angaben(pfahl: Pfahl, werte: Dict[str, Wert]) -> GleichungBlock
```

In der ersten Zeile Art, Masse und Grundwasser, in der zweiten der
Querschnitt mit η_i und die Grundlage des äusseren Widerstands mit η_a.

### widerstandstabelle

```python
def widerstandstabelle(aussen: Optional[Aussenbefund], innen: Optional[Innenbefund]) -> TabellenBlock
```

Je Widerstand eine Zeile, in kN: Druck und Zug nebeneinander.


## Braucht

- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.pfahl.aussen]]
- [[opencivil.pfahl.innen]]
- [[opencivil.pfahl.pfahl]]

## Gebraucht von

- [[opencivil.bericht.zusammenfassung]]
