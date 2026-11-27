---
erzeugt: e92431a2ed00
art: modul
tags: [modul]
---
> [!abstract] opencivil/fachwerkmodell/grundstruktur.py
> die Knoten und die möglichen Stäbe einer Scheibe.
> Paket [[opencivil.fachwerkmodell]] · [Quelltext](../../opencivil/fachwerkmodell/grundstruktur.py)

## VERANTWORTUNG

Die Grundstruktur des Verfahrens Ground Structure (He, Gilbert & Song
2019): Knoten in einem Raster der Weite h, soweit sie im Material liegen,
dazu jeder Punkt eines Lagers und einer Last und jede Ecke eines Umrisses
([[opencivil.fachwerkmodell.grundstruktur#grundstruktur|grundstruktur]]). Zwischen je zwei Knoten ein möglicher Stab, wenn
er ganz im Material liegt – auf dem Rand eines Lochs zählt, quer durch
sein Inneres nicht. Liefe ein Stab über einen dritten Knoten, fällt er weg:
aus zwei kürzeren ist er schon da, und doppelt trüge er dieselbe Kraft auf
zwei Wegen.


## DAS GLEICHGEWICHT

Je Knoten zwei Richtungen, x und y; wo ein Lager hält, fällt die Richtung
weg – dort nimmt es die Kraft. Die übrigen sind die Zeilen des
Gleichgewichts ([[opencivil.fachwerkmodell.grundstruktur#Grundstruktur|Grundstruktur.zeilen]]): an jeder ist die Summe der
Stabkräfte gleich der Last, mit umgekehrtem Vorzeichen
([[opencivil.fachwerkmodell.grundstruktur#Grundstruktur|Grundstruktur.spalte]]).


## DIE GRENZE

Mehr als [[opencivil.fachwerkmodell.grundstruktur#Konstanten|HOECHSTENS_KNOTEN]] Knoten sucht das Werkzeug nicht: die
möglichen Stäbe wachsen mit dem Quadrat der Knoten, bei 300 Knoten sind es
gegen 17 000. Die Grenze ist nach Vorgabe, nicht nachgeschlagen.

## Inhalt

### ZuVieleKnoten

```python
class ZuVieleKnoten(Exception)
```

Das Raster ist zu fein: der Satz sagt, wie viele Knoten es gäbe und was zu tun ist.

### Grundstruktur

```python
@dataclass(frozen=True)
class Grundstruktur
```

Knoten, mögliche Stäbe und die Zeilen des Gleichgewichts einer Scheibe.

- `modell: Modell`
- `knoten: Tuple[Punkt, ...]` – In m: zuerst das Raster, Zeile um Zeile von unten, dann Lager, Lasten und Ecken.
- `staebe: Tuple[Tuple[int, int], ...]` – Je möglicher Stab seine zwei Knoten.
- `laengen: Tuple[float, ...]`
- `zeilen: Dict[Tuple[int, int], int]` – `(knoten, richtung)` -> Zeile des Gleichgewichts; Richtung 0 ist x, 1 ist y.
- `last: Tuple[float, ...]` – Je Zeile die Last in N.
- `weite: float`

#### Grundstruktur.spalten

```python
@cached_property
def spalten(self) -> Tuple[Spalte, ...]
```

Je Stab, was er mit der Kraft 1 (Zug) zu den Zeilen gibt: an seinem
ersten Knoten seine Richtung zum zweiten negativ, am zweiten positiv –
dort, wo kein Lager hält.

#### Grundstruktur.knoten_bei

```python
def knoten_bei(self, p: Punkt) -> Optional[int]
```

Der Knoten an `p` – ein Lager oder eine Last steht genau auf einem.

### grundstruktur

```python
def grundstruktur(modell: Modell, weite: float) -> Grundstruktur
```

Die Grundstruktur der Scheibe mit der Rasterweite `weite` in m. Das
Modell ist geprüft ([[opencivil.fachwerkmodell.pruefen#pruefen|pruefen]]):
es hat eine Scheibe, Lager und Lasten, alle im Material.
Wirft [[opencivil.fachwerkmodell.grundstruktur#ZuVieleKnoten|ZuVieleKnoten]], wenn das Raster zu fein ist.

### _knoten

```python
def _knoten(modell: Modell, weite: float) -> Tuple[List[Punkt], List[Optional[Tuple[int, int]]], Punkt]
```

Die Knoten, je Knoten sein Platz im Raster `(i, j)` – `None` für
die übrigen – und der Punkt `(0, 0)` des Rasters: die Ecke unten
links des Rechtecks um die Scheiben. Ein Lager, eine Last oder eine
Ecke auf einem Rasterpunkt gibt ihm ihre genauen Koordinaten.

### _zu_viele

```python
def _zu_viele(modell: Modell, weite: float, anzahl: str) -> str
```

Der Satz, wenn das Raster zu fein ist – mit einer Rasterweite, die passt, auf 5 cm genau.

### _staebe

```python
def _staebe(modell: Modell, knoten: Sequence[Punkt], raster: Sequence[Optional[Tuple[int, int]]], ursprung: Punkt, weite: float) -> List[Tuple[int, int]]
```

Je zwei Knoten ein Stab, wenn kein dritter auf ihm liegt und er ganz im Material ist.

### _auf_innen

```python
def _auf_innen(p: Punkt, a: Punkt, b: Punkt) -> bool
```

Ob `p` auf der Strecke `a → b` liegt, nicht an ihren Enden.

### _rasterknoten_auf

```python
def _rasterknoten_auf(knoten: Sequence[Punkt], ka: int, kb: int, im_raster: Dict[Tuple[int, int], int], ursprung: Punkt, weite: float) -> bool
```

Ob ein Knoten des Rasters auf der Strecke von Knoten `ka` zu `kb`
liegt, ausser den beiden selbst: geprüft, wo sie die Linien des Rasters
quer zu ihrer längeren Richtung kreuzt.

### _im_material

```python
def _im_material(modell: Modell, umrisse: Sequence[Sequence[Punkt]], a: Punkt, b: Punkt) -> bool
```

Ob die Strecke `a → b` ganz im Material liegt: geteilt, wo sie einen
Rand trifft, liegt jedes Stück ganz innen, ganz aussen oder auf einem
Rand – seine Mitte sagt, welches.


## Konstanten

- `HOECHSTENS_KNOTEN = 600` – Wie viele Knoten die Grundstruktur höchstens hat – nach Vorgabe, nicht nachgeschlagen.
- `HOECHSTENS_RASTERPUNKTE = 200000` – Ab wie vielen Punkten im Rechteck um die Scheibe das Raster gar nicht erst gelegt wird.

## Braucht

- [[opencivil.decke.geometrie]]
- [[opencivil.fachwerkmodell.modell]]
- [[opencivil.fachwerkmodell.optimierung]]

## Gebraucht von

- [[opencivil.fachwerkmodell.suche]]
- [[opencivil.web.fachwerkdaten]]
