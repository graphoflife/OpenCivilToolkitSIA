---
erzeugt: cba2cde7d1ec
art: modul
tags: [modul]
---
> [!abstract] opencivil/stabwerk3d/system.py
> das raeumliche Stabwerk: Unbekannte, Zusammenbau, Loesen.
> Paket [[opencivil.stabwerk3d]] · [Quelltext](../../opencivil/stabwerk3d/system.py)

## VERANTWORTUNG

Wie [[opencivil.stabwerk.system]], im Raum: aus dem
[[opencivil.stabwerk3d.modell#System|System]] die Unbekannten, die
Steifigkeitsmatrix und je Lastfall und Kombination die rechte Seite -- und
nach dem Loesen Verschiebungen, Stabendkraefte und Lagerkraefte. Was dort
ueber Orte und Teilstaebe, die Teilung gebetteter Staebe, feste
Linienlager und Meldungen steht, gilt hier genauso; hier steht, was der
Raum anders macht.


## UNBEKANNTE

Je Ort drei Verschiebungen und drei Drehungen, weniger was festgehalten ist
-- als Richtungen im Raum: ein Lager haelt in x, y oder z des Systems, ein
festes Linienlager laengs oder quer zu seinem Stab, also auch schief. Je Ort
eine orthonormale Basis aus den festen Richtungen und dem, was frei bleibt;
unbekannt sind nur die freien, moeglichst entlang der Achsen des Systems.


## GELENKE -- NACH VORGABE, NICHT NACHGESCHLAGEN

Ein Gelenk am Stabende loest alle drei Momente, wie ein Kugelgelenk. Das
Stabende bekommt eigene Drehungen als Unbekannte -- um y und z des Stabs,
und um x, wenn er Torsion traegt. Mit Gelenken an beiden Enden traegt er
keine: er drehte sich sonst frei um seine Achse. Ein Fachwerk aus lauter
gelenkig angeschlossenen Staeben rechnet so wie in der Ebene; ein Moment um
die Achse eines solchen Stabs hat keinen Halt und ist ein Fehler.


## DREHUNG OHNE STEIFIGKEIT

In der Ebene hat ein Knoten nur an Gelenken keine Drehsteifigkeit. Im Raum
hat er sie um die Achsen, die ein starr angeschlossener Stab, eine
Drehfeder oder eine Einspannung halten -- und um die uebrigen nicht. Diese
sind gestrichen und null gesetzt ([[opencivil.stabwerk.system#Konstanten|UNBESTIMMT]]),
erkannt an der Verbindung, nicht an einer Zahl. Greift dort ein Moment an,
ist das ein Fehler.

Die Torsion haelt einen Knoten nur, wenn etwas das andere Ende des Stabs
haelt. Haelt nichts, dreht sich der Stab mit dem Knoten um seine Achse: Das
System ist beweglich, und die Meldung sagt, dass sich dabei nichts
verschiebt. Ein einfacher Balken auf zwei gelenkigen Lagern braucht darum
an einem Ende eine Gabel -- ein Lager, das die Drehung um seine Achse
festhaelt.


## FESTE LINIENLAGER

Liegt ein Stab quer in z fest auf, biegt er sich nicht in seiner
x-z-Ebene: seine Verschiebung in z ist an jedem Ort null, und wo er ohne
Gelenk anschliesst, auch die Drehung um seine y-Achse. Seine Lasten in
dieser Ebene gehen geradewegs ins Lager. Quer in y und laengs ebenso; die
Torsion traegt er weiter.

## Inhalt

### Ort

```python
@dataclass
class Ort
```

Ein Punkt des Systems mit Unbekannten -- ein Knoten oder ein Punkt in einem Stab.

- `name: str`
- `x: float`
- `y: float`
- `z: float`
- `knoten: Optional[str] = None` – Der Knoten der Beschreibung -- `None` im Innern eines Stabs.
- `stab: Optional[str] = None`
- `stelle: float = 0.0` – Bei einem inneren Ort: wo auf welchem Stab, in m ab seinem Anfang.
- `zwang: List[Vektor] = field(default_factory=list)` – Die Richtungen, in denen er nicht verschoben wird -- wie gesammelt.
- `drehzwang: List[Vektor] = field(default_factory=list)` – Die Achsen, um die er nicht gedreht wird -- wie gesammelt.
- `steif: List[Vektor] = field(default_factory=list)` – Die Achsen, um die ihn etwas steif haelt: Staebe und Drehfedern -- wie gesammelt.
- `fest: List[Vektor] = field(default_factory=list)`
- `frei: List[Vektor] = field(default_factory=list)` – Orthonormal: die festen und die freien Richtungen der Verschiebung.
- `dreh_fest: List[Vektor] = field(default_factory=list)`
- `dreh_frei: List[Vektor] = field(default_factory=list)`
- `offen: List[Vektor] = field(default_factory=list)` – Orthonormal: die Drehachsen -- fest, frei und ohne Steifigkeit, also gestrichen.
- `verschiebung: List[int] = field(default_factory=list)` – Je freie Richtung die Nummer ihrer Unbekannten.
- `drehung: List[int] = field(default_factory=list)` – Je freie Drehachse die Nummer ihrer Unbekannten.
- `feder: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])` – Federn in x, y und z des Systems, N/m.
- `drehfeder: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])` – Drehfedern um x, y und z des Systems, Nm/rad.

#### Ort.punkt

```python
@property
def punkt(self) -> Vektor
```

#### Ort.gehalten

```python
@property
def gehalten(self) -> bool
```

Ob hier eine Lagerkraft entsteht: etwas Festes oder eine Feder.

### Teilstab

```python
@dataclass
class Teilstab
```

Ein Stueck eines Stabs zwischen zwei Orten.

- `stab: Stab`
- `nummer: int`
- `x0: float`
- `x1: float`
- `a: Ort`
- `b: Ort`
- `achsen: Tuple[Vektor, Vektor, Vektor]`
- `L_stab: float = 0.0` – Die Laenge des ganzen Stabs.
- `k_y: float = 0.0`
- `k_z: float = 0.0`
- `k_x: float = 0.0` – Die Bettung quer in y und z und laengs, N/m².
- `biegung_y: bool = True` – Ob er sich in seiner x-y-Ebene biegt -- nicht, wenn er quer in y fest aufliegt.
- `biegung_z: bool = True` – Ob er sich in seiner x-z-Ebene biegt -- nicht, wenn er quer in z fest aufliegt.
- `laengs: bool = True` – Ob er sich dehnt -- nicht, wenn er laengs fest aufliegt.
- `torsion: bool = True` – Ob er Torsion traegt -- nicht, wenn sein Stab an beiden Enden ein Gelenk hat.
- `gelenk_a: bool = False`
- `gelenk_b: bool = False`
- `gelenkindizes: Dict[Tuple[str, int], int] = field(default_factory=dict)` – Je Ende (`a`, `b`) und Achse des Stabs (0, 1, 2) die Nummer seiner Drehung am Gelenk.
- `k: List[List[float]] = field(default_factory=list)`
- `abbildung: List[List[Tuple[int, float]]] = field(default_factory=list)` – Je lokale Unbekannte (u, v, w, θx, θy, θz am Anfang, dann am Ende): `[(Nummer, Beiwert)]`.

#### Teilstab.L

```python
@property
def L(self) -> float
```

#### Teilstab.EA

```python
@property
def EA(self) -> float
```

#### Teilstab.EI_y

```python
@property
def EI_y(self) -> float
```

#### Teilstab.EI_z

```python
@property
def EI_z(self) -> float
```

#### Teilstab.GI_T

```python
@property
def GI_T(self) -> float
```

#### Teilstab.gesperrt

```python
@property
def gesperrt(self) -> Tuple[int, ...]
```

Die lokalen Unbekannten der Teile, die er nicht traegt: wo ein festes
Linienlager alles nimmt, und die Torsion zwischen zwei Gelenken.

#### Teilstab.lokal

```python
def lokal(self, x: Sequence[float]) -> List[float]
```

Die Verschiebungen seiner Enden, in seinen Achsen, aus der Loesung `x`.

#### Teilstab.bettungsmatrix

```python
def bettungsmatrix(self) -> List[List[float]]
```

### Teilergebnis

```python
@dataclass
class Teilergebnis
```

Was ein Teilstab in einem Fall tut -- in seinen Achsen.

- `teil: Teilstab`
- `lasten: st3.Lasten`
- `f: List[float]` – Die arbeitsgleichen Knotenkraefte seiner Lasten.
- `d: List[float]` – Die Verschiebungen seiner Enden.
- `s: List[float]` – Die Kraefte auf seine Enden: `k · d - f`.

### Fall

```python
@dataclass
class Fall
```

Ein Lastfall oder eine Kombination, gerechnet.

- `name: str`
- `kombination: bool`
- `lasten: List`
- `F: List[float]`
- `x: List[float]`
- `teile: List[Teilergebnis]`
- `verschiebungen: Dict[str, Sechs]` – Je Ort `(u_x, u_y, u_z, φ_x, φ_y, φ_z)` -- auch die inneren.
- `lagerkraefte: Dict[str, Sechs]` – Je gehaltenen Ort `(R_x, R_y, R_z, M_x, M_y, M_z)`, auf das Tragwerk wirkend.
- `linienlast: Dict[str, Sechs]` – Je fest aufliegenden Stab, was seine Lasten geradewegs ins Lager geben -- Kraft und Moment um den Ursprung.
- `bettung: Dict[str, Sechs]` – Je gebetteten Stab die Summe der Bettungskraefte auf das Tragwerk -- ebenso.
- `lastsumme: Sechs`
- `gleichgewicht: Sechs` – Was in den Summen der Kraefte und der Momente um den Ursprung uebrig bleibt -- null bis auf Rundung.

### Ergebnis

```python
@dataclass
class Ergebnis
```

- `meldungen: List[Meldung] = field(default_factory=list)`
- `orte: Dict[str, Ort] = field(default_factory=dict)`
- `teilstaebe: List[Teilstab] = field(default_factory=list)`
- `unbekannte: List[str] = field(default_factory=list)` – Je Unbekannte ein Name, fuer die Herleitung: `u_x(K1)`, `φ_z(K2)`, `θ_y(L3, Ende)`.
- `K: Optional[Profilmatrix] = None`
- `faelle: List[Fall] = field(default_factory=list)`
- `beweglich: List[str] = field(default_factory=list)` – Was sich ohne Widerstand bewegt, wenn das System beweglich ist.

#### Ergebnis.gueltig

```python
@property
def gueltig(self) -> bool
```

#### Ergebnis.fall

```python
def fall(self, name: str) -> Fall
```

#### Ergebnis.unbestimmt

```python
def unbestimmt(self) -> List[str]
```

Die Knoten, deren Drehung um eine Achse gestrichen ist.

### _name

```python
def _name(zeichen: str, ort: str, richtung: Vektor) -> str
```

`u_x(K1)` entlang einer Achse, sonst mit der Richtung.

### _traegt_torsion

```python
def _traegt_torsion(stab_: Stab) -> bool
```

Ob ein Stab Torsion traegt: nicht mit Gelenken an beiden Enden -- siehe Dateikopf.

### rechnen

```python
def rechnen(system: System) -> Ergebnis
```

Das System, gerechnet -- oder, wo das nicht geht, die Meldungen dazu.

### _ende

```python
def _ende(t: Teilstab, ende: str) -> List[List[Tuple[int, float]]]
```

Wie u, v, w und θx, θy, θz eines Stabendes an den Unbekannten haengen.


## Konstanten

- `_ZEICHEN = 'xyz'` – Je Achse ihr Zeichen -- fuer die Namen der Unbekannten.

## Braucht

- [[opencivil.stabwerk.matrix]]
- [[opencivil.stabwerk.modell]]
- [[opencivil.stabwerk.stab]]
- [[opencivil.stabwerk.system]]
- [[opencivil.stabwerk3d.modell]]
- [[opencivil.stabwerk3d.raum]]
- [[opencivil.stabwerk3d.stab]]

## Gebraucht von

- [[opencivil.stabwerk3d.herleitung]]
- [[opencivil.stabwerk3d.rechnung]]
