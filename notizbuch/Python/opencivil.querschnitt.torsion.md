---
erzeugt: 9b597a3ca112
art: modul
tags: [modul]
---
> [!abstract] opencivil/querschnitt/torsion.py
> das Torsionstraegheitsmoment eines gezeichneten Querschnitts.
> Paket [[opencivil.querschnitt]] · [Quelltext](../../opencivil/querschnitt/torsion.py)

## VERANTWORTUNG

`I_T` nach St. Venant fuer die Polygone einer Querschnittsanalyse, mit
Aussparungen und Hohlraeumen, numerisch. Ein 3D-Balkensystem braucht es,
wenn ein Stab seinen Querschnitt aus einer Analyse nimmt
([[opencivil.stabwerk.stabquerschnitt#AusAnalyse|AusAnalyse]]): die Vorlagen der
Stabquerschnitte haben Formeln dafuer, ein beliebiges Polygon nicht. Am
Bruttoquerschnitt ohne Bewehrung, wie `A` und `I`.


## DIE SPANNUNGSFUNKTION VON PRANDTL

Im Material gilt ∇²φ = −2, am aeusseren Rand φ = 0. Am Rand eines
Hohlraums ist φ fest, φ_k, und hinaus fliesst so viel, wie er Flaeche hat:
∮ ∂φ/∂n ds = −2·A_k. Dann ist:

```
I_T = 2·∫ φ dA + 2·Σ φ_k·A_k
```

Getrennte Teile tragen je fuer sich. Liegt eines im Hohlraum eines anderen,
zaehlt es zu dessen Flaeche A_k, hat aber seinen eigenen Rand mit φ = 0.


## DAS GITTER

Ein Rechteckgitter ueber den Umriss, die laengere Seite in [[opencivil.querschnitt.torsion#Konstanten|TEILUNG]]
Zellen. Seine Linien laufen durch jede achsparallele Kante: Rechteck, T und
Hohlkasten liegen genau auf Zellraendern. Je Zelle mit Material ein Wert φ
in ihrer Mitte (finite Volumen). Durch die Kante zwischen zwei Zellen
fliesst ihre Laenge, geteilt durch den Abstand der Mitten, mal den
Unterschied in φ; liegt der Rand dazwischen, zaehlt der Abstand bis zu ihm,
genau geschnitten, auch an einer schraegen Kante. So bleibt die Matrix
symmetrisch, und der Fehler faellt mit dem Quadrat der Zellgroesse (Gibou,
Fedkiw, Cheng und Kang, J. Comput. Phys. 176, 2002). Ein Hohlraum ist ein
einziger Knoten, seine Last 2·A_k. Geloest mit konjugierten Gradienten, die
Diagonale als Vorkonditionierer; `I_T` ist dann Last mal Loesung.


## ZWEI GITTER UND RICHARDSON

Eine Wand mit n Zellen ueber ihre Dicke rechnet um 2/n² zu steif. Darum ein
zweites Gitter, jede Zelle halbiert, und I_T = (4·I_fein − I_grob)/3: das
hebt den quadratischen Fehler auf. Liegen die beiden mehr als
[[opencivil.querschnitt.torsion#Konstanten|ABWEICHUNG]] auseinander, ist das grobe Gitter fuer eine Wand zu grob
– meist fuer eine duenne schraege. Dann dasselbe feiner, solange das feine
Gitter nicht mehr als [[opencivil.querschnitt.torsion#Konstanten|ZELLEN_HOECHSTENS]] Zellen mit Material und
[[opencivil.querschnitt.torsion#Konstanten|GITTER_HOECHSTENS]] Zellen im Ganzen bekaeme.

Wie genau, zeigt `tests/test_torsion.py`: Rechteck, Dreieck, Kreis und
Rohr auf ein Promille, ein duenner Hohlkasten wie nach Bredt, bis auf das,
was seine Wanddicke dazugibt.

## Inhalt

### Gitterlauf

```python
@dataclass(frozen=True)
class Gitterlauf
```

`I_T` auf einem Gitter – wie fein es war und wie die Rechnung lief.

- `spalten: int` – Zellen in y.
- `zeilen: int` – Zellen in z.
- `zellen: int` – Davon mit Material: so viele Unbekannte, dazu eine je Hohlraum.
- `hohlraeume: Tuple[float, ...]` – Die Flaeche jedes Hohlraums auf diesem Gitter, in mm².
- `I_T: float` – In mm⁴.
- `schritte: int` – So viele Schritte brauchten die konjugierten Gradienten.

### Torsion

```python
@dataclass(frozen=True)
class Torsion
```

`I_T` eines Querschnitts – und die beiden Gitter, aus denen es kommt.

- `grob: Gitterlauf`
- `fein: Gitterlauf`

#### Torsion.I_T

```python
@property
def I_T(self) -> float
```

Nach Richardson aus beiden Gittern, in mm⁴.

### torsion

```python
def torsion(polygone: Sequence[Sequence[Punkt]], traegt: Sequence[bool], eltern: Sequence[Optional[int]]) -> Torsion
```

`I_T` der Polygone, in mm, wie sie die Zeichnung einer Analyse fuehrt:
je Polygon, ob es Material hat, und in welchem es liegt. Material ist,
wo das innerste Polygon Material hat.

### _Umriss

```python
class _Umriss
```

Die Polygone, befragt entlang einer Geraden: wo dort Material ist.

#### _Umriss.waagrecht

```python
def waagrecht(self, z: float) -> List[Strecke]
```

Die Strecken in y mit Material auf der Geraden auf Hoehe `z`.

#### _Umriss.lotrecht

```python
def lotrecht(self, y: float) -> List[Strecke]
```

Die Strecken in z mit Material auf der Geraden bei `y`.

#### _Umriss._strecken

```python
def _strecken(self, c: float, laengs: int) -> List[Strecke]
```

Wo die Gerade die Kanten schneidet – eine Ecke auf ihr zaehlt zur
Seite darunter –, und dazwischen, ob das innerste Polygon traegt.

### _darin

```python
def _darin(strecken: Sequence[Strecke], u: float) -> Optional[Strecke]
```

Die Strecke, in deren Innern `u` liegt.

### _gitter

```python
def _gitter(polygone: Sequence[Sequence[Punkt]]) -> Tuple[List[float], List[float]]
```

Die Gitterlinien in y und z: durch jede achsparallele Kante, dazwischen gleich geteilt.

### _halbiert

```python
def _halbiert(linien: Sequence[float]) -> List[float]
```

Jede Zelle halbiert.

### _lauf

```python
def _lauf(umriss: _Umriss, ys: Sequence[float], zs: Sequence[float]) -> Gitterlauf
```

Die Zellen einteilen, das Gleichungssystem aufstellen und loesen.

### _Zellen

```python
class _Zellen
```

Die Zellen eines Gitters, zeilenweise gezaehlt, `k = j·nx + i`. Eine
Zelle hat Material, wenn ihre Mitte darin liegt; ueber Kanten verbunden,
bilden solche Zellen einen Teil.

#### _Zellen.flaeche

```python
def flaeche(self, k: int) -> float
```

Die Flaeche von Zelle `k`, in mm².

#### _Zellen.hohlraeume

```python
def hohlraeume(self, t: int) -> List[Set[int]]
```

Die Hohlraeume von Teil `t`: was nicht zu ihm gehoert und den Rand
des Gitters nicht erreicht – samt einem anderen Teil darin.

#### _Zellen.fuellen

```python
def fuellen(self, start: Sequence[int], frei: Callable[[int], bool]) -> Set[int]
```

Die Zellen, die von `start` aus ueber Kanten erreichbar sind, nur durch freie.

### _System

```python
class _System
```

Das Gleichungssystem auf den Zellen: eine Unbekannte je Zelle mit
Material, dann eine je Hohlraum. Die Matrix als Diagonale und
Kopplungen, symmetrisch.

#### _System._reihe

```python
def _reihe(self, reihe: Sequence[int], mitten: Sequence[float], groessen: Sequence[float], strecken: Sequence[Optional[Strecke]], kante: float) -> None
```

Die Kanten zwischen den Zellen einer Zeile oder Spalte, auch die an
ihren Enden. Mitten, Groessen und Strecken gelten entlang der Reihe,
`kante` ist die Laenge jeder Kante quer dazu.

#### _System._zum_rand

```python
def _zum_rand(self, k: int, m: Optional[int], kante: float, abstand: float, zelle: float) -> None
```

Von Zelle `k` zum Rand hin, hinter dem `m` liegt: aussen φ = 0, sonst sein Hohlraum.

#### _System._koppeln

```python
def _koppeln(self, p: int, q: Optional[int], g: float) -> None
```

Leitwert `g` zwischen den Unbekannten `p` und `q`, ohne `q` zu φ = 0.

### _gradienten

```python
def _gradienten(diagonale: Sequence[float], kanten: Sequence[Tuple[int, int, float]], last: Sequence[float]) -> Tuple[List[float], int]
```

`A·x = last` mit konjugierten Gradienten, `A` aus Diagonale und
Kopplungen, die Diagonale als Vorkonditionierer.


## Konstanten

- `TEILUNG = 30` – In so viele Zellen teilt das grobe Gitter die laengere Seite des Umrisses.
- `ABWEICHUNG = 0.05` – So weit duerfen die beiden Gitter auseinanderliegen, relativ zum feinen.
- `ZELLEN_HOECHSTENS = 25000` – Mehr Zellen mit Material bekommt das feine Gitter nicht – so viele Unbekannte hat die Rechnung hoechstens.
- `GITTER_HOECHSTENS = 250000` – Mehr Zellen im Ganzen bekommt das feine Gitter nicht: eine duenne schraege Wand fuellt nur wenige davon, eingeteilt wird aber jede.
- `GENAUIGKEIT = 1e-09` – Die konjugierten Gradienten hoeren auf, wenn das Residuum so klein ist, relativ zur Last.
- `NAEHE = 0.01` – Naeher liegt keine Mitte am Rand, relativ zu ihrer Zelle – sonst wuechse der Fluss dorthin ohne Grenze.

## Braucht

- [[opencivil.querschnitt.geometrie]]

## Gebraucht von

- [[opencivil.querschnitt.analyse]]
