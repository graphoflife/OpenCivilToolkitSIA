---
erzeugt: 3b22d6ec0087
art: modul
tags: [modul]
---
> [!abstract] opencivil/stabwerk/modell.py
> was gerechnet wird: das ebene Stabwerk in SI.
> Paket [[opencivil.stabwerk]] · [Quelltext](../../opencivil/stabwerk/modell.py)

## VERANTWORTUNG

Die Eingabe des Rechenkerns, ohne Oberflaeche und ohne Projekt: Knoten,
Staebe, Lager, Lasten, Lastfaelle und Kombinationen, alles in N, m und rad.
Aus der Beschreibung eines Balkensystems baut sie
[[opencivil.projekt|opencivil.projekt.balkensystem]]; gerechnet wird in
[[opencivil.stabwerk.system|system]].


## DIE ACHSEN DES SYSTEMS

`x` nach rechts, `z` nach oben, Drehungen im Gegenuhrzeigersinn.
Verschiebungen und Lagerkraefte sind positiv entlang dieser Achsen; eine
Lagerkraft nach oben ist positiv.


## LASTEN MIT RICHTUNG

Eine Kraftlast traegt ihre Richtung und ist positiv in Pfeilrichtung
([[opencivil.stabwerk.modell#Lastrichtung|Lastrichtung]]): «senkrecht» nach unten, wie die Schwerkraft,
«waagrecht» nach rechts, «quer» zur gestrichelten Faser des Stabs, «laengs»
vom Anfang zum Ende. Momentlasten drehen im Gegenuhrzeigersinn. Senkrechte und
waagrechte Lasten gelten je Meter Stab -- oder, mit `projiziert`, je Meter
der Projektion, wie Schnee auf einem geneigten Dach.


## HALT

Ein Lager haelt je Richtung fest ([[opencivil.stabwerk.modell#Konstanten|FEST]]), federnd (eine Zahl) oder
gar nicht (`None`) -- dieselbe Wahl fuer die Linienlager eines Stabs, quer
und laengs. Eine Feder in N/m bzw. Nm/rad, eine Bettung in N/m je m Stab.

## Inhalt

### Lastrichtung

```python
class Lastrichtung(str, Enum)
```

Wohin eine Kraftlast zeigt, wenn ihr Wert positiv ist.

- `SENKRECHT = 'senkrecht'`
- `WAAGRECHT = 'waagrecht'`
- `QUER = 'quer'`
- `LAENGS = 'laengs'`

#### Lastrichtung.im_system

```python
@property
def im_system(self) -> bool
```

Ob sie in den Achsen des Systems liegt -- und nicht in denen des Stabs.

#### Lastrichtung.vektor

```python
def vektor(self, c: float, s: float) -> Tuple[float, float]
```

Die Richtung als Einheitsvektor `(x, z)` im System, fuer einen Stab
mit `(c, s) = (cos α, sin α)`. Quer heisst zur gestrichelten Faser:
`(s, -c)`, die rechte Seite des Stabs.

#### Lastrichtung.projektion

```python
def projektion(self, c: float, s: float) -> float
```

Laenge der Projektion je Meter Stab -- senkrecht auf die Waagrechte, waagrecht auf die Senkrechte.

### Lastart

```python
class Lastart(str, Enum)
```

Was fuer eine Last auf einem Stab liegt.

- `LINIENLAST = 'linienlast'` – Kraft je Laenge, von `wert_a` nach `wert_b` linear -- gleichmaessig oder als Dreieck.
- `EINZELLAST = 'einzellast'`
- `MOMENT = 'moment'` – Ein Einzelmoment, im Gegenuhrzeigersinn.
- `LINIENMOMENT = 'linienmoment'` – Moment je Laenge, linear.

#### Lastart.verteilt

```python
@property
def verteilt(self) -> bool
```

#### Lastart.kraft

```python
@property
def kraft(self) -> bool
```

### Knoten

```python
@dataclass(frozen=True)
class Knoten
```

- `name: str`
- `x: float`
- `z: float`

### Lager

```python
@dataclass(frozen=True)
class Lager
```

Ein Lager an einem Knoten -- je Richtung frei, fest oder Feder.

- `name: str`
- `knoten: str`
- `x: Halt = None` – In N/m, wenn Feder.
- `z: Halt = None`
- `phi: Halt = None` – In Nm/rad, wenn Feder.

### Stab

```python
@dataclass(frozen=True)
class Stab
```

Eine Linie des Systems -- ein Stab, der traegt, oder nur ein Linienlager.

`quer` und `laengs` sind die Linienlager: frei, fest oder eine
Bettung in N/m². Die Gelenke gelten fuer das Moment am Ende.

- `name: str`
- `a: str`
- `b: str`
- `EA: float = 0.0` – N.
- `EI: float = 0.0` – Nm².
- `traegt: bool = True`
- `gelenk_a: bool = False`
- `gelenk_b: bool = False`
- `quer: Halt = None`
- `laengs: Halt = None`

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
- `richtung: Lastrichtung = Lastrichtung.SENKRECHT`
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

Eine Last an einem Knoten, in den Achsen des Systems: N, N, Nm.

- `knoten: str`
- `Fx: float = 0.0`
- `Fz: float = 0.0`
- `M: float = 0.0`

#### Knotenlast.mal

```python
def mal(self, faktor: float) -> 'Knotenlast'
```

### Lastfall

```python
@dataclass
class Lastfall
```

- `name: str`
- `lasten: List[Last] = field(default_factory=list)`

### Kombination

```python
@dataclass
class Kombination
```

Eine Kombination: je Lastfall ein Beiwert. Was nicht dasteht, zaehlt null.

- `name: str`
- `faktoren: Dict[str, float] = field(default_factory=dict)`

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

#### System.kombiniert

```python
def kombiniert(self, kombination: Kombination) -> Lastfall
```

Eine Kombination als Lastfall: jede Last ihres Lastfalls mal dessen
Beiwert. So laeuft sie durch dieselbe Rechnung wie ein Lastfall --
und weil alles linear ist, ist das Ergebnis die Summe der mit ihren
Beiwerten gewichteten Lastfaelle.


## Konstanten

- `FEST = math.inf` – Fest gehalten -- eine Richtung ohne Verschiebung.

## Gebraucht von

- [[opencivil.stabwerk.system]]
