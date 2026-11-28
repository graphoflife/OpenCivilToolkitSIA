---
erzeugt: 34af97ff4c49
art: modul
tags: [modul]
---
> [!abstract] opencivil/mauerwerk/modell.py
> eine Mauerwerkswand in der Ansicht, in SI.
> Paket [[opencivil.mauerwerk]] · [Quelltext](../../opencivil/mauerwerk/modell.py)

## VERANTWORTUNG

Was eine Wand rechnet: ihr Umriss in der Ansicht, ihre Öffnungen mit
Stürzen, wie sie über die Dicke gemauert ist und ob die Stossfugen
vollfugig vermauert sind, und wie ihre Ränder gehalten sind. Dazu die eine
Regel, wo die Pfeiler stehen ([[opencivil.mauerwerk.modell#pfeiler|pfeiler]]). Ihre Dicke ist eine
Vorgabe der Rechnung ([[opencivil.mauerwerk.werk#Konstanten|VORGABEN]]).


## KOORDINATEN UND EINHEITEN

In der Ansicht x nach rechts, y nach oben, in m – wie im Zeichenfenster.
Die Norm nennt die Richtungen anders (SIA 266:2015, Figur 1): ihr x steht
senkrecht zu den Lagerfugen, also lotrecht, ihr y längs der Wand, ihr z
quer zu ihr. Die Herleitung spricht mit den Zeichen der Norm: N_x, f_xd.


## RECHTECKE

Eine Wand und eine Öffnung sind Rechtecke mit waagrechten und senkrechten
Seiten ([[opencivil.mauerwerk.modell#rechteck|rechteck]]) – gezeichnet als Umriss aus vier Ecken, wie die
Werkzeuge «Wand» und «Öffnung» sie setzen. Eine schräge Wandkrone, etwa die eines
Giebels, rechnet das Werkzeug noch nicht.


## DIE PFEILER

Zwischen zwei Öffnungen und zwischen einer Öffnung und dem Ende der Wand
steht ein Pfeiler, so breit wie der Abstand ([[opencivil.mauerwerk.modell#pfeiler|pfeiler]]). Öffnungen,
die sich in der Breite überdecken – ein Fenster über einer Türe –, bilden
zusammen eine Lücke. Wo keine Öffnung ist, ist die ganze Wand ein Pfeiler.


## DIE LASTEN

Lotrecht, je Lastfall ([[opencivil.mauerwerk.modell#Lastfall|Lastfall]]): waagrechte Linienlasten und
Punktlasten in der Ansicht, nach unten positiv, mit ihrer Ausmitte quer zur
Wand – positiv zur Seite, von der aus man die Ansicht sieht. Wie sie zu
den Pfeilern kommen, sagt [[opencivil.mauerwerk.lasten|lasten]].

## Inhalt

### Mauerung

```python
class Mauerung(Wahl)
```

Wie die Wand über ihre Dicke gemauert ist – die Begriffe nach SIA 266:2015, 1.1.

- `EINSTEIN = 'einstein'`
- `VERBAND = 'verband'`

#### Mauerung.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Mauerung.erklaerung

```python
@property
def erklaerung(self) -> str
```

### Stossfugen

```python
class Stossfugen(Wahl)
```

Wie die Stossfugen vermauert sind – die Begriffe nach SIA 266:2015, 1.1.

- `NICHT_VOLLFUGIG = 'nicht_vollfugig'`
- `VOLLFUGIG = 'vollfugig'`

#### Stossfugen.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Stossfugen.erklaerung

```python
@property
def erklaerung(self) -> str
```

### Halterung

```python
class Halterung(Wahl)
```

Wie Kopf oder Fuss der Wand gehalten sind.

- `GELENKIG = 'gelenkig'`
- `EINGESPANNT = 'eingespannt'`

#### Halterung.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Halterung.erklaerung

```python
@property
def erklaerung(self) -> str
```

### Seitenrand

```python
class Seitenrand(Wahl)
```

Wie ein senkrechter Rand der Wand gehalten ist – links oder rechts.

- `FREI = 'frei'`
- `GEHALTEN = 'gehalten'`

#### Seitenrand.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Seitenrand.erklaerung

```python
@property
def erklaerung(self) -> str
```

### Sturzart

```python
class Sturzart(Wahl)
```

Was über einer Öffnung trägt.

- `BETON = 'beton'`
- `VORFABRIZIERT = 'vorfabriziert'`

#### Sturzart.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Sturzart.erklaerung

```python
@property
def erklaerung(self) -> str
```

### Rechteck

```python
@dataclass(frozen=True)
class Rechteck
```

Ein Rechteck mit waagrechten und senkrechten Seiten, in m.

- `x0: float`
- `y0: float`
- `x1: float`
- `y1: float`

#### Rechteck.breite

```python
@property
def breite(self) -> float
```

#### Rechteck.hoehe

```python
@property
def hoehe(self) -> float
```

#### Rechteck.enthaelt

```python
def enthaelt(self, r: 'Rechteck') -> bool
```

Ob `r` ganz darin liegt – auf dem Rand zählt.

#### Rechteck.ueberlappt

```python
def ueberlappt(self, r: 'Rechteck') -> bool
```

Ob beide Fläche gemeinsam haben – berühren sie sich nur am Rand, nicht.

### rechteck

```python
def rechteck(ecken: Sequence[Punkt]) -> Optional[Rechteck]
```

Das Rechteck mit diesen vier Ecken, wenn sie eines mit waagrechten und
senkrechten Seiten bilden – sonst `None`.

### Umriss

```python
@dataclass(frozen=True)
class Umriss
```

Ein gezeichneter Umriss: sein Name und seine Ecken in m.

- `name: str`
- `ecken: Tuple[Punkt, ...]`

#### Umriss.rechteck

```python
@property
def rechteck(self) -> Optional[Rechteck]
```

### Oeffnung

```python
@dataclass(frozen=True)
class Oeffnung(Umriss)
```

Eine Türe oder ein Fenster, mit dem Sturz darüber – `h_St` und `a` in m.

- `sturz: Sturzart = Sturzart.BETON`
- `h_St: float = 0.2` – Wie hoch der Sturz ist.
- `a: float = 0.15` – Wie weit er auf jeder Seite aufliegt.

#### Oeffnung.sturzflaeche

```python
def sturzflaeche(self) -> Optional[Rechteck]
```

Der Sturz in der Ansicht – `None`, wenn die Öffnung kein Rechteck ist.

### Pfeiler

```python
@dataclass(frozen=True)
class Pfeiler
```

Ein Pfeiler zwischen Öffnungen oder am Ende der Wand, in m.

- `name: str`
- `x0: float`
- `x1: float`
- `y0: float`
- `y1: float`
- `links: Tuple[str, ...]` – Die Öffnungen gleich links – leer am linken Ende der Wand.
- `rechts: Tuple[str, ...]` – Die Öffnungen gleich rechts – leer am rechten Ende.

#### Pfeiler.b

```python
@property
def b(self) -> float
```

Die Pfeilerbreite.

### Wandlast

```python
@dataclass(frozen=True)
class Wandlast
```

Eine lotrechte Last, nach unten positiv: `Q` in N, gleichmässig von
`x0` bis `x1` in der Höhe `y` – eine Punktlast mit `x0 = x1`.
`e` ist ihre Ausmitte in m (Dateikopf). `name` nennt sie in einer
Meldung.

- `name: str`
- `x0: float`
- `x1: float`
- `y: float`
- `Q: float`
- `e: float = 0.0`

### Lastfall

```python
@dataclass(frozen=True)
class Lastfall
```

Ein Lastfall der Wand: seine Lasten, und ob er ihr Eigengewicht bekommt.

- `name: str`
- `lasten: Tuple[Wandlast, ...] = ()`
- `eigengewicht: bool = False`

### Kombination

```python
@dataclass(frozen=True)
class Kombination
```

Je Lastfall, nach seinem Namen, ein Beiwert. Was nicht dasteht, zählt null.

- `name: str`
- `faktoren: Mapping[str, float] = field(default_factory=dict)`

### Wand

```python
@dataclass(frozen=True)
class Wand
```

Die ganze Wand – jede Liste in der Folge der Beschreibung.

- `umrisse: Tuple[Umriss, ...] = ()`
- `oeffnungen: Tuple[Oeffnung, ...] = ()`
- `mauerung: Mauerung = Mauerung.EINSTEIN`
- `stossfugen: Stossfugen = Stossfugen.NICHT_VOLLFUGIG`
- `kopf: Halterung = Halterung.GELENKIG`
- `fuss: Halterung = Halterung.GELENKIG`
- `links: Seitenrand = Seitenrand.FREI`
- `rechts: Seitenrand = Seitenrand.FREI`
- `lastfaelle: Tuple[Lastfall, ...] = ()`
- `kombinationen: Tuple[Kombination, ...] = ()`

#### Wand.verband

```python
@property
def verband(self) -> bool
```

#### Wand.vollfugig

```python
@property
def vollfugig(self) -> bool
```

#### Wand.flaeche

```python
@property
def flaeche(self) -> Optional[Rechteck]
```

Die Wand als Rechteck: `None` ohne genau einen rechteckigen Umriss.

### pfeiler

```python
def pfeiler(wand: Rechteck, oeffnungen: Sequence[Oeffnung]) -> List[Pfeiler]
```

Die Pfeiler der Wand, von links nach rechts – P1, P2 … (Dateikopf).
Gezählt werden nur Öffnungen, die Rechtecke sind.


## Konstanten

- `TOLERANZ = 1e-06` – Unter dieser Länge in m sind zwei Koordinaten gleich.

## Braucht

- [[opencivil.core.wahl]]
- [[opencivil.decke.geometrie]]

## Gebraucht von

- [[opencivil.mauerwerk.herleitung]]
- [[opencivil.mauerwerk.lasten]]
- [[opencivil.mauerwerk.nachweise]]
- [[opencivil.mauerwerk.pruefen]]
- [[opencivil.mauerwerk.werk]]
- [[opencivil.projekt.aufbau.mauerwerk]]
- [[opencivil.projekt.mauerwerk]]
- [[opencivil.web.mauerwerkdaten]]
