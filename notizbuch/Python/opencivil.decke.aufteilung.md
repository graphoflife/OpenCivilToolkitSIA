---
erzeugt: 1c5692373df1
art: modul
tags: [modul]
---
> [!abstract] opencivil/decke/aufteilung.py
> welcher Teil der Last in welche Richtung geht.
> Paket [[opencivil.decke]] · [Quelltext](../../opencivil/decke/aufteilung.py)

## VERANTWORTUNG

An jeder Stelle einer Platte geht ein Anteil der Last in ihre Richtung 1,
der Rest in Richtung 2 (Stahlbeton II, 7.2 Platten, Folien 29 bis 31).
Hier steht, welcher – als Flächen mit Anteil, je Feldstreifen und je Gruppe
von Platten mit denselben Richtungen. [[opencivil.decke.lasten|lasten]] legt
die Last darauf.


## DREI QUELLEN, IN DIESER FOLGE

1. **Gezeichnete Zonen** gehen vor: dort gilt ihr Anteil.
2. Sonst, bei **fester Aufteilung**, überall derselbe Anteil.
3. Sonst, **automatisch**, nach dem Muster der Folie 31 – was nahe an einem
   Rand liegt, geht auf kürzestem Weg in dessen Lager. Gerechnet wird je
   Zelle, wo sich ein Streifen der einen und einer der anderen Richtung
   kreuzen:

   * Trägt nur eine Richtung – der Streifen der anderen ist beweglich –,
     geht alles in sie. Trägt keine, geht die Last trotzdem je zur Hälfte
     in die Streifen: dort fällt sie aus, die Probe zählt sie als nicht
     getragen, und das Bild zeigt die Stelle als «trägt nicht».
   * `b` ist die kleinere Spannweite der beiden Felder, in denen die
     Zelle liegt; eine Kragplatte zählt doppelt so lang.
   * Liegt die Zelle in einer Richtung höchstens `b/4` vor einem Lager,
     geht die Last in diese Richtung – liegt sie in beiden so nahe, je zur
     Hälfte (die Ecken der Folie 31).
   * Sonst geht sie mehr in die Richtung mit dem kürzeren Feld: bei
     gleichen Feldern je zur Hälfte, ab dem Verhältnis [[opencivil.decke.aufteilung#Konstanten|GANZ_AB]] der
     Spannweiten ganz, dazwischen geradlinig ([[opencivil.decke.aufteilung#in_der_mitte|in_der_mitte]];
     Benutzer, 2026-11-25). So springt der Anteil nicht, wenn eine
     Spannweite um ein Weniges wächst: 5 × 5.04 m und 5 × 5.06 m teilen
     fast gleich.

```
Für die einfach gelagerte Rechteckplatte der Folie 31 -- Verhältnis 2
-- ergibt das genau deren Aufteilung. Für andere Platten ist es eine
Verallgemeinerung -- nach Vorgabe. Die Norm schreibt keine vor: nach der
statischen Methode gilt jede, die im Gleichgewicht ist (SIA 262:2025,
4.1.4.2.2).
```


## WO LAST AUSFÄLLT

Je Zelle, ob ihre Last auf einen Durchlaufträger kommt, der nicht trägt: weil keine
Richtung trägt – dann fehlt ein Lager oder ein Träger –, oder weil die
feste Aufteilung oder eine Zone Last in eine Richtung gibt, die nicht
trägt. Je Platte und Ursache steht das in einer grauen Meldung an der
Platte, mit der Fläche: es fehlt etwas, und der Rest rechnet (Benutzer,
2026-11-19). Eine Zone gilt dafür in den Zellen, deren Schwerpunkt in ihr
liegt.


## FLÄCHEN MIT ANTEIL

Ein [[opencivil.decke.aufteilung#Anteil|Anteil]] ist ein konvexes Vieleck und ein Faktor: die Last
darauf, mal den Faktor, geht in den Streifen. Eine Zone wird abgezogen und
hinzugefügt – ihr Faktor ist der Unterschied zum Grundanteil darunter –,
darum dürfen sich Zonen nicht überlappen.

## Inhalt

### Anteil

```python
@dataclass(frozen=True)
class Anteil
```

Ein konvexes Vieleck (Gegenuhrzeigersinn) und der Faktor, mit dem die Last darauf in den Streifen geht.

- `ecken: Tuple[Punkt, ...]`
- `faktor: float`

### Zelle

```python
@dataclass(frozen=True)
class Zelle
```

Wo sich der Streifen `i` der Richtung 1 und der Streifen `j` der
Richtung 2 kreuzen: ihre Stücke in den Platten der Gruppe, deren
Schwerpunkt und wo er auf den Durchlaufträgern beider Richtungen liegt.

- `i: int`
- `j: int`
- `teile: Tuple[Tuple[Punkt, ...], ...]`
- `mitte: Punkt`
- `lage_1: Lage`
- `lage_2: Lage`

#### Zelle.flaeche_in

```python
def flaeche_in(self, platte: Platte) -> float
```

Wie viel von ihr in der Platte liegt – jedes Stück liegt in einer, sein Schwerpunkt also auch.

### Aufteilungen

```python
@dataclass
class Aufteilungen
```

Je `(Feldstreifen, Gruppe)` die Flächen mit Anteil – und je Zelle, was automatisch entschieden wurde.

- `flaechen: Dict[Tuple[str, int], List[Anteil]]`
- `zellen: List[Bildzelle]` – Fürs Bild, was automatisch entschieden wurde: Vieleck und Anteil in Richtung 1 – `None`, wo keine Richtung trägt –, je Streifen der Richtung 1 die Zellen gleichen Anteils zusammengelegt, wie die Last sie bekommt, geschnitten mit der Platte.
- `meldungen: List[Meldung]`

### aufteilen

```python
def aufteilen(decke: Decke, zerlegung: Zerlegung) -> Aufteilungen
```

### _ganz

```python
def _ganz(s: Streifen, gruppe: Gruppe) -> List[Punkt]
```

Das Band des Streifens, so lang, dass es die Gruppe ganz deckt.

### _zellen

```python
def _zellen(zerlegung: Zerlegung, gruppe: Gruppe, streifen1: Sequence[Streifen], streifen2: Sequence[Streifen]) -> List[Zelle]
```

Die Zellen, die in den Platten der Gruppe liegen, je mit der Lage ihres Schwerpunkts.

### _automatisch

```python
def _automatisch(gruppe: Gruppe, streifen1: Sequence[Streifen], streifen2: Sequence[Streifen], zellen: Sequence[Zelle]) -> Tuple[Dict[Tuple[str, int], List[Anteil]], List[Bildzelle]]
```

Je Streifen die Flächen nach dem Anteil jeder Zelle, Zellen gleichen
Anteils längs des Streifens zusammengelegt. Fürs Bild dieselben Flächen
der Richtung 1, geschnitten mit der Platte – ohne Anteil, wo keine
Richtung trägt.

### _ausfall

```python
def _ausfall(decke: Decke, gruppe: Gruppe, zellen: Sequence[Zelle]) -> List[Meldung]
```

Je Platte und Ursache, wo Last ausfällt, eine graue Meldung an ihr: wo
keine Richtung trägt, je Richtung warum; wo die feste Aufteilung oder
eine Zone Last in eine Richtung gibt, die nicht trägt, wer und wie viel.

### _wo

```python
def _wo(je_richtung: Dict[str, List[str]]) -> str
```

«in x liegt sie nur auf «W3», …; in y liegt sie auf nichts» – gleiche Gründe einmal, «in x und y».

### _zusammengelegt

```python
def _zusammengelegt(band: Sequence[Punkt], quer: Sequence[Streifen], folge: Sequence[Tuple[int, Optional[float]]]) -> List[Bildzelle]
```

Die Zellen längs eines Streifens, die nebeneinanderliegenden mit gleichem
Anteil zu einer: das Band, geschnitten mit den Streifen quer von der
ersten bis zur letzten – je Vieleck und Anteil.

### _anteil_bei

```python
def _anteil_bei(la: Lage, lb: Lage) -> Optional[float]
```

Der Anteil in Richtung 1, wo eine Stelle in `la` und `lb` liegt – `None`, wenn keine Richtung trägt.

### in_der_mitte

```python
def in_der_mitte(spannweite_1: float, spannweite_2: float) -> float
```

Der Anteil in Richtung 1 fern der Lager: je zur Hälfte bei gleichen
Spannweiten, geradlinig mehr in die kürzere, ganz in sie ab dem
Verhältnis [[opencivil.decke.aufteilung#Konstanten|GANZ_AB]]. Ohne Feld – unendlich – in beiden
Richtungen je zur Hälfte.

### lage

```python
def lage(zerlegung: Zerlegung, p: Punkt, streifen: Streifen, r: Richtung) -> Lage
```

Wo `p` auf dem trägt, was dort die Last in Richtung `r` übernimmt:
ein Träger in dieser Richtung, in dessen Fläche `p` liegt, sonst der
Feldstreifen.


## Konstanten

- `UEBERSTAND = 1.0` – So viel länger als die Gruppe reicht ein Anteil, der einen ganzen Streifen deckt, in m.
- `GANZ_AB = 1.5` – Ab diesem Verhältnis der Spannweiten geht die Mitte eines Felds ganz in die kürzere Richtung.
- `Bildzelle = Tuple[Tuple[Punkt, ...], Optional[float]]` – Fürs Bild ein Vieleck und sein Anteil in Richtung 1 – `None`, wo keine Richtung trägt.

## Braucht

- [[opencivil.core.latex]]
- [[opencivil.decke.geometrie]]
- [[opencivil.decke.modell]]
- [[opencivil.decke.streifen]]
- [[opencivil.stabwerk.system]]

## Gebraucht von

- [[opencivil.decke.herleitung]]
- [[opencivil.decke.lasten]]
- [[opencivil.decke.rechnung]]
