---
erzeugt: 0485e8ea8a15
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/richtungsnachweise.py
> Duktilitaet und sproedes Versagen des gezeichneten Querschnitts.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/richtungsnachweise.py)

## VERANTWORTUNG

Zwei Nachweise, die wie bei der Platte dem Querschnitt gehoeren und keinem
Lastfall: Duktilitaet (`x/d`) und sproedes Versagen (`M_Rd >= M_Riss`).
Wo die Platte je Lage fragt, fragt der gezeichnete Querschnitt je Richtung:
Zug unten, oben, links, rechts -- einachsig nur unten und oben. In der
Zusammenfassung steht die unguenstigere.

Gerechnet wird bei reiner Biegung, `N = 0`, mit dem Bruchzustand aus
[[opencivil.querschnitt.interaktion]]. Eine Richtung ohne Bewehrung auf
ihrer gezogenen Seite des Schwerpunkts hat keinen solchen Nachweis -- dort
steht ein Satz und kein Urteil, wie bei einer unbewehrten Lage der Platte.


## ANNAHMEN

Das Rissmoment gehoert dem ungerissenen Bruttoquerschnitt: unter reiner
Biegung das Moment, bei dem `f_ct,eff` zum ersten Mal irgendwo erreicht
wird -- mit `I_yz`, einachsig mit waagrechter Nulllinie. Es steht mit den
uebrigen Rissgroessen an einer Stelle ([[opencivil.nachweis.rissgroessen]]);
die Zwaengung auf Biegung ([[opencivil.nachweis.qa_gebrauch]]) haelt
dasselbe Rissmoment gegen ihre Bewehrung.

## Inhalt

### bei_reiner_biegung

```python
def bei_reiner_biegung(q: Querschnitt, seite: Zugseite, einachsig: bool) -> Bruchpunkt
```

Der Bruchzustand bei N = 0, der diese Seite zieht -- einachsig mit waagrechter Nulllinie.

### DuktilitaetQA

```python
class DuktilitaetQA(Nachweis)
```

`x/d <= Grenze` bei reiner Biegung, je Richtung.

- `THEMA = 'Duktilität je Richtung'`
- `LANGNAME = 'Duktilität'`

#### DuktilitaetQA.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll)
```

### SproedesVersagenQA

```python
class SproedesVersagenQA(Nachweis)
```

`M_Rd(N = 0) >= M_Riss` je Richtung.

- `THEMA = 'Sprödes Versagen je Richtung'`
- `LANGNAME = 'Sprödes Versagen'`

#### SproedesVersagenQA.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll)
```


## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.nachweis.duktilitaet]]
- [[opencivil.nachweis.rissgroessen]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.interaktion]]
- [[opencivil.querschnitt.zugseite]]

## Gebraucht von

- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.aufbau.querschnittsanalyse]]

## Formeln aus diesem Modul

- [[Bedingung der Duktilität]] · `DuktilitaetQA.pruefe`
- [[Bedingung gegen sprödes Versagen]] · `SproedesVersagenQA.pruefe`
- [[Bezogene Druckzonenhöhe bei reiner Biegung]] · `DuktilitaetQA.pruefe`
