---
erzeugt: f3448508f3f9
art: modul
tags: [modul]
---
> [!abstract] opencivil/konsole/zeichnen.py
> Diagramme aus der App «Python», ohne matplotlib.
> Paket [[opencivil.konsole]] · [Quelltext](../../opencivil/konsole/zeichnen.py)

## VERANTWORTUNG

Die gängigen Befehle von `matplotlib.pyplot`, unter denselben Namen:
`plot`, `scatter`, `bar`, `xlabel`, `ylabel`, `title`,
`legend`, `grid`, `xlim`, `ylim`, `axhline`, `axvline`,
`figure`, `show`. Wer matplotlib kennt, schreibt:

```python
import zeichnen as plt
plt.plot([0, 1, 2], [0, 1, 4], "o-", label="y = x²")
plt.xlabel("x")
plt.legend()
plt.show()
```


## GEZEICHNET WIRD NICHT HIER

Ein Bild ist eine Beschreibung -- Reihen, Achsen, Titel --, und die
Oberfläche zeichnet sie wie ihre übrigen Diagramme (`web/js/zeichnen.js`).
Darum braucht es keinen Download und kaum Speicher; matplotlib brächte rund
10 MB mit (Benutzer, 2026-10-15: lieber ein eigenes Modul).


## WOHIN EIN BILD GEHT

`show()` gibt das Bild an die Sitzung, die es zwischen die Ausgaben
stellt ([[opencivil.konsole.sitzung]]); was am Ende eines Laufs noch
offen ist, kommt von selbst dazu, wie in einem Notizbuch. Ausserhalb einer
Sitzung sammelt das Modul die Bilder, bis jemand [[opencivil.konsole.zeichnen#abholen|abholen]] ruft.

## Inhalt

### Figur

```python
class Figur
```

Ein Bild im Entstehen: Reihen, Hilfslinien, Beschriftung.

#### Figur.leer

```python
@property
def leer(self) -> bool
```

#### Figur.als_dict

```python
def als_dict(self) -> Dict[str, Any]
```

### figure

```python
def figure(*_args: Any, **_kwargs: Any) -> None
```

Beginnt ein neues Bild; ein angefangenes kommt vorher heraus. Grösse und Nummer zählen nicht.

### show

```python
def show(*_args: Any, **_kwargs: Any) -> None
```

Gibt das Bild heraus und beginnt ein neues -- ein leeres bleibt ungezeigt.

### clf

```python
def clf() -> None
```

Verwirft das angefangene Bild.

### abholen

```python
def abholen() -> List[Dict[str, Any]]
```

Die Bilder, die ausserhalb einer Sitzung herauskamen -- und dazu das offene.

### savefig

```python
def savefig(*_args: Any, **_kwargs: Any) -> None
```

### plot

```python
def plot(*args: Any, label: Optional[str]=None, color: Optional[str]=None, c: Optional[str]=None, linestyle: Optional[str]=None, ls: Optional[str]=None, marker: Optional[str]=None, linewidth: Optional[float]=None, lw: Optional[float]=None, markersize: Optional[float]=None, ms: Optional[float]=None, alpha: Optional[float]=None) -> None
```

Eine Linie: `plot(y)`, `plot(x, y)` oder `plot(x, y, "r--o")` --
mehrere Paare hintereinander geben mehrere Linien.

### scatter

```python
def scatter(x: Any, y: Any, s: Optional[float]=None, c: Optional[str]=None, *, label: Optional[str]=None, color: Optional[str]=None, marker: Optional[str]=None, alpha: Optional[float]=None) -> None
```

Punkte: `scatter(x, y)` -- `s` ist die Fläche der Marke wie bei matplotlib.

### bar

```python
def bar(x: Any, height: Any, width: float=0.8, *, label: Optional[str]=None, color: Optional[str]=None, alpha: Optional[float]=None) -> None
```

Balken: `bar(["A", "B"], [3, 5])` -- die Stellen dürfen auch Namen sein.

### axhline

```python
def axhline(y: float=0.0, *, color: Optional[str]=None, linestyle: Optional[str]=None, ls: Optional[str]=None) -> None
```

Eine waagrechte Linie über das ganze Bild.

### axvline

```python
def axvline(x: float=0.0, *, color: Optional[str]=None, linestyle: Optional[str]=None, ls: Optional[str]=None) -> None
```

Eine senkrechte Linie über das ganze Bild.

### title

```python
def title(text: str, **_kwargs: Any) -> None
```

### xlabel

```python
def xlabel(text: str, **_kwargs: Any) -> None
```

### ylabel

```python
def ylabel(text: str, **_kwargs: Any) -> None
```

### legend

```python
def legend(*_args: Any, **_kwargs: Any) -> None
```

Zeigt die Legende -- mit den Namen aus `label=`.

### grid

```python
def grid(sichtbar: bool=True, **_kwargs: Any) -> None
```

### xlim

```python
def xlim(*grenzen: Any, left: Any=None, right: Any=None) -> None
```

`xlim(0, 10)` oder `xlim((0, 10))` -- eine Grenze `None` bleibt frei.

### ylim

```python
def ylim(*grenzen: Any, bottom: Any=None, top: Any=None) -> None
```

### _paare

```python
def _paare(args: Sequence[Any], befehl: str) -> Iterable[tuple]
```

Die Argumente von `plot` in Paare (x, y, Format) zerlegt.

### _format

```python
def _format(fmt: str) -> tuple
```

`"r--o"` → (rot, `--`, `o`) -- wie die Formatkürzel von matplotlib.

### _als_kategorien

```python
def _als_kategorien(werte: List[Any], befehl: str) -> List[float]
```

Namen statt Zahlen: jede Kategorie bekommt ihre Stelle, alle Reihen dieselbe.

### _folge

```python
def _folge(werte: Any, befehl: str, name: str) -> List[Any]
```

Eine Liste aus dem, was kommt: Liste, Tupel, range, numpy, pandas, Generator.

### _zahl

```python
def _zahl(v: Any, befehl: str, name: str) -> float
```

Eine endliche Zahl -- unendlich liesse sich nicht zeichnen.

### _angegeben

```python
def _angegeben(*werte: Any) -> Any
```

Der erste angegebene Wert -- `0` ist angegeben, `None` nicht (`lw=0` ist keine Linie).

### _eigenschaft

```python
def _eigenschaft(v: Any, befehl: str, name: str, *, ab: Optional[float]=None, ueber: Optional[float]=None, bis: Optional[float]=None) -> Optional[float]
```

Breite, Grösse oder Deckung: eine endliche Zahl in ihrem Bereich, `None`
heisst nicht angegeben. Bis 2026-10-17 gingen diese ungeprüft durch, und
ein `nan` hielt die Konsole an ([[opencivil.web.umschlag]]).

### _name

```python
def _name(label: Any) -> Optional[str]
```

Der Name einer Reihe für die Legende -- als Text, wie matplotlib ihn schreibt.

### _zahl_oder_luecke

```python
def _zahl_oder_luecke(v: Any, befehl: str, name: str) -> Optional[float]
```

Eine Zahl -- `None`, `nan` und unendlich werden eine Lücke, wie bei matplotlib.

### _farbe

```python
def _farbe(wert: Any) -> Optional[str]
```

Eine Farbe für SVG: Name oder `#rrggbb` bleiben, `(r, g, b)` in Anteilen wird `rgb(…)`.


## Konstanten

- `FARBKUERZEL = {'b': 'blue', 'g': 'green', 'r': 'red', 'c': '#00bfbf', 'm': '#bf00bf…` – Die Farben der Formatkürzel von matplotlib, als Farben für SVG: `"r--"` ist rot gestrichelt. Dieselben Töne wie dort.
- `STRICHE = {'-': '-', '--': '--', ':': ':', '-.': '-.', 'solid': '-', 'dashed': …` – Linienarten, wie matplotlib sie schreibt -- auch ausgeschrieben.
- `MARKEN = ('o', 's', '^', '.', 'x', '+', 'D')` – Marken: Kreis, Quadrat, Dreieck, Punkt, Kreuz, Plus, Raute.
- `_ziel = None` – Wohin ein fertiges Bild geht -- die Sitzung setzt es für die Dauer eines Laufs.

## Gebraucht von

- [[opencivil.konsole.sitzung]]
