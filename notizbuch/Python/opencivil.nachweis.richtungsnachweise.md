---
erzeugt: 195cf92f1a10
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
nachgeschlagen (`notizbuch/Notizen/TODO.md`). Die Zwaengung auf Biegung
([[opencivil.nachweis.qa_gebrauch]]) haelt dasselbe Rissmoment gegen
ihre Bewehrung: es steht darum hier einmal ([[opencivil.nachweis.richtungsnachweise#rissmoment|rissmoment]]).

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

### Rissmoment

```python
@dataclass(frozen=True)
class Rissmoment
```

Das Rissmoment des Bruttoquerschnitts in einer Richtung -- und woraus es entsteht.

- `ecke: Punkt` – Der gezogenste Betonpunkt, in mm.
- `stoff: Baustoff` – Sein Beton: er gibt `f_ctm`.
- `W: float` – Das Widerstandsmoment zu diesem Punkt, m³.
- `hoehe: float` – Die Ausdehnung des Betons in Biegerichtung, m -- fuer `k_t`.
- `k_t: float`
- `f_ct_eff: float`
- `M_Riss: float` – in Nm.

### rissbezuege

```python
def rissbezuege(analyse: Querschnittsanalyse) -> List[Eingabebezug]
```

Was das Rissmoment liest, ueber die Grundbezuege hinaus: die Traegheitsmomente.

### rissmoment

```python
def rissmoment(analyse: Querschnittsanalyse, e: Eingaben, M_y: float, M_z: float) -> Rissmoment
```

Das Rissmoment in der Richtung `(M_y, M_z)` -- einem Moment von eins,
wie in [[opencivil.nachweis.richtungsnachweise#Konstanten|RICHTUNGEN]]. Es reisst der gezogenste Betonpunkt, gerechnet
mit `I_yz` fuer die unsymmetrische Biegung.

### protokoll_spannung_ungerissen

```python
def protokoll_spannung_ungerissen(p: Protokoll) -> None
```

Wie der ungerissene Querschnitt Spannung traegt -- der Ansatz des Rissmoments.

### protokoll_rissmoment

```python
def protokoll_rissmoment(p: Protokoll, e: Eingaben, analyse: Querschnittsanalyse, werte: Zwischenwerte, riss: Rissmoment, M_y: float, M_z: float, *, referenz: str) -> Wert
```

Die Herleitung von [[opencivil.nachweis.richtungsnachweise#rissmoment|rissmoment]] -- zurueck kommt `M_Riss`.

### _hoehe

```python
def _hoehe(analyse: Querschnittsanalyse, um_y: bool) -> float
```

Die Ausdehnung des Betons in Biegerichtung, in m: z bei M_y, y bei M_z.

### _w_vorlage

```python
def _w_vorlage(M_y: float, M_z: float) -> str
```

`W = 1/σ` bei einem Moment von eins -- je Richtung ausgeschrieben.

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


## Konstanten

- `RICHTUNGEN = (('Zug unten', 1.0, 0.0), ('Zug oben', -1.0, 0.0), ('Zug links', 0.0,…` – Die Richtungen: Name, und das Moment, das so zieht (M_y, M_z).

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.material.basis]]
- [[opencivil.nachweis.duktilitaet]]
- [[opencivil.nachweis.sproedes_versagen]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.geometrie]]
- [[opencivil.querschnitt.interaktion]]

## Gebraucht von

- [[opencivil.nachweis.qa_gebrauch]]
- [[opencivil.projekt.aufbau]]

## Formeln aus diesem Modul

- [[Bedingung der Duktilität]] · `DuktilitaetQA.pruefe`
- [[Bedingung gegen sprödes Versagen]] · `SproedesVersagenQA.pruefe`
- [[Bezogene Druckzonenhöhe bei reiner Biegung]] · `DuktilitaetQA.pruefe`
- [[Rissmoment des ungerissenen Querschnitts]] · `protokoll_rissmoment`
- [[Spannung im ungerissenen Querschnitt]] · `protokoll_spannung_ungerissen`
- [[Widerstandsmoment zum gezogensten Betonpunkt]] · `protokoll_rissmoment`
