---
erzeugt: 4ab1fb02ab10
art: modul
tags: [modul]
---
> [!abstract] opencivil/decke/fem/delaunay.py
> eine Delaunay-Triangulierung, Punkt für Punkt.
> Paket [[opencivil.decke.fem]] · [Quelltext](../../opencivil/decke/fem/delaunay.py)

## VERANTWORTUNG

Dreiecke über einer Menge von Punkten, so dass kein Punkt im Umkreis eines
Dreiecks liegt (Bowyer 1981, Watson 1981): ein neuer Punkt löscht die
Dreiecke, in deren Umkreis er liegt, und verbindet sich mit dem Rand des
Lochs. Das Dreieck, in dem er liegt, findet ein Weg vom zuletzt gebauten
aus – wer die Punkte so einfügt, wie sie nebeneinander liegen, geht nur
wenige Schritte.

Am Anfang steht ein grosses Dreieck um alle Punkte; was an seinen Ecken
hängt, fällt am Ende weg ([[opencivil.decke.fem.delaunay#Triangulierung.dreiecke|Triangulierung.dreiecke]]).


## RUNDUNG

Ein Punkt auf einer Kante gilt als in beiden Dreiecken; liegt er nach der
Rundung knapp neben dem Rand des Lochs, wächst das Loch um das Dreieck
dahinter, statt ein flaches Dreieck zu bauen. Ein Punkt, der schon da ist
([[opencivil.decke.fem.delaunay#Triangulierung|Triangulierung.gleich]]), kommt nicht ein zweites Mal hinein.

## Inhalt

### orientierung

```python
def orientierung(a: Punkt, b: Punkt, c: Punkt) -> float
```

Die doppelte Fläche des Dreiecks `a, b, c`: positiv im Gegenuhrzeigersinn.

### im_umkreis

```python
def im_umkreis(a: Punkt, b: Punkt, c: Punkt, d: Punkt) -> float
```

Positiv, wenn `d` im Umkreis des Dreiecks `a, b, c` (im Gegenuhrzeigersinn) liegt.

### Triangulierung

```python
class Triangulierung
```

Die Dreiecke über den Punkten, die bisher eingefügt sind. Je Dreieck
seine Ecken im Gegenuhrzeigersinn und je Ecke das Nachbardreieck über
der Kante ihr gegenüber (-1: keines).

#### Triangulierung.einfuegen

```python
def einfuegen(self, p: Punkt) -> int
```

Fügt `p` ein und gibt seine Nummer – die eines gleichen Punkts, wenn es ihn schon gibt.

#### Triangulierung._suche

```python
def _suche(self, p: Punkt) -> int
```

Das Dreieck, in dem `p` liegt – oder auf dessen Rand: ein Weg vom zuletzt gebauten aus.

#### Triangulierung._loch

```python
def _loch(self, t: int, p: Punkt) -> Set[int]
```

Die Dreiecke, in deren Umkreis `p` liegt – zusammenhängend, von `t` aus.

#### Triangulierung._rand

```python
def _rand(self, loch: Set[int], p: Punkt) -> List[Tuple[int, int, int]]
```

Der Rand des Lochs als Kanten `(b, c, aussen)`, jede links von `p`
gesehen – liegt `p` auf einer oder knapp daneben, kommt das Dreieck
dahinter ins Loch, und der Rand wird neu gesucht.

#### Triangulierung._umhaengen

```python
def _umhaengen(self, aussen: int, b: int, c: int, j: int) -> None
```

Im Dreieck `aussen` zeigt die Kante `c → b` nun auf `j`.

#### Triangulierung.dreiecke

```python
def dreiecke(self) -> List[Tuple[int, int, int]]
```

Die Dreiecke ohne die an den Ecken des Dreiecks um alles, je im Gegenuhrzeigersinn.

#### Triangulierung.kanten

```python
def kanten(self) -> Set[Tuple[int, int]]
```

Jede Kante einmal, als `(kleinere, grössere Nummer)`.

#### Triangulierung.gefunden

```python
def gefunden(self, p: Punkt) -> Optional[int]
```

Die Nummer eines Punkts, der mit `p` zusammenfällt – `None`, wenn keiner.


## Konstanten

- `UMFANG = 1000.0` – Wie gross das Dreieck um alle Punkte ist, gemessen an ihrer Ausdehnung.

## Gebraucht von

- [[opencivil.decke.fem.netz]]
