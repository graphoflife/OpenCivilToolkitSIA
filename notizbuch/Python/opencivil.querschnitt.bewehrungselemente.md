---
erzeugt: d3feee06e3f4
art: modul
tags: [modul]
---
> [!abstract] opencivil/querschnitt/bewehrungselemente.py
> die gezeichnete Bewehrung, je nach Art.
> Paket [[opencivil.querschnitt]] · [Quelltext](../../opencivil/querschnitt/bewehrungselemente.py)

## VERANTWORTUNG

Ein Bewehrungselement der Querschnittsanalyse ist ein Einzelstab
([[opencivil.querschnitt.bewehrungselemente#Einzelstab|Einzelstab]]), eine Reihe gleicher Staebe auf einer Linie
([[opencivil.querschnitt.bewehrungselemente#Stabreihe|Stabreihe]]) oder eine verschmierte Linie
([[opencivil.querschnitt.bewehrungselemente#VerschmierteLinie|VerschmierteLinie]]). Was je Art anders ist, steht in ihrer Klasse,
je einmal: wo ihre Staebe liegen, wie sie in den Tabellen der Herleitung
steht, wie sie in den Querschnitt eingeht
([[opencivil.querschnitt.bewehrungselemente#Bewehrungselement.als_bewehrung|Bewehrungselement.als_bewehrung]]) und welcher Durchmesser ihre
Rissbreite bestimmt. Welche Art eine Beschreibung ist, wird einmal
entschieden, beim Bauen ([[opencivil.querschnitt.bewehrungselemente#aus_stab|aus_stab]], [[opencivil.querschnitt.bewehrungselemente#aus_linie|aus_linie]]).

Bis 2026-10-25 war ein Element ein Datensatz mit der Art als Text, und ein
Dutzend Weichen in fuenf Modulen fragten sie ab.

Koordinaten und Durchmesser in mm, Flaechen in mm² -- wie in der Zeichnung.
Erst [[opencivil.querschnitt.bewehrungselemente#Bewehrungselement.als_bewehrung|als_bewehrung]] rechnet in Meter um.

## Inhalt

### Bewehrungselement

```python
@dataclass(frozen=True)
class Bewehrungselement(ABC)
```

Ein Bewehrungselement der Zeichnung -- siehe Dateikopf.

- `name: str`
- `kennung: str`
- `stahl: Baustoff`
- `von: Punkt`
- `bis: Punkt`
- `flaeche: float` – Die ganze Stahlflaeche des Elements in mm².
- `verschmiert: ClassVar[bool] = False` – Ob der Stahl ueber eine Linie verteilt ist statt in Staeben.

#### Bewehrungselement.punkte

```python
@property
def punkte(self) -> Tuple[Punkt, ...]
```

Die Stabmitten -- verschmiert keine.

#### Bewehrungselement.lage

```python
@property
def lage(self) -> Mathe
```

Wo es liegt, fuer die Tabelle der Herleitung.

#### Bewehrungselement.menge

```python
@property
@abstractmethod
def menge(self) -> Zelle
```

Wie viel Stahl es ist, fuer die Tabelle der Herleitung.

#### Bewehrungselement.kurzmenge

```python
@property
@abstractmethod
def kurzmenge(self) -> Zelle
```

Dasselbe kurz, fuer die Angaben ueber der Nachweistabelle.

#### Bewehrungselement.fiktiv

```python
@property
def fiktiv(self) -> bool
```

Ob sein [[opencivil.querschnitt.bewehrungselemente#Bewehrungselement.rissdurchmesser|rissdurchmesser]] erdacht ist statt gezeichnet.

#### Bewehrungselement.rissdurchmesser

```python
@property
@abstractmethod
def rissdurchmesser(self) -> float
```

Der Durchmesser, der die Rissbreite bestimmt.

#### Bewehrungselement.als_bewehrung

```python
@abstractmethod
def als_bewehrung(self, stahl: int, verdraengt: Verdraengt) -> List[Bewehrung]
```

Wie es in den Querschnitt eingeht, in Meter -- `stahl` ist der Index seines Stahls.

### Einzelstab

```python
@dataclass(frozen=True)
class Einzelstab(Bewehrungselement)
```

Ein Stab -- `von` und `bis` sind seine Mitte.

- `durchmesser: float`
- `kurzmenge = menge`

#### Einzelstab.punkte

```python
@property
def punkte(self) -> Tuple[Punkt, ...]
```

#### Einzelstab.lage

```python
@property
def lage(self) -> Mathe
```

#### Einzelstab.menge

```python
@property
def menge(self) -> Zelle
```

#### Einzelstab.rissdurchmesser

```python
@property
def rissdurchmesser(self) -> float
```

#### Einzelstab.als_bewehrung

```python
def als_bewehrung(self, stahl: int, verdraengt: Verdraengt) -> List[Bewehrung]
```

### Stabreihe

```python
@dataclass(frozen=True)
class Stabreihe(Bewehrungselement)
```

Gleiche Staebe auf einer Linie, nach Anzahl oder Teilung ([[opencivil.querschnitt.geometrie#stablinie|stablinie]]).

- `durchmesser: float`
- `linie: geo.Stablinie`
- `gewaehlt: Optional[float] = None` – Nach Teilung der eingegebene Abstand -- nach Anzahl keiner.

#### Stabreihe.punkte

```python
@property
def punkte(self) -> Tuple[Punkt, ...]
```

#### Stabreihe.menge

```python
@property
def menge(self) -> Zelle
```

#### Stabreihe.kurzmenge

```python
@property
def kurzmenge(self) -> Zelle
```

#### Stabreihe.rissdurchmesser

```python
@property
def rissdurchmesser(self) -> float
```

#### Stabreihe.als_bewehrung

```python
def als_bewehrung(self, stahl: int, verdraengt: Verdraengt) -> List[Bewehrung]
```

### VerschmierteLinie

```python
@dataclass(frozen=True)
class VerschmierteLinie(Bewehrungselement)
```

Stahl, gleichmaessig ueber eine Linie verteilt: die Flaeche von Hand oder
aus Staeben ⌀ im Abstand s ueber eine Laenge L.

- `aus_staeben: Optional[Tuple[float, float, float]] = None` – ⌀, s und L, aus denen die Flaeche kommt -- von Hand keine.
- `verschmiert = True`

#### VerschmierteLinie.menge

```python
@property
def menge(self) -> Zelle
```

#### VerschmierteLinie.kurzmenge

```python
@property
def kurzmenge(self) -> Zelle
```

#### VerschmierteLinie.fiktiv

```python
@property
def fiktiv(self) -> bool
```

Die Flaeche von Hand: ihr Durchmesser ist erdacht, nicht aus ⌀ und s.

#### VerschmierteLinie.rissdurchmesser

```python
@property
def rissdurchmesser(self) -> float
```

Aus Staeben deren ⌀. Die Flaeche von Hand verteilt sich auf Staebe im
Abstand [[opencivil.querschnitt.geometrie#Konstanten|TEILUNG_VERSCHMIERT]]
([[opencivil.querschnitt.geometrie#aequivalenter_durchmesser|aequivalenter_durchmesser]]).

#### VerschmierteLinie.als_bewehrung

```python
def als_bewehrung(self, stahl: int, verdraengt: Verdraengt) -> List[Bewehrung]
```

### aus_stab

```python
def aus_stab(s: Mapping) -> Einzelstab
```

Ein Stab der Beschreibung, wie [[opencivil.querschnitt.analyse#Querschnittsanalyse|Querschnittsanalyse]] ihn bekommt.

### aus_linie

```python
def aus_linie(l: Mapping, linie: geo.Stablinie) -> Bewehrungselement
```

Eine Stablinie der Beschreibung mit ihren aufgeloesten Staeben `linie`
-- nach ihrer Art eine Reihe von Staeben oder eine verschmierte Linie.


## Konstanten

- `MM = 0.001` – mm in m.
- `Verdraengt = Callable[[Punkt], Optional[int]]` – Zu einem Punkt der Zeichnung der Werkstoff, der dort liegt und den der Stahl verdraengt -- als Index, ohne Beton `None`.

## Braucht

- [[opencivil.core.latex]]
- [[opencivil.material.basis]]
- [[opencivil.querschnitt.geometrie]]
- [[opencivil.querschnitt.interaktion]]

## Gebraucht von

- [[opencivil.nachweis.schiefe_biegung]]
- [[opencivil.nachweis.stabgrenzen]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.spannungsanalyse.schnitt]]
