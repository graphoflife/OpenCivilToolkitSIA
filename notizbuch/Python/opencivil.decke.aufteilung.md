---
erzeugt: df79b83c6532
art: modul
tags: [modul]
---
> [!abstract] opencivil/decke/aufteilung.py
> welcher Teil der Last in welche Richtung geht.
> Paket [[opencivil.decke]] · [Quelltext](../../opencivil/decke/aufteilung.py)

## VERANTWORTUNG

An jeder Stelle einer Platte geht ein Anteil der Last in ihre Richtung 1,
der Rest in Richtung 2 (Stahlbeton II, 7.2 Platten, Folien 29 bis 31).
Hier steht, welcher -- als Flächen mit Anteil, je Feldstreifen und je Gruppe
von Platten mit denselben Richtungen. [[opencivil.decke.lasten|lasten]] legt
die Last darauf.


## DREI QUELLEN, IN DIESER FOLGE

1. **Gezeichnete Zonen** gehen vor: dort gilt ihr Anteil.
2. Sonst, bei **fester Aufteilung**, überall derselbe Anteil.
3. Sonst, **automatisch**, nach dem Muster der Folie 31 -- was nahe an einem
   Rand liegt, geht auf kürzestem Weg in dessen Lager. Gerechnet wird je
   Zelle, wo sich ein Streifen der einen und einer der anderen Richtung
   kreuzen:

   * Trägt nur eine Richtung -- der Streifen der anderen ist beweglich --,
     geht alles in sie.
   * `b` ist die kleinere Spannweite der beiden Felder, in denen die
     Zelle liegt; eine Kragplatte zählt doppelt so lang.
   * Liegt die Zelle in einer Richtung höchstens `b/4` vor einem Lager,
     geht die Last in diese Richtung -- liegt sie in beiden so nahe, je zur
     Hälfte (die Ecken der Folie 31).
   * Sonst geht sie in die Richtung mit dem kürzeren Feld, bei gleichen
     Feldern je zur Hälfte.

```
Für die einfach gelagerte Rechteckplatte der Folie 31 ergibt das genau
deren Aufteilung. Für andere Platten ist es eine Verallgemeinerung --
nach Vorgabe. Die Norm schreibt keine vor: nach der statischen Methode
gilt jede, die im Gleichgewicht ist (SIA 262:2025, 4.1.4.2.2).
```


## FLÄCHEN MIT ANTEIL

Ein [[opencivil.decke.aufteilung#Anteil|Anteil]] ist ein konvexes Vieleck und ein Faktor: die Last
darauf, mal den Faktor, geht in den Streifen. Eine Zone wird abgezogen und
hinzugefügt -- ihr Faktor ist der Unterschied zum Grundanteil darunter --,
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

### Aufteilungen

```python
@dataclass
class Aufteilungen
```

Je `(Feldstreifen, Gruppe)` die Flächen mit Anteil -- und je Zelle, was automatisch entschieden wurde.

- `flaechen: Dict[Tuple[str, int], List[Anteil]]`
- `zellen: List[Tuple[Tuple[Punkt, ...], float]]` – Fürs Bild, was automatisch entschieden wurde: Vieleck und Anteil in Richtung 1 -- je Streifen der Richtung 1 die Zellen gleichen Anteils zusammengelegt, wie die Last sie bekommt, geschnitten mit der Platte.
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

### _automatisch

```python
def _automatisch(zerlegung: Zerlegung, gruppe: Gruppe, streifen1: Sequence[Streifen], streifen2: Sequence[Streifen])
```

Die Zellen der Gruppe, je mit ihrem Anteil in Richtung 1 -- und daraus je
Streifen die Flächen, Zellen gleichen Anteils längs des Streifens
zusammengelegt. Fürs Bild dieselben Flächen der Richtung 1, geschnitten
mit der Platte. Dazu je Platte, an wie vielen Zellen keine Richtung trägt.

### _zusammengelegt

```python
def _zusammengelegt(band: Sequence[Punkt], quer: Sequence[Streifen], folge: Sequence[Tuple[int, float]]) -> List[Anteil]
```

Die Zellen längs eines Streifens, die nebeneinanderliegenden mit gleichem
Anteil zu einer: das Band, geschnitten mit den Streifen quer von der
ersten bis zur letzten.

### _anteil_bei

```python
def _anteil_bei(zerlegung: Zerlegung, p: Punkt, a: Tuple[Streifen, Richtung], b: Tuple[Streifen, Richtung]) -> Optional[float]
```

Der Anteil in Richtung 1 an der Stelle `p` -- `None`, wenn keine Richtung trägt.

### lage

```python
def lage(zerlegung: Zerlegung, p: Punkt, streifen: Streifen, r: Richtung) -> Lage
```

Wo `p` auf dem trägt, was dort die Last in Richtung `r` übernimmt:
ein Unterzug in dieser Richtung, in dessen Fläche `p` liegt, sonst der
Feldstreifen.


## Konstanten

- `UEBERSTAND = 1.0` – So viel länger als die Gruppe reicht ein Anteil, der einen ganzen Streifen deckt, in m.
- `GLEICHE_SPANNWEITE = 0.01` – Zwei Spannweiten, die weniger als so viel auseinanderliegen, gelten als gleich.

## Braucht

- [[opencivil.decke.geometrie]]
- [[opencivil.decke.modell]]
- [[opencivil.decke.streifen]]
- [[opencivil.stabwerk.system]]

## Gebraucht von

- [[opencivil.decke.lasten]]
- [[opencivil.decke.rechnung]]
