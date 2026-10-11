---
erzeugt: 97a503808e39
art: modul
tags: [modul]
---
> [!abstract] opencivil/querschnitt/geometrie.py
> Ebene Geometrie eines gezeichneten Querschnitts.
> Paket [[opencivil.querschnitt]] · [Quelltext](../../opencivil/querschnitt/geometrie.py)

## VERANTWORTUNG

Alles, was aus der Zeichnung folgt, bevor ein Werkstoff ins Spiel kommt:
Flaeche, Schwerpunkt und Traegheitsmomente eines Polygons, wie Polygone
ineinanderliegen, wo die Staebe einer Stablinie liegen, ob ein Stab ganz im
Beton steckt und wo eine Gerade ein Polygon schneidet.


## WARUM HIER UND NICHT IN DER OBERFLAECHE

Das Zeichenfenster zeigt Stabpositionen, tatsaechliche Teilungen und
Fehlermeldungen. Gerechnet wird das hier; die Oberflaeche zeichnet, was der
Kern sagt. Eine zweite Fassung der Teilungsregel in JavaScript liefe frueher
oder spaeter auseinander.


## EINHEITEN

Keine. Gerechnet wird in der Einheit der Punkte -- in der Beschreibung sind
das Millimeter --, Flaechen kommen im Quadrat dieser Einheit zurueck.
Umgerechnet wird einmal am Rand, dort wo die Fasern entstehen.


## KOORDINATEN

y nach rechts, z nach oben. Ein Polygon ist eine Folge von Ecken, die erste
wird am Ende nicht wiederholt. Ob es links- oder rechtsherum laeuft, ist gleich.


## INEINANDER LIEGEN

Liegt ein Polygon ganz in einem anderen, ersetzt es dieses dort -- so entsteht
eine Aussparung, spaeter ein Stahlprofil im Beton. Beruehren duerfen sich
Polygone, auch entlang einer ganzen Kante. Teilweise ueberlappen duerfen sie
nicht: welches Material dort gilt, waere eine Willkuer.

## Inhalt

### GeometrieFehler

```python
class GeometrieFehler(ValueError)
```

Eine Zeichnung, aus der sich nichts rechnen laesst -- mit dem Grund und
den Elementen, die er betrifft. Das Zeichenfenster faerbt sie ein.

### Flaechenwerte

```python
@dataclass(frozen=True)
class Flaechenwerte
```

Flaeche, Schwerpunkt und Traegheitsmomente, bezogen auf den Schwerpunkt.

`I_y` ist das Moment um die y-Achse, also `∫(z - z_S)² dA`; `I_z`
entsprechend `∫(y - y_S)² dA` und `I_yz = ∫(y - y_S)(z - z_S) dA`.

- `A: float`
- `y_S: float`
- `z_S: float`
- `I_y: float`
- `I_z: float`
- `I_yz: float`

### flaeche

```python
def flaeche(punkte: Sequence[Punkt]) -> float
```

Die Flaeche mit Vorzeichen: positiv, wenn das Polygon linksherum laeuft.

### flaechenwerte

```python
def flaechenwerte(punkte: Sequence[Punkt]) -> Flaechenwerte
```

Die Werte eines einfachen Polygons, nach den Formeln aus dem Satz von Gauss.

Mit `c_i = y_i·z_(i+1) - y_(i+1)·z_i` gilt, bezogen auf den Ursprung:

```
A     = 1/2  · Σ c_i
S_z   = 1/6  · Σ (y_i + y_(i+1)) · c_i          = A·y_S
S_y   = 1/6  · Σ (z_i + z_(i+1)) · c_i          = A·z_S
I_yy  = 1/12 · Σ (z_i² + z_i·z_(i+1) + z_(i+1)²) · c_i
I_zz  = 1/12 · Σ (y_i² + y_i·y_(i+1) + y_(i+1)²) · c_i
I_yz0 = 1/24 · Σ (y_i·z_(i+1) + 2·y_i·z_i + 2·y_(i+1)·z_(i+1)
                  + y_(i+1)·z_i) · c_i
```

Laeuft das Polygon rechtsherum, kehren alle Summen das Vorzeichen; geteilt
durch das Vorzeichen der Flaeche ist das gleichgueltig. Danach mit Steiner
auf den Schwerpunkt.

### summe

```python
def summe(teile: Sequence[Tuple[float, Flaechenwerte]]) -> Flaechenwerte
```

Die Werte eines zusammengesetzten Querschnitts.

`teile` sind Paare aus Gewicht und Werten. Das Gewicht ist +1 fuer eine
Flaeche, die zaehlt, und -1 fuer eine, die herausgenommen wird -- eine
Aussparung. Ueber die Momente um den Ursprung summiert und dann wieder auf
den gemeinsamen Schwerpunkt bezogen (Steiner hin und zurueck).

### _kanten

```python
def _kanten(punkte: Sequence[Punkt])
```

Die Kanten eines Polygons, die letzte schliesst zum ersten Punkt.

### _kreuz

```python
def _kreuz(o: Punkt, a: Punkt, b: Punkt) -> float
```

Das Kreuzprodukt (a - o) × (b - o): > 0 heisst, b liegt links von o→a.

### abstand_zur_strecke

```python
def abstand_zur_strecke(p: Punkt, a: Punkt, b: Punkt) -> float
```

Der kuerzeste Abstand von `p` zur Strecke `a`–`b`.

### abstand_zum_rand

```python
def abstand_zum_rand(p: Punkt, punkte: Sequence[Punkt]) -> float
```

Der kuerzeste Abstand von `p` zum Rand des Polygons.

### lage

```python
def lage(p: Punkt, punkte: Sequence[Punkt]) -> int
```

Wo `p` liegt: +1 innen, 0 auf dem Rand, -1 aussen.

Erst der Rand mit Toleranz, dann ein Strahl nach rechts: jede Kante, die er
kreuzt, wechselt zwischen innen und aussen. Halb offene Kanten (unten
eingeschlossen, oben nicht), damit ein Strahl durch eine Ecke nicht doppelt
zaehlt.

### echt_geschnitten

```python
def echt_geschnitten(a1: Punkt, a2: Punkt, b1: Punkt, b2: Punkt) -> bool
```

Ob sich zwei Strecken im Innern beider kreuzen.

Beruehren -- ein Endpunkt auf der anderen Strecke, gemeinsame Ecke,
deckungsgleiches Stueck -- zaehlt nicht. Das ist gewollt: Polygone duerfen
sich beruehren, und eine Aussparung darf am Rand ansetzen.

### selbstschnitt

```python
def selbstschnitt(punkte: Sequence[Punkt]) -> Optional[Tuple[int, int]]
```

Das erste Paar nicht benachbarter Kanten, die sich kreuzen -- oder nichts.

### polygon_pruefen

```python
def polygon_pruefen(punkte: Sequence[Punkt], name: str) -> None
```

Ob sich aus diesem Polygon rechnen laesst. Wirft [[opencivil.querschnitt.geometrie#GeometrieFehler|GeometrieFehler]]
mit einem Satz, der sagt, was nicht stimmt.

### schnitt_mit_gerade

```python
def schnitt_mit_gerade(punkte: Sequence[Punkt], normale: Tuple[float, float], v: float) -> List[Tuple[float, float]]
```

Wo die Gerade `n·p = v` im Polygon liegt -- als Abschnitte auf ihr.

Gemessen wird entlang der Tangente `t = (-n_z, n_y)`, also `u = t·p`.
`normale` muss ein Einheitsvektor sein. Zurueck kommen die Paare
`(u_von, u_bis)` in aufsteigender Folge; ihre Laengen ergeben die Breite
des Polygons auf dieser Hoehe.

Gedacht fuer Geraden, die keine Ecke treffen -- die Fasern legen ihre
Mitten zwischen die Ecken. Trifft eine trotzdem eine Ecke, zaehlt die
halb offene Regel aus [[opencivil.querschnitt.geometrie#lage|lage]] sie genau einmal.

### Beziehung

```python
class Beziehung(str, Enum)
```

Wie zwei Polygone zueinander liegen.

- `ERSTES_IM_ZWEITEN = 'erstes_im_zweiten'`
- `ZWEITES_IM_ERSTEN = 'zweites_im_ersten'`
- `GETRENNT = 'getrennt'`
- `UEBERLAPPEND = 'ueberlappend'`

### _ganz_in

```python
def _ganz_in(p: Sequence[Punkt], q: Sequence[Punkt]) -> Optional[bool]
```

Ob `p` ganz in `q` liegt: `True`, ganz draussen: `False`, weder
noch: `None`.

Gezaehlt werden die Ecken von `p` und die Mitten seiner Kanten. Eine
Ecke auf dem Rand von `q` sagt nichts; liegt alles auf dem Rand,
entscheiden die Kantenmitten -- so wird eine Aussparung, die am Rand
ansetzt, als innen erkannt.

### beziehung

```python
def beziehung(p: Sequence[Punkt], q: Sequence[Punkt]) -> Beziehung
```

Wie `p` zu `q` liegt.

Zuerst echte Kreuzungen von Kanten -- die bedeuten immer Ueberlappung.
Ohne sie entscheiden die Proben aus [[opencivil.querschnitt.geometrie#_ganz_in|_ganz_in]] in beide Richtungen.
Deckungsgleiche Polygone ueberlappen.

### verschachteln

```python
def verschachteln(polygone: Sequence[Sequence[Punkt]], namen: Sequence[str]) -> Tuple[Optional[int], ...]
```

Je Polygon das, in dem es liegt -- das kleinste, das es ganz enthaelt.

Wirft [[opencivil.querschnitt.geometrie#GeometrieFehler|GeometrieFehler]], wenn zwei Polygone teilweise ueberlappen.

### innerstes

```python
def innerstes(p: Punkt, polygone: Sequence[Sequence[Punkt]]) -> Optional[int]
```

Das kleinste Polygon, in dessen Innern `p` liegt -- oder nichts.

Bei verschachtelten Polygonen ist das das innerste, also das, dessen
Material an dieser Stelle gilt.

### stab_liegt_in

```python
def stab_liegt_in(p: Punkt, radius: float, polygone: Sequence[Sequence[Punkt]], traegt: Sequence[bool]) -> bool
```

Ob ein runder Stab ganz in einem tragenden Polygon liegt.

`traegt` sagt je Polygon, ob sein Material Bewehrung aufnimmt -- beim
Stahlbeton: ob es Beton ist. Die Mitte muss im innersten Polygon liegen
und dieses muss tragen; dazu darf der Stab keinen Rand schneiden, weder
den aeusseren noch den einer Aussparung.

### strecke_liegt_in

```python
def strecke_liegt_in(a: Punkt, b: Punkt, polygone: Sequence[Sequence[Punkt]], traegt: Sequence[bool]) -> bool
```

Ob eine Strecke -- eine Schubwand -- ganz in tragenden Polygonen verlaeuft.

Geprueft wird an Proben alle [[opencivil.querschnitt.geometrie#Konstanten|WANDPROBE]] entlang der Strecke, ohne
die beiden Enden: eine Wand darf bis an den Rand reichen. Eine Aussparung,
schmaler als der Probenabstand, faellt dabei durch -- fuenf Millimeter
liegen unter allem, was als Aussparung gezeichnet wird.

### Linienart

```python
class Linienart(str, Enum)
```

Wie die Menge einer Stablinie angegeben ist.

- `FLAECHE = 'flaeche'` – Eine Stahlflaeche, gleichmaessig ueber die Linie verteilt.
- `ANZAHL = 'anzahl'` – So viele Staebe, gleich weit voneinander.
- `TEILUNG = 'teilung'` – Ein Wunschabstand -- gerundet auf den naechsten, der aufgeht.

### Stablinie

```python
@dataclass(frozen=True)
class Stablinie
```

Eine aufgeloeste Stablinie: wo ihre Staebe liegen.

- `von: Punkt`
- `bis: Punkt`
- `laenge: float`
- `felder: int` – In wie viele gleiche Felder die Linie geteilt ist; null bei einer Flaeche.
- `teilung: Optional[float]` – Der tatsaechliche Abstand der Staebe; `None` bei einer Flaeche.
- `punkte: Tuple[Punkt, ...]` – Die Stabmitten; leer bei einer Flaeche.

### _halb_auf

```python
def _halb_auf(x: float) -> int
```

Kaufmaennisch gerundet: 2.5 gibt 3. `round` gaebe 2 (zur geraden Zahl).

### stablinie

```python
def stablinie(von: Punkt, bis: Punkt, art: Linienart, wert: float, *, starteisen: bool=True, endeisen: bool=True) -> Stablinie
```

Wo die Staebe einer Linie liegen.

Die Linie wird in `m` gleiche Felder geteilt, die Staebe sitzen auf den
Teilpunkten. `starteisen` und `endeisen` sagen, ob die beiden Enden
besetzt sind:

```
Anzahl n:   m = n - 1 + (0 oder 1 je freies Ende)
Teilung s:  m = runde(L / s), kaufmaennisch; tatsaechlich L / m
```

Bei 1000 mm und s = 150 sind das sieben Felder zu 142.9 mm, mit beiden
Enden acht Staebe. Bei einer Flaeche gibt es keine Einzelstaebe.


## Konstanten

- `TOLERANZ = 1e-06` – Wie nahe zwei Lagen beieinander liegen duerfen, um als gleich zu gelten, in der Einheit der Punkte. Ein Millionstel Millimeter liegt weit unter allem, was jemand zeichnet, und weit ueber dem Rauschen gerechneter Kreispunkte.
- `NULL = Flaechenwerte(A=0.0, y_S=0.0, z_S=0.0, I_y=0.0, I_z=0.0, I_yz=0.0)` – Ein Querschnitt ohne Flaeche -- der Anfang jeder Summe.
- `WANDPROBE = 5.0` – Abstand der Proben entlang einer Wandlinie, in der Einheit der Punkte.

## Gebraucht von

- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.interaktion]]
- [[opencivil.web.api]]
