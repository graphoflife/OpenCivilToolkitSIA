---
erzeugt: dc557a8e6032
art: modul
tags: [modul]
---
> [!abstract] opencivil/querschnitt/plastisch.py
> Spannungsbloecke an einer geraden Nulllinie, starr-plastisch.
> Paket [[opencivil.querschnitt]] · [Quelltext](../../opencivil/querschnitt/plastisch.py)

## VERANTWORTUNG

Was der Stahlquerschnitt ([[opencivil.stahlbau.querschnitt]]) und der
Verbundquerschnitt ([[opencivil.verbund.querschnitt]]) plastisch teilen,
in mm und N/mm²:

* Polygone mit Gewicht in Gruppen ([[opencivil.querschnitt.plastisch#Stueck|Stueck]]), je Gruppe ein Werkstoff
  mit seiner Festigkeit -- und die Regel, nach der ein Polygon seinen
  Elternteil dort ersetzt, wo es liegt ([[opencivil.querschnitt.plastisch#stuecke|stuecke]]);
* an einer Nulllinie ([[opencivil.querschnitt.plastisch#Linie|Linie]]) je Gruppe die Spannung `+zug` auf der
  gezogenen und `-druck` auf der gedrueckten Seite ([[opencivil.querschnitt.plastisch#Starrplastisch|Starrplastisch]]):
  die Kraefte, je Teil die Bloecke mit ihrem Angriffspunkt, die Nulllinie bei
  einer Normalkraft und der Zustand, dessen Moment in die Richtung einer
  Einwirkung zeigt.

Beim Baustahl sind `zug` und `druck` gleich, beim Beton im Verbund ist
`zug` null. Wie weit ein Querschnitt so rechnen darf, sagen die Normen;
hier steht nur die Rechnung, an einer Stelle.


## VORZEICHEN

N > 0 Zug; `M_y = -∫σ (z - z_b) dA` zieht unten, `M_z = -∫σ (y - y_b) dA`
links -- um einen Bezugspunkt `b`.

## Inhalt

### Linie

```python
@dataclass(frozen=True)
class Linie
```

Eine Nulllinie `n·p = v`, in mm: gezogen, wo `n·p > v`, gedrueckt, wo
`n·p < v` -- `n` zeigt zur gezogenen Seite. Mit `n = (0, 0)` liegt
sie ausserhalb des Querschnitts: dann ist alles gedrueckt
([[opencivil.querschnitt.plastisch#Konstanten|DRUCK]]) oder alles gezogen ([[opencivil.querschnitt.plastisch#Konstanten|ZUG]]).

- `n: Tuple[float, float]`
- `v: float`

#### Linie.d

```python
def d(self, p: Punkt) -> float
```

Wie weit `p` auf der gezogenen Seite liegt -- negativ, wo es gedrueckt ist.

### Stueck

```python
@dataclass(frozen=True)
class Stueck
```

Ein Polygon mit Gewicht in einer Gruppe: +1, wo es liegt, -1 im
Elternteil, den es dort ersetzt, dazwischen ein Anteil -- so mindert die
Querkraft einen Steg. `teil` ist der Index des Teils, zu dem es zaehlt
-- bei einer Aussparung der des Teils darum --, `was` sagt, wofuer ein
Streifen weggenommen ist.

- `gruppe: int`
- `gewicht: float`
- `punkte: Tuple[Punkt, ...]`
- `teil: int`
- `was: str = ''`

#### Stueck.werte

```python
@cached_property
def werte(self) -> geo.Flaechenwerte
```

### Block

```python
@dataclass(frozen=True)
class Block
```

Die Kraft einer Zone eines Teils an einer Nulllinie, in N, und wo sie angreift, in mm.

- `teil: int`
- `was: str`
- `zone: str` – «Zug» oder «Druck».
- `F: float`
- `punkt: Punkt`

### Zustand

```python
@dataclass(frozen=True)
class Zustand
```

Der Zustand an einer Nulllinie: was die Bloecke tragen, in N und N·mm um den Bezugspunkt.

- `linie: Linie`
- `N: float`
- `M_y: float`
- `M_z: float`

### stuecke

```python
def stuecke(punkte: Sequence[Sequence[Punkt]], eltern: Sequence[Optional[int]], gruppe_von: Mapping[int, int], teil_von: Mapping[int, int]) -> List[Stueck]
```

Die Stuecke einer Zeichnung: ein Polygon zaehlt in seiner Gruppe mit +1
und in der seines Elternteils mit -1 -- so nimmt eine Aussparung den
Werkstoff darum weg, und ein Polygon aus anderem ersetzt ihn dort. Ein
Polygon ohne Gruppe in `gruppe_von` zaehlt nicht mit: fuer diese
Gruppen ist es eine Aussparung. `teil_von` sagt je Polygon mit
Gruppe, zu welchem Teil es gehoert.

### Starrplastisch

```python
@dataclass(frozen=True)
class Starrplastisch
```

Stuecke mit ihren Festigkeiten, je Gruppe `zug` und `druck` als
Betraege in N/mm² -- siehe Dateikopf.

- `stuecke: Tuple[Stueck, ...]`
- `zug: Tuple[float, ...]`
- `druck: Tuple[float, ...]`

#### Starrplastisch.zugkraft

```python
@property
def zugkraft(self) -> float
```

Was der Querschnitt ganz gezogen traegt, in N.

#### Starrplastisch.druckkraft

```python
@property
def druckkraft(self) -> float
```

Was er ganz gedrueckt traegt, als Betrag in N.

#### Starrplastisch.kraefte

```python
def kraefte(self, linie: Linie, bezug: Punkt) -> Tuple[float, float, float]
```

Was die Bloecke an der Nulllinie tragen: `(N, M_y, M_z)` in N, N·mm um `bezug`.

#### Starrplastisch.bloecke

```python
def bloecke(self, linie: Linie) -> List[Block]
```

Je Teil -- und je weggenommenem Streifen -- die Kraft seiner gezogenen
und seiner gedrueckten Zone an der Nulllinie, mit Angriffspunkt: die
Probe zu [[opencivil.querschnitt.plastisch#Starrplastisch.kraefte|kraefte]], Teil fuer Teil.

#### Starrplastisch.nulllinie

```python
def nulllinie(self, n: Tuple[float, float], N: float=0.0) -> Optional[float]
```

Die Nulllinie `n·p = v` bei der Normalkraft `N` in N. `None`,
wo `N` jenseits der reinen Zug- oder Druckkraft liegt. Gesucht mit
Illinois, bis sie auf 1e-9 mm genau liegt: je weiter sie zur
gezogenen Seite rueckt, desto kleiner die Kraft.

#### Starrplastisch.zustand

```python
def zustand(self, N: float, M_y: float, M_z: float, bezug: Punkt, neigung: Optional[float]) -> Optional[Zustand]
```

Der Zustand bei `N`, dessen Moment in die Richtung von
`(M_y, M_z)` zeigt -- mit fester Zugrichtung `neigung`, wo sie
feststeht ([[opencivil.querschnitt.biegung#Biegung.neigung|neigung]]).
`None`, wo `N` jenseits der reinen Zug- oder Druckkraft liegt.
Gesucht wird die Neigung der Nulllinie wie beim Stahlbeton
([[opencivil.core.suche#winkel_suchen|winkel_suchen]]).


## Konstanten

- `DRUCK = Linie((0.0, 0.0), 1.0)` – Gleichmaessiger Druck und gleichmaessiger Zug -- ohne Nulllinie im Querschnitt.
- `ZUG = Linie((0.0, 0.0), -1.0)`

## Braucht

- [[opencivil.core.suche]]
- [[opencivil.querschnitt.geometrie]]
- [[opencivil.querschnitt.interaktion]]

## Gebraucht von

- [[opencivil.nachweis.qa_stahl]]
- [[opencivil.nachweis.qa_stahl_kennzahlen]]
- [[opencivil.nachweis.qa_verbund_kennzahlen]]
- [[opencivil.stahlbau.querschnitt]]
- [[opencivil.stahlbau.widerstand]]
- [[opencivil.verbund.querschnitt]]
- [[opencivil.verbund.widerstand]]
