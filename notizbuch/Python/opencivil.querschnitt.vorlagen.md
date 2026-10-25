---
erzeugt: 50a1b7493f23
art: modul
tags: [modul]
---
> [!abstract] opencivil/querschnitt/vorlagen.py
> Querschnitte zum Anfangen.
> Paket [[opencivil.querschnitt]] · [Quelltext](../../opencivil/querschnitt/vorlagen.py)

## VERANTWORTUNG

Vier Vorlagen -- Rechteck, T-Balken, Hohlkasten, Kreis. Jede kennt ihre
Masse samt Vorgabe und baut daraus [[opencivil.querschnitt.vorlagen#Teile|Teile]] in mm, den Ursprung unten
links: die Polygone, auf Wunsch die Bewehrung und die Schubwaende, und fuer
die Skizze im Zeichenfenster die Masslinien.

Die Vorlagen stehen nur hier. [[opencivil.projekt.querschnittsanalyse#QuerschnittsanalyseEintrag.neu|QuerschnittsanalyseEintrag.neu]] baut
seine frische Analyse aus dem Rechteck, und die Oberflaeche fragt nach ihnen:
`vorlage` fuer die Skizze, waehrend man tippt, `vorlage_einsetzen` zum
Einsetzen. Vorher stand das Rechteck zweimal da, in Python und in JS.

Was eine Vorlage nicht sagt, kommt aus den Vorgaben der Eintraege -- der
Stahl, die Buegel einer Schubwand, ihre Schnitte. Eine Vorlage ist ein
Anfang, kein Entwurf.


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

Ein Mass einer Vorlage, in mm.

- `schluessel: str`
- `beschriftung: str`
- `vorgabe: float`

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
def kreispunkte(mitte: Punkt, radius: float) -> List[Punkt]
```

Ein Kreis als Vieleck mit [[opencivil.querschnitt.vorlagen#Konstanten|KREISECKEN]] Ecken, auf Tausendstel gerundet.

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
def bauen(self, masse: Optional[Mapping[str, float]]=None, randabstand: float=50.0, bewehrung: bool=True, schubwaende: bool=True) -> Teile
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
- `VORLAGEN = (Vorlage('rechteck', 'Rechteck', (Mass('b', 'Breite b', 300.0), Mass(…`

## Gebraucht von

- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.stabwerk.querschnitte]]
- [[opencivil.web.api]]
- [[opencivil.web.dienst]]
