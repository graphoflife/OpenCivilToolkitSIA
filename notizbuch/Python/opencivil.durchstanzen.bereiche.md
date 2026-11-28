---
erzeugt: b7c647bb2a4a
art: modul
tags: [modul]
---
> [!abstract] opencivil/durchstanzen/bereiche.py
> Bereiche der Platte mit eigener Dicke.
> Paket [[opencivil.durchstanzen]] · [Quelltext](../../opencivil/durchstanzen/bereiche.py)

## VERANTWORTUNG

Ein [[opencivil.durchstanzen.bereiche#Plattenbereich|Plattenbereich]] – sein Umriss, seine Dicke und auf welcher
Seite der Platte seine Stufe liegt – und was die Stelle von allen zusammen
wissen muss ([[opencivil.durchstanzen.bereiche#Dicken|Dicken]]): welche Bereiche die Stütze umschliessen, was
jenseits einer Stufe liegt, welche statische Höhe wo gilt. Die Platte
behält ihre Dicke h; ein Bereich gilt in seinem Umriss statt ihr, dicker
oder dünner. Bereiche dürfen ineinander liegen – es gilt der innerste –,
aber sich nicht teilweise überdecken und die Stütze nicht schneiden; das
prüft der Aufbau ([[opencivil.projekt.aufbau.durchstanzen]]).


## DIE SEITE DER STUFE (SIA 262:2025, 4.3.6.2.7, Figur 24)

Um die Stütze liegt die Druckseite der Platte auf der Seite der Stütze –
bei der Decke unten, bei der Bodenplatte oben. Ein Bereich ist dicker oder
dünner auf einer der beiden Seiten ([[opencivil.durchstanzen.bereiche#Seite|Seite]]):

- zur Stütze hin – auf der Druckseite, wie ein Stützenkopf unter einer
  Decke (Figur 24a): die Zugseite läuft eben durch;
- Gegenseite – auf der Zugseite, wie eine Vertiefung unter einer
  Bodenplatte (Figur 24c): die Zugbewehrung folgt der Oberfläche.


## DIE STATISCHE HÖHE

Die Zugbewehrung liegt überall c_nom unter der Oberfläche der Zugseite: in
einem Bereich ist d um so viel grösser oder kleiner als in der Platte, wie
er dicker oder dünner ist, d_B = d + (h_B − h). Welche Seite sich dabei
verschiebt, zählt erst für einen Riss, der über eine Stufe läuft
([[opencivil.durchstanzen.bereiche#Dicken.wirksam|Dicken.wirksam]]): er beginnt auf der Druckseite des einen Bereichs
und endet an der Zugbewehrung eines anderen. Je Bereich steht darum, um wie
viel seine Druckseite und seine Zugseite gegenüber der Platte versetzt sind
([[opencivil.durchstanzen.bereiche#Versatz|Versatz]]) – ineinander liegende Bereiche je gegenüber dem, in dem
sie liegen.


## EINHEITEN

m.

## Inhalt

### Seite

```python
class Seite(Wahl)
```

Auf welcher Seite der Platte die Stufe eines Bereichs liegt – siehe Dateikopf.

- `STUETZE = 'stuetze'`
- `GEGENSEITE = 'gegenseite'`

#### Seite.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Seite.figur

```python
@property
def figur(self) -> str
```

Die Figur der Norm, die die Stufe zeigt.

#### Seite.titel

```python
@property
def titel(self) -> str
```

Was die Stellung heisst, in einem Satz – für den Schalter.

### Plattenbereich

```python
@dataclass(frozen=True)
class Plattenbereich
```

Ein Bereich mit eigener Dicke: Name, Ecken in m, Dicke und die Seite der Stufe.

- `name: str` – Wie Zeichnung und Herleitung ihn nennen – «B1».
- `ecken: Tuple[Punkt, ...]`
- `h: float`
- `seite: Seite`

#### Plattenbereich.titel

```python
@property
def titel(self) -> str
```

«Bereich B1» – so steht er in Sätzen.

#### Plattenbereich.huelle

```python
@property
def huelle(self) -> Tuple[Punkt, ...]
```

Die konvexe Hülle gegen den Uhrzeigersinn – um sie läuft ein Schnitt (Figur 22c).

#### Plattenbereich.enthaelt

```python
def enthaelt(self, punkte: Sequence[Punkt]) -> bool
```

Ob alle `punkte` in ihm liegen – auf seinem Rand zählt als darin.

### Versatz

```python
@dataclass(frozen=True)
class Versatz
```

Um wie viel die Druckseite und die Zugseite eines Bereichs gegenüber der
Platte nach aussen versetzt sind, in m – negativ, wo er dünner ist.
Die Summe ist, um wie viel er dicker ist als die Platte.

- `druck: float = 0.0`
- `zug: float = 0.0`

### Dicken

```python
@dataclass(frozen=True)
class Dicken
```

Die Platte und ihre Bereiche: wo welche Dicke gilt – siehe Dateikopf.
`h` und `d` sind die der Platte, ausserhalb aller Bereiche.

- `h: float`
- `d: float`
- `bereiche: Tuple[Plattenbereich, ...] = ()`
- `eltern: Dict[str, Optional[Plattenbereich]] = field(init=False, repr=False, compare=False)` – Je Bereich der kleinste, der ihn ganz enthält; `None`: die Platte.

#### Dicken.aussen

```python
def aussen(self, bereich: Plattenbereich) -> Optional[Plattenbereich]
```

Was jenseits seiner Stufe liegt: der Bereich, in dem er liegt – `None`: die Platte.

#### Dicken.h_von

```python
def h_von(self, bereich: Optional[Plattenbereich]) -> float
```

#### Dicken.d_von

```python
def d_von(self, bereich: Optional[Plattenbereich]) -> float
```

Die statische Höhe im Bereich: d der Platte, verschoben um den Unterschied der Dicke.

#### Dicken.versatz

```python
def versatz(self, bereich: Optional[Plattenbereich]) -> Versatz
```

Wie weit Druck- und Zugseite des Bereichs gegenüber der Platte versetzt sind.

#### Dicken.dicker

```python
def dicker(self, bereich: Plattenbereich) -> bool
```

Ob der Bereich dicker ist als das, was jenseits seiner Stufe liegt.

#### Dicken.um

```python
def um(self, umriss: Sequence[Punkt]) -> Tuple[Plattenbereich, ...]
```

Die Bereiche, die den Umriss ganz umschliessen, der innerste zuerst.

#### Dicken.wirksam

```python
def wirksam(self, start: Optional[Plattenbereich], reicht: Callable[[float, Plattenbereich], bool]) -> Optional[Plattenbereich]
```

Wo die Zugbewehrung liegt, an der ein Riss endet, der auf der
Druckseite von `start` beginnt: in `start` selbst – ausser
`start` ist auf der Gegenseite dicker und reicht nicht weit genug,
`reicht(d_v, bereich)` ist falsch. Dann endet der Riss jenseits
seiner Stufe, wo die Zugbewehrung höher liegt, und es gilt, was dort
liegt. Die Druckseite ist dabei dieselbe: eine Stufe auf der
Gegenseite versetzt nur die Zugseite. Nach Vorgabe, nicht
nachgeschlagen ([[opencivil.durchstanzen.stufen|.stufen]]).


## Konstanten

- `PLATTE = Versatz()`

## Braucht

- [[opencivil.core.wahl]]
- [[opencivil.durchstanzen.schnitt]]
- [[opencivil.querschnitt.geometrie]]

## Gebraucht von

- [[opencivil.durchstanzen.herleitung]]
- [[opencivil.durchstanzen.mit_bewehrung]]
- [[opencivil.durchstanzen.nachweis]]
- [[opencivil.durchstanzen.stelle]]
- [[opencivil.durchstanzen.stufen]]
- [[opencivil.durchstanzen.weg]]
- [[opencivil.projekt.aufbau.durchstanzen]]
- [[opencivil.projekt.durchstanzen]]
- [[opencivil.web.durchstanzdaten]]
