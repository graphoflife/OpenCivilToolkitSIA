---
erzeugt: 15a88dd6f5fe
art: modul
tags: [modul]
---
> [!abstract] opencivil/decke/feld.py
> die Schnittkräfte der Platte an einer Stelle.
> Paket [[opencivil.decke]] · [Quelltext](../../opencivil/decke/feld.py)

## VERANTWORTUNG

Aus den Trägern eines Falls, was an einer Stelle der Platte wirkt: die
Momente `m_x`, `m_y`, `m_xy` je Meter, die Querkräfte `v_x`,
`v_y` je Meter und daraus die erforderlichen Biegewiderstände. Dazu die
Lastverteilelemente über Stützen und unter Einzellasten.


## WO BILDER UND BERICHT HINSEHEN

An den Proben eines Falls ([[opencivil.decke.feld#proben|proben]]): dem Schwerpunkt jeder Zelle der
Bilder ([[opencivil.decke.feld#zellen_von|zellen_von]]) und den Stellen, an denen ein Träger springt
oder seine grössten Werte hat ([[opencivil.decke.feld#stellen|stellen]]). Dort sucht [[opencivil.decke.feld#extrem|extrem]]
den grössten und den kleinsten Wert – für das Bild und den Bericht
derselbe. Wie sich die Werte über eine Zelle ändern, sagt
[[opencivil.decke.feld#gefaelle|gefaelle]]; damit verläuft die Farbe im Bild, statt in jeder Zelle
zu stehen (Benutzer, 2026-11-16).


## VOM STREIFEN ZUR PLATTE

Ein Streifen der Breite `b` in Richtung `n` trägt mit dem Moment `M`
und der Querkraft `V`; je Meter sind das `m = M/b` und `v = V/b`, in
seiner Richtung `n`. In den Achsen x, y wird daraus mit dem Winkel `φ`
von `n` gegen x – die Transformation der Stahlbeton II, 7.2 Platten,
Folie 14, rückwärts gelesen, mit `m_n = m` und `m_t = m_nt = 0`:

```
m_x  = m · cos²φ
m_y  = m · sin²φ
m_xy = m · sinφ · cosφ
```

Ein Streifen in x trägt also nur `m_x`, einer in y nur `m_y`; ein
schiefer Streifen trägt mit `m_η` auch ein Drillmoment `m_xy`. An einer
Stelle zählen alle Streifen, die über sie gehen – je Richtung ein
Feldstreifen und jeder Unterzug, in dessen Fläche sie liegt.


## BIEGEWIDERSTÄNDE

Nach der linearisierten Normalmomenten-Fliessbedingung, `k = k' = 1`
(Folien 9 und 10) – in der Norm SIA 262:2025, 4.3.2.6, (34), als Näherung
für Bewehrung in x und y und nicht zu grosse Drillmomente. Weicht die
Hauptbeanspruchung deutlich von der Bewehrung ab, etwa bei schiefen
Streifen, verlangt 4.3.2.5, das zu beachten:

```
m_x,u  ≥  m_x + |m_xy|      m'_x,u ≥ −m_x + |m_xy|
m_y,u  ≥  m_y + |m_xy|      m'_y,u ≥ −m_y + |m_xy|
```

Was negativ herauskommt, braucht keine Bewehrung: null.


## LASTVERTEILELEMENTE (Folie 38)

Über einer Stütze tragen die Streifen in den Stützenbereich `l_x × l_y`,
als läge dort eine gleichmässige Pressung. Damit die Stützenkraft `Q`
als Punkt hineinpasst, braucht der Bereich zusätzlich:

```
m'_x,u ≥ Q/8 · l_x/l_y          m_x,u ≥ (1/(2π) − 1/8) · Q · l_x/l_y
m'_y,u ≥ Q/8 · l_y/l_x          m_y,u ≥ (1/(2π) − 1/8) · Q · l_y/l_x
```

Unter einer Einzellast gilt dasselbe mit vertauschten Seiten: die
gleichmässige Last ist dort, wo die Streifen sie tragen, und der Punkt,
wo die Last angreift.

## Inhalt

### Schnittkraefte

```python
@dataclass(frozen=True)
class Schnittkraefte
```

An einer Stelle: Momente in Nm/m, Querkräfte in N/m.

- `mx: float = 0.0`
- `my: float = 0.0`
- `mxy: float = 0.0`
- `vx: float = 0.0`
- `vy: float = 0.0`

#### Schnittkraefte.v0

```python
@property
def v0(self) -> float
```

Die Hauptquerkraft `√(v_x² + v_y²)`.

#### Schnittkraefte.groesse

```python
def groesse(self, name: str) -> float
```

Die Grösse `name` aus [[opencivil.decke.feld#Konstanten|GROESSEN]].

### Widerstaende

```python
@dataclass(frozen=True)
class Widerstaende
```

Die erforderlichen Biegewiderstände in Nm/m: unten (positiv) und oben (gestrichen).

- `mxu: float`
- `myu: float`
- `mxu_oben: float`
- `myu_oben: float`

### in_xy

```python
def in_xy(m: float, v: float, n: Punkt) -> Schnittkraefte
```

Moment und Querkraft je Meter eines Streifens in Richtung `n` – in den Achsen x, y.

### an_stelle

```python
def an_stelle(ergebnis: Ergebnis, fall: Fallergebnis, p: Punkt) -> Schnittkraefte
```

Die Schnittkräfte an der Stelle `p`: je Richtung der Feldstreifen, in
dem sie liegt, und jeder Unterzug, in dessen Fläche sie liegt. An der
Grenze zweier Feldstreifen zählt der mit dem grösseren `τ`.

### widerstaende

```python
def widerstaende(k: Schnittkraefte) -> Widerstaende
```

Die erforderlichen Biegewiderstände nach der linearisierten Fliessbedingung, `k = 1`.

### zellen_von

```python
def zellen_von(ergebnis: Ergebnis) -> List[List[Punkt]]
```

Die Zellen der Bilder: je Gruppe die Feldstreifen ihrer beiden
Richtungen, die breiten geteilt ([[opencivil.decke.feld#Konstanten|ZELLEN]]), gekreuzt und mit den
konvexen Stücken ihrer Platten geschnitten. So liegt jede Zelle in
einem Streifen jeder Richtung, und ihr Wert gilt für sie ganz.

### _baender

```python
def _baender(streifen: Sequence[Streifen], weite: float) -> List[Tuple[float, float]]
```

Die Feldstreifen einer Richtung quer in Bänder, keines breiter als `weite`.

### stellen

```python
def stellen(ergebnis: Ergebnis, fall: Fallergebnis) -> List[Punkt]
```

Wo ein Träger des Falls springt oder ein Extremum hat, auf der Mittellinie
seines Streifens: an den Enden jedes Stücks – knapp innerhalb
([[opencivil.decke.feld#Konstanten|INNEN]]) – und wo die Querkraft oder die Last null wird. Wo nur
ein Streifen trägt, liegen dort die grössten und kleinsten m und v genau;
wo sich zwei überlagern, in der Nähe.

### proben

```python
def proben(ergebnis: Ergebnis, fall: Fallergebnis, zellen: Sequence[Sequence[Punkt]]) -> List[Probe]
```

Wo Bilder und Bericht die Platte im Fall ansehen, je mit den
Schnittkräften dort: zuerst die Schwerpunkte der `zellen`
([[opencivil.decke.feld#zellen_von|zellen_von]]), in ihrer Folge, dann die Stellen
([[opencivil.decke.feld#stellen|stellen]]), die in einer Platte liegen.

### gefaelle

```python
def gefaelle(ergebnis: Ergebnis, fall: Fallergebnis, zelle: Sequence[Punkt], probe: Probe) -> Dict[str, Tuple[float, float]]
```

Wie sich jede Grösse ([[opencivil.decke.feld#Konstanten|GROESSEN]]) über eine Zelle ändert, je
`(∂/∂x, ∂/∂y)` in ihrer Einheit je m: das Gefälle der Ebene durch den
Wert der `probe` in ihrem Schwerpunkt, die die Werte an ihren Ecken –
knapp innen, [[opencivil.decke.feld#Konstanten|ECKE_INNEN]] – nach den kleinsten Quadraten am
besten trifft. Nur für das Bild.

In einer Zelle trägt je Richtung ein Streifen, und ein Unterzug deckt
sie ganz oder gar nicht ([[opencivil.decke.feld#zellen_von|zellen_von]]): ihre Werte folgen dort je
einem Polynom längs des Streifens. Auf einem Rechteck hat die Ebene
dann das Gefälle der Sehne, bei einer Parabel gleich der Ableitung im
Schwerpunkt, und Nachbarn im selben Streifen treffen sich an der
gemeinsamen Kante bis auf die Krümmung über eine Zelle.

### _nach_innen

```python
def _nach_innen(p: Punkt, mitte: Punkt) -> Punkt
```

`p`, um [[opencivil.decke.feld#Konstanten|ECKE_INNEN]] zur `mitte` gerückt – höchstens um die Hälfte des Wegs.

### extrem

```python
def extrem(proben: Sequence[Probe], aus: Callable[[Schnittkraefte], float]) -> Tuple[Tuple[Punkt, float], Tuple[Punkt, float]]
```

`((Ort, kleinster), (Ort, grösster))` dessen, was `aus` aus den
Schnittkräften liest – bei gleichen Werten die vordere Probe.

### Lastverteilelement

```python
@dataclass(frozen=True)
class Lastverteilelement
```

Ein Lastverteilelement `lx × ly` um `ort`: was es zusätzlich an
Biegewiderstand braucht, in Nm/m – `oben` für negative, `unten` für
positive Momente, je in x und y.

- `name: str`
- `art: str` – `stuetze` oder `einzellast`.
- `ort: Punkt`
- `lx: float`
- `ly: float`
- `Q: float` – Die Kraft, die es bündelt, in N: die Stützenkraft nach oben, die Einzellast nach unten positiv.

#### Lastverteilelement.ecken

```python
@property
def ecken(self) -> List[Punkt]
```

#### Lastverteilelement.zusatz

```python
def zusatz(self) -> Tuple[Tuple[float, float], Tuple[float, float]]
```

`((oben_x, unten_x), (oben_y, unten_y))`: das zusätzliche negative
Moment (≤ 0) und das zusätzliche positive (≥ 0), je Richtung.

### lastverteilelemente

```python
def lastverteilelemente(ergebnis: Ergebnis, fall: Fallergebnis) -> List[Lastverteilelement]
```

Je Stütze mit Kraft und je Einzellast des Falls ein Lastverteilelement.

### _einzellasten

```python
def _einzellasten(ergebnis: Ergebnis, name: str) -> Sequence[Tuple[Punktlast, float]]
```

Die Einzellasten eines Lastfalls oder einer Kombination, mit ihrem Beiwert.


## Konstanten

- `POSITIV_JE_LAST = 1.0 / (2.0 * math.pi) - 1.0 / 8.0` – Der positive Widerstand je Last eins im Lastverteilelement: `1/(2π) − 1/8`, auf der Folie 0.034.
- `GROESSEN = {'m_x': 'mx', 'm_y': 'my', 'm_xy': 'mxy', 'v_x': 'vx', 'v_y': 'vy', '…` – Was ein Bild der Platte zeigen kann: je Name das Feld von [[opencivil.decke.feld#Schnittkraefte|Schnittkraefte]].
- `INNEN = 1e-06` – So weit innerhalb eines Stücks liegt die Stelle an seinem Ende, in m: weiter als [[opencivil.decke.traeger#Konstanten|GLEICH]], so dass links und rechts eines Sprungs beide zählen.
- `ZELLEN = 24` – So viele Zellen hat ein Bild über die längere Seite der Decke mindestens – breitere Streifen werden dafür geteilt. Mehr machten die Bilder gross: bei 40 waren es für die Decke des Kolloquiums 4 (9 m, Streifen 0.25 m) 3168 Zellen und 330 kB.
- `ECKE_INNEN = 0.0001` – So weit rückt eine Ecke einer Zelle zu ihrem Schwerpunkt, bevor dort gerechnet wird, in m: weiter als [[opencivil.decke.geometrie#Konstanten|TOLERANZ]], so dass sie in der Zelle liegt und nicht auf dem Rand des Streifens oder Unterzugs daneben.
- `Probe = Tuple[Punkt, 'Schnittkraefte']` – Eine Stelle der Platte mit ihren Schnittkräften.

## Braucht

- [[opencivil.decke.geometrie]]
- [[opencivil.decke.modell]]
- [[opencivil.decke.rechnung]]
- [[opencivil.decke.streifen]]
- [[opencivil.decke.traeger]]
- [[opencivil.stabwerk.verlauf]]

## Gebraucht von

- [[opencivil.decke.herleitung]]
- [[opencivil.decke.schnitt]]
- [[opencivil.projekt.decke]]
- [[opencivil.web.deckendaten]]
