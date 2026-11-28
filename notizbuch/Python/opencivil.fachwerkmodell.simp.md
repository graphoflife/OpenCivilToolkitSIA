---
erzeugt: 840c4fc187e2
art: modul
tags: [modul]
---
> [!abstract] opencivil/fachwerkmodell/simp.py
> das Material einer Scheibe zur steifsten Form verteilt.
> Paket [[opencivil.fachwerkmodell]] · [Quelltext](../../opencivil/fachwerkmodell/simp.py)

## VERANTWORTUNG

Das Verfahren SIMP nach Andreassen, Clausen, Schevenels, Lazarov &
Sigmund (2011): die Scheibe in quadratische Elemente der Netzweite h
geteilt ([[opencivil.fachwerkmodell.simp#netz|netz]]), je Element eine Dichte zwischen null und eins.
Ein Schritt ([[opencivil.fachwerkmodell.simp#schritt|schritt]]) rechnet die Scheibe mit diesen Dichten
linear elastisch, fragt, wie stark jedes Element die Nachgiebigkeit
senkte, und verteilt das Material neu – so viel, wie der Volumenanteil
erlaubt. Schritt um Schritt wächst so die steifste Form.


## DAS ELEMENT

Vier Knoten, bilinear, im ebenen Spannungszustand, Dicke eins
([[opencivil.fachwerkmodell.simp#elementsteifigkeit|elementsteifigkeit]]). Ohne Material hat es noch E_min = 10⁻⁹ der
vollen Steifigkeit, damit nichts frei schwebt; dazwischen gilt
`E = E_min + ρ^p · (1 − E_min)` mit p = 3 – halbe Dichten lohnen sich
so nicht, und die Form wird klar (Gl. (1) der Quelle).


## DER FILTER

Ein Element sieht nicht seine eigene Dichte, sondern ihr Mittel über die
Nachbarn bis 1.5 h, gewichtet mit `r_min − Abstand` (Gl. (8) und (9));
so bleiben keine Schachbretter stehen, und die Form hängt kaum am Netz.
Die Ableitungen gehen über den Filter zurück auf die Dichten (Gl. (10)).
Die Änderung je Schritt ist höchstens 0.2, der Multiplikator der
Bedingung für das Volumen kommt aus einer Halbierung (Gl. (3) und (4)).


## KEIN MATERIAL

E und ν sind keine Eigenschaften des Bauteils: die Form hängt nur an
ihrem Verhältnis. ν = 0.2 wie für Beton (SIA 262:2025, 3.1.2.3.5), E = 1.
Die Lasten zählen bezogen auf die grösste.


## DIE GRENZE

Mehr als [[opencivil.fachwerkmodell.simp#Konstanten|HOECHSTENS_ELEMENTE]] Elemente rechnet das Werkzeug nicht
– auf der Seite dauerte jeder Schritt gegen zwei Sekunden (nach Vorgabe,
nicht nachgeschlagen).

## Inhalt

### NetzFehler

```python
class NetzFehler(Exception)
```

Das Netz lässt sich so nicht rechnen: der Satz sagt, warum und was zu tun ist.

### Netz

```python
@dataclass(frozen=True)
class Netz
```

Die Elemente einer Scheibe, ihre Freiheitsgrade, die Last und der Filter.

- `modell: Modell`
- `weite: float`
- `ursprung: Punkt` – Die Ecke unten links des Rechtecks um die Scheiben, in m.
- `spalten: int`
- `zeilen: int` – Wie viele Elemente das Rechteck in x und in y fasst.
- `elemente: Tuple[Tuple[int, int], ...]` – Je Element sein Platz `(i, j)` im Rechteck – nur die im Material, Zeile um Zeile von unten.
- `freiheitsgrade: Tuple[Tuple[int, ...], ...]` – Je Element seine acht Unbekannten, je Ecke x und y – `-1`, wo ein Lager hält.
- `unbekannte: int`
- `last: Tuple[float, ...]` – Je Unbekannte die Last, bezogen auf die grösste.
- `filter: Tuple[Tuple[Tuple[int, float], ...], ...]` – Je Element die Nachbarn im Filter und ihr Gewicht – die Gewichte zusammen eins.
- `zurueck: Tuple[Tuple[Tuple[int, float], ...], ...]` – Je Element, mit welchem Gewicht es in die gefilterte Dichte seiner Nachbarn eingeht.
- `anteil: Tuple[float, ...]` – Je Element, wie viel es zum Volumen der gefilterten Dichten gibt.
- `profil: Tuple[int, ...]` – Je Unbekannte die erste Spalte ihrer Zeile in der Steifigkeitsmatrix.
- `eintraege: Tuple[Tuple[Tuple[int, int, float], ...], ...]` – Je Element, wohin seine Steifigkeit geht: Zeile, Platz in der Zeile, Wert bei voller Dichte.

#### Netz.mitte

```python
def mitte(self, platz: Tuple[int, int]) -> Punkt
```

Die Mitte des Elements am Platz `(i, j)`, in m.

### Schritt

```python
@dataclass(frozen=True)
class Schritt
```

Was ein Schritt gibt.

- `dichte: Tuple[float, ...]` – Die neuen Dichten, je Element – die der Optimierung, noch nicht gefiltert.
- `aenderung: float` – Wie stark sich die Dichten höchstens änderten.
- `nachgiebigkeit: float` – `fᵀ · u` mit den Dichten vor dem Schritt, die Last bezogen auf die grösste.

### elementsteifigkeit

```python
def elementsteifigkeit(nu: float=NU) -> Tuple[Tuple[float, ...], ...]
```

Die Steifigkeit eines quadratischen Elements mit E = 1 und der Dicke
eins, 8 × 8, die Ecken unten links, unten rechts, oben rechts, oben
links, je x und y. Aus vier Punkten nach Gauss – genau für das
bilineare Element; quadratisch hängt sie nicht an seiner Grösse.

### netz

```python
def netz(modell: Modell, weite: float) -> Netz
```

Das Netz der Scheibe mit der Netzweite `weite` in m: je Quadrat des
Rasters ein Element, wenn seine Mitte im Material liegt. Ein Lager und
eine Last gehen an die nächste Ecke eines Elements. Das Modell ist
geprüft. Wirft [[opencivil.fachwerkmodell.simp#NetzFehler|NetzFehler]], wenn es zu viele Elemente wären.

### raster

```python
def raster(modell: Modell, weite: float) -> Tuple[Punkt, int, int]
```

Das Raster der Elemente: die Ecke unten links des Rechtecks um die
Scheiben, in m, und wie viele Felder der Weite `weite` es in x und in
y fasst.

### _naechster

```python
def _naechster(knoten, ort, p: Punkt)
```

Die Ecke eines Elements, die `p` am nächsten liegt – bei gleichem Abstand die erste.

### _zu_viele

```python
def _zu_viele(modell: Modell, weite: float, anzahl: str) -> str
```

Der Satz, wenn das Netz zu fein ist – mit einer Netzweite, die passt, auf 1 cm genau.

### _filter

```python
def _filter(elemente: Sequence[Tuple[int, int]], radius: float)
```

Je Element die Nachbarn bis `radius` Netzweiten mit ihren Gewichten – siehe Dateikopf.

### gefiltert

```python
def gefiltert(n: Netz, x: Sequence[float]) -> List[float]
```

Die Dichten, die die Elemente sehen: je das gewichtete Mittel über die Nachbarn.

### schritt

```python
def schritt(n: Netz, x: Sequence[float], volumen: float) -> Schritt
```

Ein Schritt der Optimierung (Dateikopf): die Scheibe mit den Dichten
`x` gerechnet, das Material nach Optimality Criteria neu verteilt.
Wirft [[opencivil.fachwerkmodell.simp#NetzFehler|NetzFehler]], wenn ein Teil der Scheibe an keinem Lager hängt.


## Konstanten

- `QUELLE = 'Andreassen et al. (2011)'` – Wo das Verfahren nachzulesen ist.
- `HOECHSTENS_ELEMENTE = 2500` – Wie viele Elemente das Netz höchstens hat – nach Vorgabe, nicht nachgeschlagen.
- `E_MIN = 1e-09` – Die Steifigkeit eines Elements ohne Material, bezogen auf die volle – wie in der Quelle.
- `P = 3.0` – Der Exponent, mit dem die Dichte in die Steifigkeit eingeht – wie in den Beispielen der Quelle.
- `NU = 0.2` – Die Querdehnzahl – wie für Beton; die Quelle nimmt 0.3 (nach Vorgabe, nicht nachgeschlagen).
- `FILTER = 1.5` – Der Radius des Filters, in Netzweiten – wie im ersten Beispiel der Quelle.
- `BEWEGUNG = 0.2` – Um wie viel sich eine Dichte je Schritt höchstens ändert – wie in der Quelle.
- `KE = elementsteifigkeit()` – Die Steifigkeit des vollen Elements ([[opencivil.fachwerkmodell.simp#elementsteifigkeit|elementsteifigkeit]]).

## Braucht

- [[opencivil.decke.geometrie]]
- [[opencivil.fachwerkmodell.modell]]
- [[opencivil.stabwerk.matrix]]

## Gebraucht von

- [[opencivil.fachwerkmodell.form]]
- [[opencivil.fachwerkmodell.herleitung]]
- [[opencivil.fachwerkmodell.skelett]]
- [[opencivil.fachwerkmodell.verfahren]]
- [[opencivil.web.fachwerkdaten]]
