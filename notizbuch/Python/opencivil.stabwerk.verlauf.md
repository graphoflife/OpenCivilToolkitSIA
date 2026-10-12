---
erzeugt: 48d14bf9687c
art: modul
tags: [modul]
---
> [!abstract] opencivil/stabwerk/verlauf.py
> Schnittgroessen und Biegelinie laengs eines Stabs.
> Paket [[opencivil.stabwerk]] · [Quelltext](../../opencivil/stabwerk/verlauf.py)

## VERANTWORTUNG

Aus dem, was [[opencivil.stabwerk.system|system]] an den Enden jedes Teilstabs
findet -- Kraefte und Verschiebungen --, und aus seinen Lasten die Verlaeufe
dazwischen: Normalkraft, Querkraft, Moment, Laengs- und Querverschiebung.
Dazu die groessten und kleinsten Werte und wo sie liegen.


## VORZEICHEN DER BAUSTATIK

Die Schnittgroessen stehen, wie man sie von Hand rechnet: `N > 0` ist Zug;
`M > 0` zieht an der gestrichelten Faser, der rechten Seite des Stabs vom
Anfang zum Ende gesehen -- bei einem Stab von links nach rechts unten;
`V = dM/dx + m` (`m` ein verteiltes Moment im Gegenuhrzeigersinn). Ein
Einfeldtraeger unter Last nach unten hat also ein positives Feldmoment und
links eine positive Querkraft.

Aus den Kraeften `s` auf die Enden (in den Achsen des Stabs, y links,
Gegenuhrzeigersinn) folgt am Anfang:

```python
N(0) = -s_u      V(0) = s_v      M(0) = -s_θ
```

und mit den Lasten `p_x`, `p_y` und `m` laengs des Stabs:

```
dN/dx = -p_x     dV/dx = p_y     dM/dx = V - m
```

Eine Einzelkraft laesst N um `-P_x` und V um `+P_y` springen, ein
Einzelmoment M um `-M`.


## STUECKWEISE POLYNOME

Zwischen zwei Laststellen sind die Lasten linear -- also V quadratisch, M
kubisch, die Biegelinie vom fuenften Grad. Gerechnet wird darum genau, mit
Polynomen ([[opencivil.stabwerk.verlauf#Polynom|Polynom]]), nicht an Stuetzstellen. Ein gebetteter Teilstab
traegt dazu `-k · v(x)` mit der kubischen Biegelinie seiner Enden; dort ist
es die Naeherung, mit der auch gerechnet wurde.

Die Biegelinie folgt aus `v'' = M/EI` und `u' = N/EA`, je Teilstab von
seinem Anfang aus -- Verschiebung und Drehung dort sind die der Loesung, am
Ende trifft sie die des Endes (eine Probe in den Tests).


## EXTREMWERTE

Ein Moment ist dort am groessten, wo `dM/dx = V - m` null wird, oder an
einer Grenze: einem Stabende, einer Laststelle -- dort auf beiden Seiten.
Gesucht wird an genau diesen Stellen, nicht im Raster der Bilder.

## Inhalt

### Polynom

```python
class Polynom
```

`k[0] + k[1]·x + k[2]·x² + …` -- mit Grad, so hoch es sein muss.

#### Polynom.durch

```python
@classmethod
def durch(cls, x0: float, y0: float, x1: float, y1: float) -> 'Polynom'
```

Die Gerade durch zwei Punkte -- waagrecht, wo sie zusammenfallen.

#### Polynom.stammfunktion

```python
def stammfunktion(self, ab: float) -> 'Polynom'
```

`∫_ab^x p(ξ) dξ` -- null bei `x = ab`.

#### Polynom.ableitung

```python
def ableitung(self) -> 'Polynom'
```

#### Polynom.nullstellen

```python
def nullstellen(self, a: float, b: float, stellen: int=48) -> List[float]
```

Wo es in `(a, b)` das Vorzeichen wechselt -- abgetastet und halbiert.

### Intervall

```python
@dataclass
class Intervall
```

Ein Stueck eines Stabs ohne Laststelle -- alles darauf Polynome in x ab dem Stabanfang.

- `x0: float`
- `x1: float`
- `N: Polynom`
- `V: Polynom`
- `M: Polynom`
- `u: Polynom` – Laengs, in x des Stabs.
- `v: Polynom` – Quer, in y des Stabs -- links positiv.
- `theta: Polynom`
- `p_y: Polynom = field(default_factory=lambda: NULL)` – Die Querlast samt Bettung -- fuer das, was ins Linienlager geht.

### Extrem

```python
@dataclass(frozen=True)
class Extrem
```

Der kleinste und der groesste Wert einer Groesse, je mit Stelle.

- `kleinst: Tuple[float, float]`
- `groesst: Tuple[float, float]`

### Stabverlauf

```python
@dataclass
class Stabverlauf
```

Ein Stab von Anfang bis Ende -- ueber alle seine Teilstaebe.

- `stab: str`
- `L: float`
- `c: float`
- `s: float`
- `x_a: float`
- `z_a: float`
- `intervalle: List[Intervall] = field(default_factory=list)`

#### Stabverlauf.bei

```python
def bei(self, x: float, links: bool=False) -> Dict[str, float]
```

Die Werte an der Stelle `x` -- an einer Sprungstelle rechts davon,
mit `links` links davon.

#### Stabverlauf.sehne

```python
def sehne(self, x: float) -> float
```

Die Querverschiebung der Sehne zwischen den Stabenden -- fuer die relative Durchbiegung.

#### Stabverlauf.proben

```python
def proben(self, je_stab: int=24) -> List[Dict[str, float]]
```

Werte zum Zeichnen: an beiden Seiten jeder Grenze und dazwischen so
dicht, dass ein Stab rund `je_stab` Stuecke hat.

#### Stabverlauf.extremstellen

```python
def extremstellen(self) -> List[float]
```

Wo ein Moment, eine Querkraft oder eine Normalkraft im Innern eines Stuecks extrem ist.

#### Stabverlauf.extrem

```python
def extrem(self, groesse: str) -> Extrem
```

Kleinster und groesster Wert von `N`, `V`, `M` oder `w` (der
Durchbiegung gegen die Sehne), mit Stelle.

### verlaeufe

```python
def verlaeufe(fall) -> Dict[str, Stabverlauf]
```

Je Stab sein Verlauf in diesem Fall -- aus den Teilstaeben, der Reihe nach.

### teilverlauf

```python
def teilverlauf(teil) -> List[Intervall]
```

Die Intervalle eines Teilstabs, in x ab dem Anfang seines Stabs -- aus
den Kraeften und Verschiebungen seiner Enden und seinen Lasten.

### _hermite

```python
def _hermite(L: float, v1: float, t1: float, v2: float, t2: float) -> Polynom
```

Die kubische Biegelinie aus den Enden -- die Form, mit der die Bettung gerechnet wurde.

### _verschoben

```python
def _verschoben(i: Intervall, um: float) -> Intervall
```

Dasselbe Intervall in x ab dem Anfang des ganzen Stabs.

### _schieben

```python
def _schieben(p: Polynom, um: float) -> Polynom
```

`q(x) = p(x - um)`.


## Konstanten

- `NULL = Polynom((0.0,))`

## Braucht

- [[opencivil.stabwerk.stab]]

## Gebraucht von

- [[opencivil.stabwerk.rechnung]]
