---
erzeugt: ad5b6f32b9b2
art: modul
tags: [modul]
---
> [!abstract] opencivil/decke/fem/element.py
> das Dreieck der Platte und der Balken in ihr.
> Paket [[opencivil.decke.fem]] · [Quelltext](../../opencivil/decke/fem/element.py)

## VERANTWORTUNG

Die Steifigkeit eines Dreiecks der Platte nach Kirchhoff, die eines Trägers
in ihrer Mittelebene, und wie aus den Verschiebungen ihre Schnittkräfte
werden. Je Knoten drei Unbekannte: die Durchbiegung `w`, nach unten
positiv, und ihre Neigungen `β_x = ∂w/∂x` und `β_y = ∂w/∂y`.


## DAS DREIECK (DKT, Batoz, Bathe und Ho 1980)

Die Neigungen ändern sich über das Dreieck quadratisch, durch ihre Werte an
den drei Ecken und den drei Mitten der Seiten. An den Ecken sind es die
Unbekannten; in einer Mitte legt sie die Kirchhoffsche Bedingung fest:

- längs der Seite ist `w` kubisch, durch `w` und die Neigung längs der
  Seite an ihren beiden Enden – in der Mitte ist die Neigung längs
  `β_s = 3/(2·l) · (w_j − w_i) − (β_s,i + β_s,j)/4`;
- quer zur Seite ändert sich die Neigung linear: `β_n = (β_n,i + β_n,j)/2`.

Damit sind die Krümmungen linear über das Dreieck, und die Momente auch:

```
κ = (∂β_x/∂x, ∂β_y/∂y, ∂β_x/∂y + ∂β_y/∂x)
m = (m_x, m_y, m_xy) = −D_b · κ
D_b = D · [[1, ν, 0], [ν, 1, 0], [0, 0, (1 − ν)/2]]      D = E·h³ / (12·(1 − ν²))
```

`m_x > 0` zieht unten, wie in der Streifenmethode, und `m_xy` gilt so,
dass in der Richtung `(cos φ, sin φ)` ``m_n = m_x·cos²φ + m_y·sin²φ +
2·m_xy·sin φ·cos φ`` ist ([[opencivil.decke.feld#in_xy|in_xy]]). Die
Steifigkeit `K = ∫ Bᵀ·D_b·B dA` ist mit den drei Mitten der Seiten genau,
je mit einem Drittel der Fläche: `Bᵀ·D_b·B` ist quadratisch.


## DER BALKEN

Ein Träger liegt als Balken in der Mittelebene der Platte, von Knoten zu
Knoten längs seiner Achse, ohne Torsionssteifigkeit (Entscheid 10 des Plans
vom 2026-11-27). Seine Durchbiegung ist kubisch, durch `w` und die Neigung
längs `w' = β_x·cos α + β_y·sin α` an beiden Enden; daher die bekannte
Steifigkeit `EI/L³ · [[12, 6L, −12, 6L], …]`. Sein Moment `M = −EI·w''`
zieht unten, wenn es positiv ist, und `V = dM/ds`.

## Inhalt

### steifigkeit_der_platte

```python
def steifigkeit_der_platte(E: float, h: float, nu: float) -> float
```

`D = E·h³ / (12·(1 − ν²))`, in Nm, mit E in N/m² und h in m.

### steifigkeit_des_traegers

```python
def steifigkeit_des_traegers(E: float, h: float, b: float, h_T: float) -> float
```

`EI = E·b·((h + h_T)³ − h³)/12` des Balkens eines Trägers, in Nm²: das
Rechteck `b × (h + h_T)` ohne den Teil, den die Platte schon trägt
(Entscheid 10 des Plans vom 2026-11-27).

### Dreieck

```python
class Dreieck
```

Ein Dreieck der Platte, seine Ecken im Gegenuhrzeigersinn: seine
Steifigkeit [[opencivil.decke.fem.element#Dreieck|K]] über `(w, β_x, β_y)` der drei Ecken und je Ecke,
wie die Momente dort aus den Unbekannten folgen ([[opencivil.decke.fem.element#Dreieck.momente|momente]]).

#### Dreieck._b

```python
def _b(self, xi: float, eta: float) -> Tuple[List[float], List[float], List[float]]
```

Die drei Zeilen von `B` an der Stelle `(ξ, η)`: κ_x, κ_y und κ_xy über den 9 Unbekannten.

#### Dreieck.momente

```python
def momente(self, u: Sequence[float]) -> List[Tuple[float, float, float]]
```

Je Ecke `(m_x, m_y, m_xy)` in Nm/m aus den 9 Unbekannten `u` des Dreiecks.

#### Dreieck.gefaelle

```python
def gefaelle(self, werte: Sequence[float]) -> Tuple[float, float]
```

`(∂/∂x, ∂/∂y)` einer Grösse, die über das Dreieck linear ist, aus ihren Werten an den Ecken.

### _neigungen

```python
def _neigungen(ecken: Sequence[Punkt]) -> List[List[Tuple[int, float, float]]]
```

Je Punkt der Neigungen – erst die Ecken, dann die Mitten der Seiten
2–3, 3–1, 1–2 –, wie `β_x` und `β_y` dort aus den 9 Unbekannten
folgen: Tripel `(Spalte, Beitrag zu β_x, Beitrag zu β_y)`.

In der Mitte einer Seite mit der Richtung `t` und der Länge `l`:

```
β = 3/(2·l) · t · (w_j − w_i) + (I/2 − 3/4 · t·tᵀ) · (β_i + β_j)
```

– die Neigung längs nach der kubischen Durchbiegung, quer das Mittel.

### balken

```python
def balken(L: float, EI: float) -> Matrix
```

Die Steifigkeit eines Balkens über `(w_i, w'_i, w_j, w'_j)`, `w'` längs seiner Achse.

### balken_in_der_platte

```python
def balken_in_der_platte(K4: Matrix, richtung: Punkt) -> Matrix
```

Die Steifigkeit des Balkens über `(w, β_x, β_y)` seiner beiden Knoten:
`w' = β_x·cos α + β_y·sin α`, `richtung = (cos α, sin α)`.

### balkenkraefte

```python
def balkenkraefte(K4: Matrix, u4: Sequence[float]) -> Tuple[float, float, float]
```

`(M_i, M_j, V)` eines Balkens aus seinen vier Unbekannten: die
Momente an seinen Enden, positiv mit Zug unten, und die Querkraft
`V = dM/ds` dazwischen – aus den Kräften an seinen Enden, `K·u`.


## Konstanten

- `ECKEN = ((0.0, 0.0), (1.0, 0.0), (0.0, 1.0))` – Die Ecken des Dreiecks in den Koordinaten `(ξ, η)`: dort liest das Glätten die Momente.
- `MITTEN = ((0.5, 0.0), (0.5, 0.5), (0.0, 0.5))` – Die Punkte der Integration, die Mitten der Seiten – je ein Drittel der Fläche.
- `SEITEN = ((1, 2), (2, 0), (0, 1))` – Die Seiten, an deren Mitte die Neigungen 4, 5 und 6 stehen: 2–3, 3–1 und 1–2.

## Braucht

- [[opencivil.decke.geometrie]]

## Gebraucht von

- [[opencivil.decke.fem.herleitung]]
- [[opencivil.decke.fem.rechnung]]
- [[opencivil.decke.fem.system]]
