---
erzeugt: 253d0ffe9eb0
art: modul
tags: [modul]
---
> [!abstract] opencivil/decke/fem/netz.py
> das Dreiecksnetz einer Decke.
> Paket [[opencivil.decke.fem]] · [Quelltext](../../opencivil/decke/fem/netz.py)

## VERANTWORTUNG

Aus den Platten einer Decke ein Netz aus Dreiecken, nicht weiter als
[[opencivil.decke.modell#Decke|netzweite]], das allem folgt, was die
Rechnung an einer Linie oder einem Punkt braucht: den Rändern der Platten,
den Linienlagern, den Trägern und den Linienlasten als Kanten, den Stützen
als Knoten. Wo keine Platte liegt, ist ein Loch.


## WIE ES ENTSTEHT

1. Alle Linien werden an ihren Kreuzungen und an den Stützen auf ihnen
   geteilt; was neben den Platten liegt, fällt weg.
2. Jedes Stück bekommt Knoten in gleichen Abständen, höchstens die
   Netzweite `h` auseinander.
3. Ins Innere kommt ein Gitter gleichseitiger Dreiecke der Weite `h`,
   ohne die Punkte näher als [[opencivil.decke.fem.netz#Konstanten|ABSTAND]] · `h` an einer Linie.
4. Über alle Punkte eine Delaunay-Triangulierung
   ([[opencivil.decke.fem.delaunay|delaunay]]). Fehlt danach ein Stück einer
   Linie als Kante, wird es in der Mitte geteilt, bis es da ist – der
   Umkreis eines kurzen Stücks hat keinen fremden Punkt mehr.
5. Ein Dreieck gehört zu der Platte, in der sein Schwerpunkt liegt; eines
   in keiner fällt weg, mit ihm die Knoten, die nur ihm gehörten.
6. Die Knoten des Gitters rücken ein paarmal in die Mitte ihrer Nachbarn
   ([[opencivil.decke.fem.netz#Konstanten|GLAETTEN]]), solange kein Dreieck kippt – das gleicht aus, wo
   das Gitter schief an eine Linie stösst.

## Inhalt

### Linie

```python
@dataclass
class Linie
```

Eine Linie der Decke im Netz: ein Linienlager, ein Träger oder eine
Linienlast, von `a` nach `b`. `knoten` sind die Knoten auf ihr,
nach `u` – der Stelle in m ab `a` –, und `stuecke` die Paare
benachbarter Knoten, zwischen denen das Netz eine Kante hat: über ein
Loch hinweg keine.

- `name: str`
- `art: str`
- `a: Punkt`
- `b: Punkt`
- `knoten: List[int] = field(default_factory=list)`
- `u: List[float] = field(default_factory=list)`
- `stuecke: List[Tuple[int, int]] = field(default_factory=list)`

#### Linie.laenge

```python
@property
def laenge(self) -> float
```

#### Linie.richtung

```python
@property
def richtung(self) -> Punkt
```

### Netz

```python
@dataclass
class Netz
```

Die Knoten in m, die Dreiecke im Gegenuhrzeigersinn und je Dreieck die
Nummer seiner Platte in der Decke. `linien` nach Art und Name
([[opencivil.decke.fem.netz#Netz.linie|linie]]), `stuetzen`
je Stütze ihr Knoten – eine neben den Platten fehlt. `trennkanten`
sind die Kanten, über die hinweg die Momente und Querkräfte nicht
gemittelt werden ([[opencivil.decke.fem.glaetten|glaetten]]): Lager, Träger,
Linienlasten und Fugen zwischen Platten verschiedener Steifigkeit.

- `weite: float`
- `knoten: List[Punkt] = field(default_factory=list)`
- `dreiecke: List[Tuple[int, int, int]] = field(default_factory=list)`
- `platte: List[int] = field(default_factory=list)`
- `linien: Dict[Tuple[str, str], Linie] = field(default_factory=dict)`
- `stuetzen: Dict[str, int] = field(default_factory=dict)`
- `trennkanten: Set[Tuple[int, int]] = field(default_factory=set)`
- `meldungen: List[Meldung] = field(default_factory=list)`

#### Netz.flaeche

```python
def flaeche(self, e: int) -> float
```

#### Netz.linie

```python
def linie(self, art: str, name: str) -> Optional[Linie]
```

Die Linie `name` der Art `linienlager`, `traeger` oder `linienlast` – `None`, wenn sie keine Länge hat.

#### Netz.kanten

```python
def kanten(self) -> Set[Tuple[int, int]]
```

Jede Kante einmal, als `(kleinere, grössere Nummer)`.

#### Netz.auf_strecke

```python
def auf_strecke(self, linie: Linie, kanten: Optional[Set[Tuple[int, int]]]=None) -> Linie
```

`linie` mit den Knoten auf ihr, nach der Stelle `u` ab `a` –
und den Stücken, die Kanten des Netzes sind (`kanten`, ohne Angabe
[[opencivil.decke.fem.netz#Netz.kanten|kanten]]).

### kante

```python
def kante(a: int, b: int) -> Tuple[int, int]
```

### schaetzung

```python
def schaetzung(decke: Decke, weite: float) -> int
```

Wie viele Knoten das Netz etwa hätte: je Knoten zwei gleichseitige Dreiecke.

### vernetzen

```python
def vernetzen(decke: Decke, weite: float) -> Netz
```

Das Netz der Decke – ihre Platten geprüft ([[opencivil.decke.streifen#pruefen|pruefen]]).

### _linien

```python
def _linien(decke: Decke) -> List[Linie]
```

Die Linien der Decke, die das Netz als Kanten braucht.

### _geteilt

```python
def _geteilt(strecken: Sequence[Tuple[Punkt, Punkt]], punkte: Sequence[Punkt]) -> List[Tuple[Punkt, Punkt]]
```

Die Strecken in Stücke, geteilt an jeder Kreuzung, an jedem Ende einer
anderen auf ihnen und an jedem Punkt auf ihnen – jedes Stück einmal.

### _auf

```python
def _auf(p: Punkt, a: Punkt, b: Punkt) -> Optional[float]
```

Wo `p` auf der Strecke `a → b` liegt, als Parameter – `None`, wenn daneben.

### _Raster

```python
class _Raster
```

Strecken in Zellen der Netzweite – damit ein Punkt nur die nahen prüft.

#### _Raster.strecke

```python
def strecke(self, p: Punkt, q: Punkt, rand: float) -> None
```

#### _Raster.frei

```python
def frei(self, p: Punkt, abstand: float) -> bool
```

Ob `p` mindestens `abstand` von jeder Strecke liegt.

### _gitter

```python
def _gitter(platten: Sequence[Sequence[Punkt]], x0: float, y0: float, x1: float, y1: float, weite: float) -> Iterable[Punkt]
```

Die Punkte eines Gitters gleichseitiger Dreiecke in den Platten – Zeile um Zeile, hin und her.

### _erzwingen

```python
def _erzwingen(t: Triangulierung, zwang: List[Tuple[int, int]], weite: float) -> int
```

Teilt jedes Stück einer Linie, das als Kante fehlt, in der Mitte, bis
alle da sind – `zwang` danach mit den geteilten Stücken – und gibt
zurück, wie viele es nicht wurden, weil sie kürzer als
[[opencivil.decke.fem.netz#Konstanten|KUERZESTES]] der Netzweite geworden wären. Ein neuer Punkt kann
eine Kante nehmen, die schon da war; darum wird jede Runde alles geprüft.

### _uebernehmen

```python
def _uebernehmen(netz: Netz, t: Triangulierung, platten: Sequence[Sequence[Punkt]]) -> Dict[int, int]
```

Die Dreiecke in Platten ins Netz, ihre Knoten neu gezählt – zurück: je Punkt der Triangulierung sein Knoten.

### _glaetten

```python
def _glaetten(netz: Netz, fest: Set[int]) -> None
```

Jeder Knoten, der nicht auf einer Linie oder an einer Stütze liegt, rückt
in die Mitte seiner Nachbarn – nur, wenn danach jedes Dreieck um ihn
noch richtig herum liegt.

### _linien_finden

```python
def _linien_finden(netz: Netz, linien: Sequence[Linie]) -> None
```

Je Linie die Knoten auf ihr, nach der Stelle – und die Stücke, die Kanten des Netzes sind.

### _trennkanten

```python
def _trennkanten(netz: Netz, decke: Decke) -> Set[Tuple[int, int]]
```

Lager, Träger und Linienlasten – und wo zwei Platten verschieden steif aneinanderstossen.


## Konstanten

- `ABSTAND = 0.55` – So nahe an einer Linie bleibt kein Punkt des Gitters, als Teil der Netzweite.
- `GLAETTEN = 3` – So oft rücken die Knoten des Gitters in die Mitte ihrer Nachbarn.
- `KUERZESTES = 1.0 / 64.0` – Kürzer wird ein Stück einer Linie beim Teilen nicht, als Teil der Netzweite.
- `GLEICH = 1e-07` – Was als derselbe Punkt gilt, in m.

## Braucht

- [[opencivil.decke.fem.delaunay]]
- [[opencivil.decke.geometrie]]
- [[opencivil.decke.modell]]
- [[opencivil.stabwerk.system]]

## Gebraucht von

- [[opencivil.decke.fem.belastung]]
- [[opencivil.decke.fem.glaetten]]
- [[opencivil.decke.fem.rechnung]]
- [[opencivil.decke.fem.system]]
