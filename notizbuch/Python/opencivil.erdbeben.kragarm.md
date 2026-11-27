---
erzeugt: 62910682b7df
art: modul
tags: [modul]
---
> [!abstract] opencivil/erdbeben/kragarm.py
> der Kern als Kragarm: Querkraft, Moment und Auslenkung.
> Paket [[opencivil.erdbeben]] · [Quelltext](../../opencivil/erdbeben/kragarm.py)

## VERANTWORTUNG

Das ebene Modell des Ersatzkraftverfahrens ([[opencivil.erdbeben.ersatzkraft|.ersatzkraft]]) je
Hauptrichtung: ein Kragarm, am Fuss eingespannt, die Kraefte waagrecht auf
der Hoehe der Decken. Querkraft und Moment unter jedem Geschoss
([[opencivil.erdbeben.kragarm#querkraefte|querkraefte]], [[opencivil.erdbeben.kragarm#momente|momente]]) und, Geschoss fuer Geschoss, die
Auslenkung des Dachs unter den Gewichten ([[opencivil.erdbeben.kragarm#beitraege|beitraege]]) – das u in
T_1 = 2 sqrt(u) (SIA 261:2020, 16.5.2.3, (40)). Die Herleitung schreibt
[[opencivil.erdbeben.ersatzkraft|.ersatzkraft]].

DIE AUSLENKUNG, nach dem Arbeitssatz:

```
u = Integral M(z) a(z) / EI(z) dz      ueber die Hoehe, a(z) = H - z
```

M ist das Moment aus den Gewichten, a das aus einer Kraft 1 am Dach.
Zwischen zwei Decken greift keine Kraft an: beide laufen dort gerade, und EI
ist das des Geschosses – es darf von Geschoss zu Geschoss wechseln, der
Kern oben duenner sein (Benutzer, 2026-11-27). Das Integral eines Geschosses
ist darum genau:

```
Delta u_i = h_i / (6 EI_i) * (M_u (2 a_u + a_o) + M_o (a_u + 2 a_o))
```

u steht fuer unten, an der Decke darunter, o fuer oben, an seiner. Mit einem
EI ueber die ganze Hoehe gibt die Summe u = Summe W_i z_i^2 (3 H - z_i) /
(6 EI) – so wurde bis 2026-11-27 gerechnet, mit allen Waenden ueber die
ganze Hoehe.


## EINHEITEN

SI-Basis: N, m, N m^2; u in m.

## Inhalt

### querkraefte

```python
def querkraefte(kraefte: Sequence[float]) -> Tuple[float, ...]
```

Je Geschoss, von unten, die Querkraft unter ihm: die Kraefte von dort bis oben.

### momente

```python
def momente(kraefte: Sequence[float], z: Sequence[float]) -> Tuple[float, ...]
```

Je Geschoss, von unten, das Moment unter ihm, auf der Hoehe der Decke
darunter: die Kraefte von dort bis oben, je mal ihr Abstand. Am Fuss ist
es das Kippmoment M_0 – der Kragarm ist dort eingespannt.

### Geschossbeitrag

```python
@dataclass(frozen=True)
class Geschossbeitrag
```

Was ein Geschoss zur Auslenkung des Dachs beitraegt – SI. `M` ist das
Moment aus den Gewichten, `a` das aus einer Kraft 1 am Dach, je unten
und oben im Geschoss.

- `h: float`
- `EI: float`
- `M_u: float`
- `M_o: float`
- `a_u: float`
- `a_o: float`

#### Geschossbeitrag.du

```python
@property
def du(self) -> float
```

Das Integral ueber das Geschoss – genau, beide Momente laufen gerade.

### beitraege

```python
def beitraege(z: Sequence[float], W: Sequence[float], EI: Sequence[float]) -> Tuple[Geschossbeitrag, ...]
```

Je Geschoss, von unten, sein Beitrag zur Auslenkung des Dachs: `z` die
Hoehen der Decken ueber der Einspannung, `W` die Gewichte, waagrecht
auf ihnen, `EI` die Biegesteifigkeit jedes Geschosses.


## Gebraucht von

- [[opencivil.erdbeben.ersatzkraft]]
- [[opencivil.web.erdbebendaten]]
