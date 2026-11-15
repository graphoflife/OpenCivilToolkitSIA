---
erzeugt: 5801bc3c1261
art: modul
tags: [modul]
---
> [!abstract] opencivil/stabwerk3d/modell.py
> was gerechnet wird: das raeumliche Stabwerk in SI.
> Paket [[opencivil.stabwerk3d]] · [Quelltext](../../opencivil/stabwerk3d/modell.py)

## VERANTWORTUNG

Die Eingabe des Rechenkerns, ohne Oberflaeche und ohne Projekt: Knoten,
Staebe, Lager, Lasten, Lastfaelle und Kombinationen, alles in N, m und rad.
Gerechnet wird in [[opencivil.stabwerk.system|system]]. Was nicht vom Raum
abhaengt, kommt aus der Ebene ([[opencivil.stabwerk.modell]]): wie eine
Richtung gehalten ist ([[opencivil.stabwerk.modell#Halt|Halt]]), die Arten der Lasten, Lastfall und
Kombination.


## DIE ACHSEN DES SYSTEMS

`x` und `y` waagrecht, `z` nach oben, ein Rechtssystem; Drehungen im
Rechtssinn um ihre Achse. Verschiebungen und Lagerkraefte sind positiv
entlang dieser Achsen. Liegt ein Rahmen in der x-z-Ebene, sieht man ihn wie
im 2D-Balkensystem: x nach rechts, z nach oben -- `y` zeigt dann vom
Betrachter weg, und eine Drehung im Gegenuhrzeigersinn ist eine um `-y`.


## LASTEN MIT RICHTUNG

Eine Kraftlast ist positiv in ihrer Richtung ([[opencivil.stabwerk3d.modell#Richtung|Richtung]]):
«senkrecht» nach unten, wie die Schwerkraft, in x, y oder z des Systems,
oder laengs, quer y oder quer z in den Achsen des Stabs
([[opencivil.stabwerk3d.stab|stab]]). Eine Momentlast dreht im Rechtssinn um
ihre Richtung -- laengs ist sie ein Torsionsmoment. Lasten in Richtungen des
Systems gelten je Meter Stab -- oder, mit `projiziert`, je Meter seiner
Projektion auf die Ebene senkrecht zur Richtung, wie Schnee auf einem
geneigten Dach.

## Inhalt

### Richtung

```python
class Richtung(Wahl)
```

Wohin eine Kraftlast zeigt -- oder um welche Achse eine Momentlast dreht --, wenn ihr Wert positiv ist.

- `SENKRECHT = 'senkrecht'`
- `X = 'x'`
- `Y = 'y'`
- `Z = 'z'`
- `LAENGS = 'laengs'`
- `QUER_Y = 'quer_y'`
- `QUER_Z = 'quer_z'`

#### Richtung.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Richtung.stabachse

```python
@property
def stabachse(self) -> Optional[str]
```

In welcher Achse des Stabs sie liegt -- keine, wenn sie im System liegt.

#### Richtung.im_system

```python
@property
def im_system(self) -> bool
```

Ob sie in den Achsen des Systems liegt -- und nicht in denen des Stabs.

#### Richtung.systemvektor

```python
@property
def systemvektor(self) -> Optional[Vektor]
```

Die Richtung, wenn sie im System liegt.

#### Richtung.vektor

```python
def vektor(self, achsen: Sequence[Vektor]) -> Vektor
```

Die Richtung als Einheitsvektor im System, fuer einen Stab mit den Achsen `(x, y, z)`.

#### Richtung.projektion

```python
def projektion(self, achsen: Sequence[Vektor]) -> float
```

Laenge der Projektion je Meter Stab, auf die Ebene senkrecht zu dieser
Richtung -- in der Ebene `|cos α|` fuer senkrecht, `|sin α|` fuer
waagrecht.

### Knoten

```python
@dataclass(frozen=True)
class Knoten
```

- `name: str`
- `x: float`
- `y: float`
- `z: float`

### Lager

```python
@dataclass(frozen=True)
class Lager
```

Ein Lager an einem Knoten -- je Richtung des Systems frei, fest oder Feder.

- `name: str`
- `knoten: str`
- `x: Halt = FREI` – In N/m, wenn Feder.
- `y: Halt = FREI`
- `z: Halt = FREI`
- `phi_x: Halt = FREI` – In Nm/rad, wenn Feder.
- `phi_y: Halt = FREI`
- `phi_z: Halt = FREI`

#### Lager.verschiebungen

```python
@property
def verschiebungen(self) -> Tuple[Halt, Halt, Halt]
```

#### Lager.drehungen

```python
@property
def drehungen(self) -> Tuple[Halt, Halt, Halt]
```

### Stab

```python
@dataclass(frozen=True)
class Stab
```

Eine Linie des Systems -- ein Stab, der traegt, oder nur ein Linienlager.

`drehung` ist der Drehwinkel β seiner Achsen um x, in rad. Die
Linienlager halten laengs und quer in y und z des Stabs: frei, fest oder
eine Bettung in N/m². Ein Gelenk loest am Stabende alle drei Momente,
wie ein Kugelgelenk; mit Gelenken an beiden Enden traegt der Stab keine
Torsion ([[opencivil.stabwerk.system|system]]).

- `name: str`
- `a: str`
- `b: str`
- `EA: float = 0.0` – N.
- `EI_y: float = 0.0` – Nm² -- Biegung um y, in der x-z-Ebene des Stabs.
- `EI_z: float = 0.0` – Nm² -- Biegung um z, in der x-y-Ebene des Stabs.
- `GI_T: float = 0.0` – Nm² -- Torsion.
- `drehung: float = 0.0`
- `traegt: bool = True`
- `gelenk_a: bool = False`
- `gelenk_b: bool = False`
- `laengs: Halt = FREI`
- `quer_y: Halt = FREI`
- `quer_z: Halt = FREI`

### Stablast

```python
@dataclass(frozen=True)
class Stablast
```

Eine Last auf einem Stab. Stellen in m ab seinem Anfang; `bis = None`
heisst bis zum Ende. Einzellast und Einzelmoment stehen bei `von`.
Werte in N/m, N, Nm oder Nm/m, positiv in ihrer Richtung.

- `stab: str`
- `art: Lastart`
- `wert_a: float`
- `wert_b: Optional[float] = None` – Am Ende des belasteten Bereichs -- `None`: wie am Anfang.
- `richtung: Richtung = Richtung.SENKRECHT`
- `von: float = 0.0`
- `bis: Optional[float] = None`
- `projiziert: bool = False`

#### Stablast.mal

```python
def mal(self, faktor: float) -> 'Stablast'
```

### Knotenlast

```python
@dataclass(frozen=True)
class Knotenlast
```

Eine Last an einem Knoten, in den Achsen des Systems: N und Nm.

- `knoten: str`
- `F: Vektor = (0.0, 0.0, 0.0)`
- `M: Vektor = (0.0, 0.0, 0.0)`

#### Knotenlast.mal

```python
def mal(self, faktor: float) -> 'Knotenlast'
```

### System

```python
@dataclass
class System
```

- `knoten: List[Knoten] = field(default_factory=list)`
- `staebe: List[Stab] = field(default_factory=list)`
- `lager: List[Lager] = field(default_factory=list)`
- `lastfaelle: List[Lastfall] = field(default_factory=list)`
- `kombinationen: List[Kombination] = field(default_factory=list)`


## Braucht

- [[opencivil.core.wahl]]
- [[opencivil.stabwerk.modell]]
- [[opencivil.stabwerk3d.raum]]

## Gebraucht von

- [[opencivil.projekt.aufbau.balkensystem3d]]
- [[opencivil.projekt.balkensystem3d]]
- [[opencivil.stabwerk.art]]
- [[opencivil.stabwerk.system]]
- [[opencivil.stabwerk3d.herleitung]]
- [[opencivil.stabwerk3d.rechnung]]
- [[opencivil.stabwerk3d.stab]]
