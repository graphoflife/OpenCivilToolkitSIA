---
erzeugt: 00ac49650ea6
art: modul
tags: [modul]
---
> [!abstract] opencivil/fachwerkmodell/modell.py
> die Scheibe eines Fachwerkmodells, in SI.
> Paket [[opencivil.fachwerkmodell]] · [Quelltext](../../opencivil/fachwerkmodell/modell.py)

## VERANTWORTUNG

Was ein Fachwerkmodell rechnet: Umrisse aus Ecken – Scheiben, die
zusammen das Material bilden, und Löcher, die es dort wegnehmen –, Lager
an Punkten, je fest in x, in y oder in beiden ([[opencivil.fachwerkmodell.modell#Halt|Halt]]), und
Punktlasten in jeder Richtung. Dazu die eine Regel, wo Material ist
([[opencivil.fachwerkmodell.modell#Modell.im_material|Modell.im_material]]): in einer Scheibe, ihr Rand zählt dazu, und
nicht im Innern eines Lochs – sein Rand ist noch Material. Ein Lager am
Rand eines Lochs steht also auf der Scheibe.


## KEIN MATERIAL, KEINE DICKE

Ohne Bemessung hängen Fachwerk und Kräfte nur von Form, Lagern und Lasten
ab (Plan vom 2026-11-27, Entscheid 11). Ein Satz Lasten je Modell; wer
einen zweiten Lastfall will, kopiert es.


## KOORDINATEN UND EINHEITEN

x nach rechts, y nach oben, in m; Kräfte in N, `F_x` nach rechts, `F_y`
nach oben. Die Beschreibung ([[opencivil.projekt.fachwerkmodell]]) gibt
die senkrechte Kraft nach unten positiv an, wie das Balkensystem;
umgerechnet wird beim Bauen.

## Inhalt

### Halt

```python
class Halt(Wahl)
```

In welchen Richtungen ein Lager die Scheibe hält.

- `XY = 'xy'`
- `X = 'x'`
- `Y = 'y'`

#### Halt.x

```python
@property
def x(self) -> bool
```

Ob es waagrecht hält.

#### Halt.y

```python
@property
def y(self) -> bool
```

Ob es senkrecht hält.

#### Halt.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Halt.erklaerung

```python
@property
def erklaerung(self) -> str
```

### Umriss

```python
@dataclass(frozen=True)
class Umriss
```

Eine Scheibe oder ein Loch: ihr Name und ihre Ecken in m.

- `name: str`
- `ecken: Tuple[Punkt, ...]`

### Lager

```python
@dataclass(frozen=True)
class Lager
```

Ein Lager an einem Punkt der Scheibe, in m.

- `name: str`
- `ort: Punkt`
- `halt: Halt`

### Last

```python
@dataclass(frozen=True)
class Last
```

Eine Punktlast in N: `F_x` nach rechts, `F_y` nach oben.

- `name: str`
- `ort: Punkt`
- `F_x: float`
- `F_y: float`

### Modell

```python
@dataclass(frozen=True)
class Modell
```

Die ganze Scheibe – jede Liste in der Folge der Beschreibung.

- `scheiben: Tuple[Umriss, ...] = ()`
- `loecher: Tuple[Umriss, ...] = ()`
- `lager: Tuple[Lager, ...] = ()`
- `lasten: Tuple[Last, ...] = ()`

#### Modell.in_scheibe

```python
def in_scheibe(self, p: Punkt) -> bool
```

Ob `p` in einer Scheibe liegt – auf ihrem Rand zählt.

#### Modell.loch_bei

```python
def loch_bei(self, p: Punkt) -> Optional[Umriss]
```

Das Loch, in dessen Innern `p` liegt – auf seinem Rand liegt es in keinem.

#### Modell.im_material

```python
def im_material(self, p: Punkt) -> bool
```

Ob bei `p` Material ist: in einer Scheibe und in keinem Loch.


## Braucht

- [[opencivil.core.wahl]]
- [[opencivil.decke.geometrie]]

## Gebraucht von

- [[opencivil.fachwerkmodell.form]]
- [[opencivil.fachwerkmodell.grundstruktur]]
- [[opencivil.fachwerkmodell.herleitung]]
- [[opencivil.fachwerkmodell.nachrechnung]]
- [[opencivil.fachwerkmodell.pruefen]]
- [[opencivil.fachwerkmodell.simp]]
- [[opencivil.fachwerkmodell.suche]]
- [[opencivil.fachwerkmodell.werk]]
- [[opencivil.projekt.aufbau.fachwerkmodell]]
- [[opencivil.projekt.fachwerkmodell]]
- [[opencivil.web.fachwerkdaten]]
