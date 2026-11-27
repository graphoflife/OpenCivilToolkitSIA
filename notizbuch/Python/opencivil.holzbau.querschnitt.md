---
erzeugt: a0ddc4eee297
art: modul
tags: [modul]
---
> [!abstract] opencivil/holzbau/querschnitt.py
> ein gezeichneter Querschnitt aus Holz.
> Paket [[opencivil.holzbau]] · [Quelltext](../../opencivil/holzbau/querschnitt.py)

## VERANTWORTUNG

Was Kennzahlen und Nachweise eines Holzquerschnitts
([[opencivil.nachweis.qa_holz]]) aus der Zeichnung brauchen, ohne
Rechenwerk und ohne Herleitung, in mm: die Polygone mit ihrem Gewicht, die
Ausdehnung, je Achse den Abstand der weitesten Faser, den Schnitt, an dem
eine Querkraft die groesste Schubspannung weckt, und beim Rechteck den
Beiwert der Torsion.


## LINEAR (SIA 265:2012, 4.1.2)

Die Spannungen sind elastisch, am Bruttoquerschnitt, wie die Werte der
Analyse. y und z gelten als Hauptachsen, wie beim Stahl
([[opencivil.stahlbau.querschnitt]]): eine Biegung um y hat ihre
Nulllinie waagrecht. Die Biegespannung je Achse ist die an der weitesten
Faser – beim Rechteck M/W; bei einem Querschnitt, dessen Fasern ungleich
weit vom Schwerpunkt liegen, auf der sicheren Seite (nach Vorgabe, nicht
nachgeschlagen).


## SCHUB AUS QUERKRAFT

`τ = V·S/(I·b)` nach Jourawski, auf dem Schnitt quer zur Querkraft, auf
dem `S/b` am groessten ist – gesucht zwischen je zwei Ecken auf
[[opencivil.holzbau.querschnitt#Konstanten|TEILE]] Schnitten und im Schwerpunkt. Beim Rechteck ist das die
Mitte, mit `τ = 1.5·V/A`.


## SCHUB AUS TORSION

Nur fuer ein Rechteck, die Seiten parallel zu y und z
([[opencivil.holzbau.querschnitt#Holzquerschnitt.rechteck|Holzquerschnitt.rechteck]]): `τ_tor = T/W_T` mit `W_T = k_2·h·b²`,
`b` die kurze Seite, `k_2` aus den Reihen von Saint-Venant
([[opencivil.holzbau.querschnitt#k_2|k_2]]). Fuer einen anderen Querschnitt gibt es keine solche Formel;
dort weist das Werkzeug Torsion nicht nach (nach Vorgabe, nicht
nachgeschlagen).

## Inhalt

### Schubschnitt

```python
@dataclass(frozen=True)
class Schubschnitt
```

Der Schnitt mit dem groessten `S/b`: `S` in mm³, `b` und `lage` in mm.

- `S: float`
- `b: float`
- `lage: float` – Wo er liegt: `z` fuer eine Querkraft in z, `y` fuer eine in y.

#### Schubschnitt.faktor

```python
@property
def faktor(self) -> float
```

`S/b` in mm² – mal `V/I` gibt das `τ`.

### Holzquerschnitt

```python
@dataclass(frozen=True)
class Holzquerschnitt
```

Die Polygone eines Holzquerschnitts, je mit ihrem Gewicht – +1 mit Holz,
-1 fuer eine Aussparung darin –, und sein Schwerpunkt, in mm.

- `polygone: Tuple[Tuple[Tuple[Punkt, ...], float], ...]`
- `y_S: float`
- `z_S: float`

#### Holzquerschnitt.aus

```python
@classmethod
def aus(cls, zeichnung) -> 'Holzquerschnitt'
```

Aus der Zeichnung einer Analyse ([[opencivil.querschnitt.analyse#Zeichnung|Zeichnung]]).

#### Holzquerschnitt.ausdehnung

```python
@cached_property
def ausdehnung(self) -> Tuple[float, float, float, float]
```

`(y_min, y_max, z_min, z_max)` des Holzes.

#### Holzquerschnitt.faser

```python
def faser(self, achse: str) -> float
```

Wie weit die weiteste Faser einer Biegung um `achse` vom Schwerpunkt liegt.

#### Holzquerschnitt.hoehe

```python
def hoehe(self, achse: str) -> float
```

Die Hoehe einer Biegung um `achse`: in z um y, in y um z.

#### Holzquerschnitt.breite

```python
def breite(self, achse: str) -> float
```

Die Breite quer dazu.

#### Holzquerschnitt.rechteck

```python
@cached_property
def rechteck(self) -> bool
```

Ob der Querschnitt ein einziges Rechteck ist, die Seiten parallel zu y und z.

#### Holzquerschnitt.schubschnitt

```python
def schubschnitt(self, richtung: str) -> Optional[Schubschnitt]
```

Der Schnitt quer zu einer Querkraft in `richtung` ("y" oder "z"),
auf dem `S/b` am groessten ist – `None`, wo keiner Holz trifft.

#### Holzquerschnitt._schnitt

```python
def _schnitt(self, normale: Tuple[float, float], v: float, schwer: float) -> Tuple[float, float]
```

Das statische Moment jenseits von `n·p = v` um die Schwerachse und die Breite dort.

#### Holzquerschnitt.seiten

```python
@property
def seiten(self) -> Tuple[float, float]
```

Die kurze und die lange Seite des Rechtecks, `(b, h)`.

### k_2

```python
def k_2(verhaeltnis: float) -> float
```

Der Beiwert `k_2` in `W_T = k_2·h·b²` eines Rechtecks mit
`h/b = verhaeltnis ≥ 1` – aus den Reihen von Saint-Venant fuer
`I_T = β·h·b³` und die groesste Schubspannung, `τ = c·T·b/I_T`, in der
Mitte der langen Seite: `k_2 = β/c`. 0.208 beim Quadrat, gegen 1/3 beim
schmalen Rechteck.

### _reihe

```python
def _reihe(glied) -> float
```

Die Summe ueber die ungeraden `n`, bis ein Glied kleiner ist als [[opencivil.holzbau.querschnitt#Konstanten|GLIED]].

### _sech

```python
def _sech(x: float) -> float
```

`1/cosh x` – auch fuer grosse `x`, wo `cosh` ueberliefe.

### starke_achse

```python
def starke_achse(I_y: float, I_z: float) -> str
```

Die Achse mit dem groesseren Traegheitsmoment, gleich gross y: nur eine
Biegung um sie kann den Stab kippen lassen. Beim Rechteck die um die
lange Seite.


## Konstanten

- `TEILE = 64` – Auf so vielen Schnitten zwischen zwei Ecken sucht der Schub seine Stelle.
- `PARALLEL = 1e-09` – Wie genau ein Rechteck seine Seiten parallel zu y und z haben muss, relativ zu seiner Groesse.
- `GLIED = 1e-15` – Die Reihen von Saint-Venant enden, wo ihr Glied kleiner ist als das.

## Braucht

- [[opencivil.querschnitt.geometrie]]

## Gebraucht von

- [[opencivil.nachweis.qa_holz_stabilitaet]]
- [[opencivil.nachweis.qa_holz_werte]]
