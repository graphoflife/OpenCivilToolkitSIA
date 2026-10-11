---
erzeugt: b03c6de231d5
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

Das Rissmoment gehoert dem ungerissenen Bruttoquerschnitt, gerechnet mit
`I_yz` fuer die unsymmetrische Biegung; `k_t` mit einem Drittel der Hoehe
in Biegerichtung -- die Regel der Platte, uebertragen. Nach Vorgabe, nicht
nachgeschlagen (`notizbuch/Notizen/TODO.md`).

## Inhalt

### richtungen

```python
def richtungen(einachsig: bool) -> Tuple[Tuple[str, float, float], ...]
```

Einachsig nur unten und oben -- um z wird dann nicht nachgewiesen.

### bei_reiner_biegung

```python
def bei_reiner_biegung(q: Querschnitt, M_y: float, M_z: float, einachsig: bool) -> Bruchpunkt
```

Der Bruchzustand bei N = 0 in dieser Richtung -- einachsig mit waagrechter Nulllinie.

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

#### SproedesVersagenQA._hoehe

```python
def _hoehe(self, um_y: bool) -> float
```

Die Ausdehnung des Betons in Biegerichtung, in m: z bei M_y, y bei M_z.

#### SproedesVersagenQA._w_vorlage

```python
@staticmethod
def _w_vorlage(M_y: float, M_z: float) -> str
```

`W = 1/σ` bei einem Moment von eins -- je Richtung ausgeschrieben.


## Konstanten

- `RICHTUNGEN = (('Zug unten', 1.0, 0.0), ('Zug oben', -1.0, 0.0), ('Zug links', 0.0,…` – Die Richtungen: Name, und das Moment, das so zieht (M_y, M_z).

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.nachweis.duktilitaet]]
- [[opencivil.nachweis.sproedes_versagen]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.interaktion]]

## Gebraucht von

- [[opencivil.projekt.aufbau]]

## Formeln aus diesem Modul

- [[Bedingung der Duktilität]] · `DuktilitaetQA.pruefe`
- [[Bedingung gegen sprödes Versagen]] · `SproedesVersagenQA.pruefe`
- [[Bezogene Druckzonenhöhe bei reiner Biegung]] · `DuktilitaetQA.pruefe`
- [[Rissmoment des ungerissenen Querschnitts]] · `SproedesVersagenQA.pruefe`
- [[Spannung im ungerissenen Querschnitt]] · `SproedesVersagenQA.pruefe`
- [[Widerstandsmoment zum gezogensten Betonpunkt]] · `SproedesVersagenQA.pruefe`
