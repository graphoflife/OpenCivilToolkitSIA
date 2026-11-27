---
erzeugt: 3cbd8112fd1b
art: modul
tags: [modul]
---
> [!abstract] opencivil/decke/modell.py
> was gerechnet wird: die Decke in SI.
> Paket [[opencivil.decke]] · [Quelltext](../../opencivil/decke/modell.py)

## VERANTWORTUNG

Die Eingabe des Rechenkerns, ohne Oberfläche und ohne Projekt: Platten,
Lager, Stützen, Träger, Zonen der Lastaufteilung, Lasten,
Lastfälle und Kombinationen – alles in N, m und rad. Gerechnet wird nach
der Streifenmethode in [[opencivil.decke.rechnung|rechnung]], mit finiten
Elementen in [[opencivil.decke.fem|fem]] ([[opencivil.decke.modell#Verfahren|Verfahren]]).


## DIE ACHSEN

`x` nach rechts, `y` nach oben, im Grundriss. Lasten wirken nach unten
und sind dann positiv; eine Lagerkraft nach oben ist positiv.


## RICHTUNGEN DER LASTABTRAGUNG

Jede Platte trägt in zwei Richtungen, Winkel gegen die x-Achse – im
Rechteck `0` und `π/2`, in einer schiefen Platte etwa parallel zu ihren
Rändern. Die erste heisst «Richtung 1», die zweite «Richtung 2»; ein Anteil
gilt immer für Richtung 1, der Rest geht in Richtung 2. Grenzen zwei Platten
mit derselben Richtung aneinander, laufen ihre Streifen durch.

## Inhalt

### Verfahren

```python
class Verfahren(Wahl)
```

Wie die Decke gerechnet wird.

- `STREIFEN = 'streifen'` – Nach der Streifenmethode, für die Tragsicherheit – [[opencivil.decke.rechnung|rechnung]].
- `FEM = 'fem'` – Linear elastisch mit finiten Elementen – [[opencivil.decke.fem|fem]].

### Aufteilung

```python
class Aufteilung(Wahl)
```

Wie die Last ausserhalb der gezeichneten Zonen auf die beiden Richtungen geht.

- `AUTOMATISCH = 'automatisch'` – Nach dem Muster der randnahen Lastabtragung – siehe [[opencivil.decke.aufteilung|aufteilung]].
- `FEST = 'fest'` – Überall derselbe Anteil in Richtung 1.

### Platte

```python
@dataclass(frozen=True)
class Platte
```

- `name: str`
- `ecken: Tuple[Punkt, ...]`
- `h: float` – Dicke in m.
- `E: float` – Elastizitätsmodul in N/m² – er zählt nur, wo Platten verschieden steif sind.
- `wichte: float` – Gewicht je Volumen in N/m³, für das Eigengewicht.
- `richtungen: Tuple[float, float] = (0.0, math.pi / 2.0)` – Richtung 1 und 2 der Lastabtragung, rad gegen die x-Achse.
- `von_selbst: bool = False` – Ob die Platte ihre Richtungen selbst wählt, entlang ihrer Ränder ([[opencivil.decke.richtungen|richtungen]]) – dann gilt `richtungen` erst, wenn die Rechnung sie gewählt hat ([[opencivil.decke.rechnung#Ergebnis|decke]]).
- `nu: float = 0.0` – Die Querdehnungszahl – nur die FEM braucht sie; sie kommt wie E vom Beton.

### Linienlager

```python
@dataclass(frozen=True)
class Linienlager
```

Eine Wand oder ein Träger unter der Platte, als Linie. `vertikal`:
sie hält die Platte in der Höhe; `eingespannt`: sie hält ihre Drehung.
Beides zusammen ist eine Einspannung, nur `eingespannt` eine
Symmetrieachse.

- `name: str`
- `a: Punkt`
- `b: Punkt`
- `vertikal: bool = True`
- `eingespannt: bool = False`

### Stuetze

```python
@dataclass(frozen=True)
class Stuetze
```

Eine Stütze, `bx × by` gross. Die Streifen und Träger über ihr
liegen auf dem Stützenbereich `lx × ly` mit gleichmässiger Pressung –
ohne Angabe so breit wie die Träger über ihr, mindestens so gross wie
die Stütze ([[opencivil.decke.streifen#stuetzenbereich|stuetzenbereich]]).

- `name: str`
- `ort: Punkt`
- `bx: float`
- `by: float`
- `lx: Optional[float] = None`
- `ly: Optional[float] = None`

### Traeger

```python
@dataclass(frozen=True)
class Traeger
```

Ein Träger – ein Unterzug oder ein Überzug –, in der Streifenmethode
ein Streifen der Breite `breite` von `a` nach `b`, so dick wie
die Platte. Streifen quer dazu liegen auf ihm,
ein Träger mit kleinerer `stufe` ebenso; er selbst liegt auf Lagern,
Stützen und Trägern höherer Stufe. In der FEM ein Balken in der Platte
([[opencivil.decke.fem.element|element]]), so steif wie das Rechteck
`breite × (h + hoehe)` ohne den Teil der Platte.

- `name: str`
- `a: Punkt`
- `b: Punkt`
- `breite: float`
- `stufe: float = 1` – Ganz, ab 1 – nur die Bänder liegen darunter ([[opencivil.decke.baender|STUFE_RAND]]).
- `von_selbst: bool = False` – Ein Band, das die Rechnung selbst legt ([[opencivil.decke.baender|baender]]) – kein Eintrag im Projekt.
- `hoehe: float = 0.0` – So weit reicht er über oder unter die Platte, in m – null: er steckt in ihr. Sein Steg wiegt mit, wenn ein Lastfall das Eigengewicht hat ([[opencivil.decke.lasten#stege|stege]]).

### Zone

```python
@dataclass(frozen=True)
class Zone
```

Ein Gebiet mit eigener Lastaufteilung: `anteil` geht in Richtung 1, der Rest in Richtung 2.

- `name: str`
- `ecken: Tuple[Punkt, ...]`
- `anteil: float`

### Flaechenlast

```python
@dataclass(frozen=True)
class Flaechenlast
```

Eine gleichmässige Flächenlast in N/m², nach unten positiv – auf dem
gezeichneten Vieleck `ecken` oder auf der ganzen Platte `platte`.

- `name: str`
- `wert: float`
- `ecken: Tuple[Punkt, ...] = ()`
- `platte: str = ''`

#### Flaechenlast.mal

```python
def mal(self, faktor: float) -> 'Flaechenlast'
```

### Linienlast

```python
@dataclass(frozen=True)
class Linienlast
```

Eine gleichmässige Linienlast in N/m von `a` nach `b`, nach unten positiv.

- `name: str`
- `a: Punkt`
- `b: Punkt`
- `wert: float`

#### Linienlast.mal

```python
def mal(self, faktor: float) -> 'Linienlast'
```

### Punktlast

```python
@dataclass(frozen=True)
class Punktlast
```

Eine Einzellast in N, nach unten positiv. Die Streifen tragen sie als
gleichmässige Last auf der Fläche `lx × ly` um `ort`; was das an
Biegewiderstand kostet, sagt das Lastverteilelement
([[opencivil.decke.feld|feld]]).

- `name: str`
- `ort: Punkt`
- `wert: float`
- `lx: float = VERTEILBREITE`
- `ly: float = VERTEILBREITE`

#### Punktlast.mal

```python
def mal(self, faktor: float) -> 'Punktlast'
```

### Lastfall

```python
@dataclass
class Lastfall
```

- `name: str`
- `lasten: List[Last] = field(default_factory=list)`
- `eigengewicht: bool = False` – Ob das Eigengewicht der Platten dazugehört.

### Kombination

```python
@dataclass
class Kombination
```

Je Lastfall ein Beiwert. Was nicht dasteht, zählt null.

- `name: str`
- `faktoren: Dict[str, float] = field(default_factory=dict)`

### Decke

```python
@dataclass
class Decke
```

- `platten: List[Platte] = field(default_factory=list)`
- `linienlager: List[Linienlager] = field(default_factory=list)`
- `stuetzen: List[Stuetze] = field(default_factory=list)`
- `traeger: List[Traeger] = field(default_factory=list)`
- `zonen: List[Zone] = field(default_factory=list)`
- `lastfaelle: List[Lastfall] = field(default_factory=list)`
- `kombinationen: List[Kombination] = field(default_factory=list)`
- `streifenbreite: float = STREIFENBREITE`
- `aufteilung: Aufteilung = Aufteilung.AUTOMATISCH`
- `anteil: float = 0.5` – Bei fester Aufteilung: der Anteil in Richtung 1.
- `bandbreite: float = BANDBREITE` – Nur bei automatischer Aufteilung: dann legt die Rechnung Bänder so breit ([[opencivil.decke.baender|baender]]).
- `verfahren: Verfahren = Verfahren.STREIFEN`
- `netzweite: float = NETZWEITE` – Nur in der FEM: so weit liegen die Knoten ihres Netzes höchstens auseinander ([[opencivil.decke.fem.netz|netz]]).


## Konstanten

- `STREIFENBREITE = 0.25` – Die Breite eines Streifens höchstens, in m – ein Vorschlag.
- `VERTEILBREITE = 1.0` – Die Seiten der Fläche, über die eine Einzellast verteilt wird, in m – ein Vorschlag.
- `BANDBREITE = 1.0` – Wie breit die Bänder sind, die die Rechnung selbst legt, in m – ein Vorschlag.
- `NETZWEITE = 0.5` – Wie weit die Knoten des Netzes der FEM höchstens auseinander liegen, in m – ein Vorschlag.

## Braucht

- [[opencivil.core.wahl]]
- [[opencivil.decke.geometrie]]

## Gebraucht von

- [[opencivil.decke.aufteilung]]
- [[opencivil.decke.baender]]
- [[opencivil.decke.feld]]
- [[opencivil.decke.fem.auswertung]]
- [[opencivil.decke.fem.belastung]]
- [[opencivil.decke.fem.herleitung]]
- [[opencivil.decke.fem.netz]]
- [[opencivil.decke.fem.rechnung]]
- [[opencivil.decke.fem.system]]
- [[opencivil.decke.herleitung]]
- [[opencivil.decke.lasten]]
- [[opencivil.decke.rechnung]]
- [[opencivil.decke.richtungen]]
- [[opencivil.decke.schnitt]]
- [[opencivil.decke.streifen]]
- [[opencivil.decke.werk]]
- [[opencivil.projekt.aufbau.decke]]
- [[opencivil.projekt.decke]]
- [[opencivil.web.api]]
- [[opencivil.web.deckendaten]]
