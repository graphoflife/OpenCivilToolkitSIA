---
erzeugt: 703c422bbb3f
art: modul
tags: [modul]
---
> [!abstract] opencivil/querschnitt/vorlagen.py
> Querschnitte zum Anfangen.
> Paket [[opencivil.querschnitt]] · [Quelltext](../../opencivil/querschnitt/vorlagen.py)

## VERANTWORTUNG

Vier Vorlagen -- Rechteck, T-Balken, Hohlkasten, Kreis. Jede kennt ihre
Masse samt Vorgabe -- der Kreis auch, wie viele Staebe er hat -- und baut
daraus [[opencivil.querschnitt.vorlagen#Teile|Teile]] in mm, den Ursprung unten links: die Polygone, auf Wunsch die Bewehrung und die Schubwaende, und fuer
die Skizze im Zeichenfenster die Masslinien.

Die Vorlagen stehen nur hier. [[opencivil.projekt.querschnittsanalyse#QuerschnittsanalyseEintrag.neu|QuerschnittsanalyseEintrag.neu]] baut
seine frische Analyse aus dem Rechteck, und die Oberflaeche fragt nach ihnen:
`vorlage` fuer die Skizze, waehrend man tippt, `vorlage_einsetzen` zum
Einsetzen. Vorher stand das Rechteck zweimal da, in Python und in JS.

Was eine Vorlage nicht sagt, kommt aus den Vorgaben der Eintraege -- der
Stahl, die Buegel einer Schubwand, ihre Schnitte. Eine Vorlage ist ein
Anfang, kein Entwurf.


## DAS MASS

Ein [[opencivil.querschnitt.vorlagen#Mass|Mass]] steht fuer die Vorlagen hier und die der Stabquerschnitte
([[opencivil.stabwerk.querschnitte]]). Seine Grenze ist ein
[[opencivil.core.bereich#Bereich|Bereich]] wie die eines Feldes: derselbe
Satz, dieselbe Angabe fuer die Maske. Bis 2026-11-20 hatte jede Seite ihre
eigene Klasse, ihren eigenen Satz und im Fenster ihren eigenen Mindestwert --
1 hier, 0 beim Stab.


## DIE UMRISSE

Rechteck, T und Kreis zeichnet auch das Balkensystem fuer seine
Stabquerschnitte ([[opencivil.stabwerk.querschnitte]]). Ihre Umrisse und
was an einem T nicht geht, stehen darum hier, einmal fuer beide
([[opencivil.querschnitt.vorlagen#rechteckpunkte|rechteckpunkte]], [[opencivil.querschnitt.vorlagen#t_punkte|t_punkte]], [[opencivil.querschnitt.vorlagen#t_pruefen|t_pruefen]],
[[opencivil.querschnitt.vorlagen#kreispunkte|kreispunkte]]). Bis 2026-10-25 standen sie in beiden Katalogen, und
ein Steg so breit wie der Flansch galt im einen als T, im anderen nicht.

## Inhalt

### Mass

```python
@dataclass(frozen=True)
class Mass
```

Ein Mass einer Vorlage: eine Laenge in mm, wo `einheit` nichts anderes
sagt -- oder, `ganzzahlig`, eine Anzahl, wie die der Staebe im Kreis.
Jedes ist groesser als null; was die Masse untereinander verlangen,
prueft die Vorlage.

- `schluessel: str`
- `symbol: str` – Wie es in der Skizze heisst -- leer, wo es dort nicht steht.
- `beschriftung: str`
- `vorgabe: float`
- `einheit: Einheit = MM`
- `ganzzahlig: bool = False`

#### Mass.heisst

```python
@property
def heisst(self) -> str
```

Wie es an der Maske und in einer Meldung heisst: «Breite b».

#### Mass.bereich

```python
@property
def bereich(self) -> Bereich
```

#### Mass.schritt

```python
@property
def schritt(self) -> float
```

Um wie viel ein Pfeil am Feld den Wert aendert.

#### Mass.grund

```python
def grund(self, wert: float) -> str
```

Was an `wert` nicht geht, als Satz mit Punkt -- leer, wenn er geht.

#### Mass.als_dict

```python
def als_dict(self) -> Dict[str, Any]
```

Fuer den Katalog: wie es heisst, seine Vorgabe, der Schritt der
Pfeile und, was die Maske wie bei einem Feld braucht (`angabe`:
Einheit, Grenze, Satz, bei einer Anzahl `ganz`).

### Teile

```python
@dataclass
class Teile
```

Was eine Vorlage baut -- in mm, der Ursprung unten links.

- `polygone: List[dict] = field(default_factory=list)` – Je Polygon `punkte` und `aussparung`.
- `staebe: List[dict] = field(default_factory=list)` – Je Stab `lage` und `durchmesser`.
- `stablinien: List[dict] = field(default_factory=list)` – Je Linie `von`, `bis` und die Felder, die von der Vorgabe abweichen.
- `schubwaende: List[dict] = field(default_factory=list)` – Je Wand `von`, `bis` und `dicke`.
- `masslinien: List[dict] = field(default_factory=list)` – Nur fuer die Skizze: `von`, `bis`, `text` und `seite` ('unten', 'oben', 'links', 'rechts') -- wohin sie neben dem Bauteil steht.

#### Teile.als_dict

```python
def als_dict(self) -> dict
```

### kreispunkte

```python
def kreispunkte(mitte: Punkt, radius: float, ecken: int=KREISECKEN) -> List[Punkt]
```

`ecken` Punkte, gleich verteilt auf einem Kreis, der erste rechts, auf
Tausendstel gerundet: die Ecken eines Kreises als Vieleck -- oder die
Staebe darin.

### rechteckpunkte

```python
def rechteckpunkte(b: float, h: float, y: float=0.0, z: float=0.0) -> List[Punkt]
```

Ein Rechteck `b` breit und `h` hoch, die Ecke unten links in `(y, z)`.

### t_punkte

```python
def t_punkte(b: float, h: float, b_w: float, h_f: float) -> List[Punkt]
```

Ein T, der Flansch oben und mittig ueber dem Steg -- der Ursprung unten links.

### t_pruefen

```python
def t_pruefen(b: float, h: float, b_w: float, h_f: float) -> Optional[str]
```

Was an einem T nicht geht -- `None`, wenn alles geht. Ein Steg so breit
wie der Flansch gaebe ein Rechteck mit doppelten Ecken: dafuer gibt es das
Rechteck.

### Vorlage

```python
@dataclass(frozen=True)
class Vorlage
```

Eine Vorlage: ihre Masse und wie sie daraus Teile baut.

- `schluessel: str`
- `name: str`
- `masse: Tuple[Mass, ...]`
- `teile: Callable[[Mapping[str, float], float], Teile]`
- `pruefen: Callable[[Mapping[str, float], float], Optional[str]]`
- `hat_waende: bool = True`

#### Vorlage.bauen

```python
def bauen(self, masse: Optional[Mapping[str, float]]=None, randabstand: float=RANDABSTAND.vorgabe, bewehrung: bool=True, schubwaende: bool=True) -> Teile
```

Die Teile zu diesen Massen -- was fehlt, nach Vorgabe. `randabstand`
ist der Achsabstand der Staebe vom Rand. Ohne `bewehrung` keine
Staebe und Linien, ohne `schubwaende` keine Waende. Passen die
Masse nicht zueinander, ein `ValueError` mit dem Grund.

### vorlage

```python
def vorlage(schluessel: str) -> Vorlage
```

Die Vorlage zu einem Schluessel -- `ValueError`, wenn es sie nicht gibt.


## Konstanten

- `KREISECKEN = 48` – Ecken eines Kreises. Sie liegen auf dem Kreis; was das an Flaeche kostet, rechnet die Geometrie wie bei jedem anderen Polygon.
- `RANDABSTAND = Mass('randabstand', '', 'Achsabstand', 50.0)` – Der Achsabstand der Staebe vom Rand -- ein Mass jeder Vorlage hier. Auch die Schubwaende enden auf seiner Hoehe.
- `VORLAGEN = (Vorlage('rechteck', 'Rechteck', (Mass('b', 'b', 'Breite', 300.0), Ma…`

## Braucht

- [[opencivil.core.bereich]]
- [[opencivil.core.einheiten]]

## Gebraucht von

- [[opencivil.pfahl.innen]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.stabwerk.profilformen]]
- [[opencivil.stabwerk.querschnitte]]
- [[opencivil.web.api]]
- [[opencivil.web.dienst]]
