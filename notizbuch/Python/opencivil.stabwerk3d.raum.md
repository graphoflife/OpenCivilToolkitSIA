---
erzeugt: 772bbcc8af3d
art: modul
tags: [modul]
---
> [!abstract] opencivil/stabwerk3d/raum.py
> Vektoren, Richtungen und Strecken im Raum.
> Paket [[opencivil.stabwerk3d]] · [Quelltext](../../opencivil/stabwerk3d/raum.py)

## VERANTWORTUNG

Die Geometrie des raeumlichen Stabwerks: Vektoren als Tupel `(x, y, z)`,
Skalar- und Kreuzprodukt, orthonormale Basen aus Richtungen, Punkte auf
Strecken -- und eine Kraft mit ihrem Moment um den Ursprung. Nur die
Standardbibliothek.


## GENAUIGKEIT

Ein Punkt liegt auf einer Strecke, wenn er weniger als
[[opencivil.stabwerk.system#Konstanten|TOLERANZ]] daneben liegt -- so genau rundet
das Zeichenfenster. Eine Richtung zaehlt in einer Basis, wenn von ihr nach
Abzug der anderen mehr als 1e-9 bleibt.

## Inhalt

### skalar

```python
def skalar(a: Sequence[float], b: Sequence[float]) -> float
```

### kreuz

```python
def kreuz(a: Sequence[float], b: Sequence[float]) -> Vektor
```

### mal

```python
def mal(faktor: float, a: Sequence[float]) -> Vektor
```

### plus

```python
def plus(a: Sequence[float], b: Sequence[float]) -> Vektor
```

### minus

```python
def minus(a: Sequence[float], b: Sequence[float]) -> Vektor
```

### betrag

```python
def betrag(a: Sequence[float]) -> float
```

### punkt

```python
def punkt(p) -> Vektor
```

Der Ort eines Knotens -- oder von allem, was `x`, `y` und `z` hat.

### im_system

```python
def im_system(achsen: Sequence[Vektor], lokal: Sequence[float]) -> Vektor
```

Ein Vektor in den Achsen eines Stabs, in denen des Systems: `Rᵀ · v`.

### addiere

```python
def addiere(summe: List[float], ort: Sequence[float], kraft: Sequence[float], moment: Sequence[float]=NULL) -> None
```

Eine Kraft an `ort` und ein Moment zur Summe `(F, M)` -- das Moment um den Ursprung.

### orthonormal

```python
def orthonormal(vektoren: Sequence[Sequence[float]], gegen: Sequence[Vektor]=()) -> List[Vektor]
```

Die Richtungen von `vektoren` orthonormal, ohne was in `gegen` liegt (Gram-Schmidt).

### in_achsen

```python
def in_achsen(raum: Sequence[Vektor]) -> List[Vektor]
```

Eine orthonormale Basis des Raums, den die orthonormalen `raum`
aufspannen -- aus den Achsen des Systems, zuerst die, die am meisten
darin liegt. Eine Rolle auf waagrechter Bahn ist so frei in x, nicht in
-x und nicht schief.

### stelle_auf

```python
def stelle_auf(a, b, p) -> Optional[float]
```

Wo `p` auf der Strecke a-b liegt, in m ab a -- `None`, wenn daneben oder an einem Ende.

### kreuzen

```python
def kreuzen(p1, p2, q1, q2) -> bool
```

Ob sich die Strecken p1-p2 und q1-q2 im Innern beider treffen.


## Konstanten

- `ACHSEN = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))` – Die Achsen des Systems.
- `NULL = (0.0, 0.0, 0.0)`

## Braucht

- [[opencivil.stabwerk.system]]

## Gebraucht von

- [[opencivil.projekt.aufbau.balkensystem3d]]
- [[opencivil.projekt.balkensystem3d]]
- [[opencivil.stabwerk3d.herleitung]]
- [[opencivil.stabwerk3d.modell]]
- [[opencivil.stabwerk3d.stab]]
- [[opencivil.stabwerk3d.system]]
- [[opencivil.stabwerk3d.verlauf]]
