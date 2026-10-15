---
erzeugt: 3a52a9d1dff2
art: modul
tags: [modul]
---
> [!abstract] opencivil/querschnitt/analyse.py
> der gezeichnete Querschnitt als Bauteil im Rechenwerk.
> Paket [[opencivil.querschnitt]] · [Quelltext](../../opencivil/querschnitt/analyse.py)

## VERANTWORTUNG

Aus der Beschreibung einer Querschnittsanalyse wird hier ein Bauteil wie die
Platte ([[opencivil.querschnitt.platte#Plattenquerschnitt|Plattenquerschnitt]]): mit
Namensraum, Ueberschrift, Werten und einer Herleitung des Querschnitts --
Polygone, Bruttoquerschnitt, Bewehrung, Schubwaende. Die Nachweise bekommen
das Bauteil und lesen daraus die Geometrie; seine Zahlen beziehen sie ueber
das Rechenwerk, damit jede rueckverfolgbar bleibt.


## DIE ZEICHNUNG WIRD HIER GEPRUEFT

Kreuzt sich ein Polygon, ueberlappen sich zwei, liegt ein Stab nicht ganz im
Beton oder eine Wand ausserhalb -- dann entsteht kein Bauteil, sondern ein
[[opencivil.querschnitt.geometrie#GeometrieFehler|GeometrieFehler]] mit dem Element,
das nicht stimmt. Erst hier und nicht beim Oeffnen der Datei: eine Analyse
mit einem verunglueckten Polygon soll sich oeffnen und korrigieren lassen.


## KOORDINATEN UND EINHEITEN

Die Beschreibung zeichnet in Millimetern, y nach rechts, z nach oben. Die
Tabellen der Herleitung bleiben in Millimetern; fuer die Nachweise wird
einmal in Meter umgerechnet ([[opencivil.querschnitt.analyse#Querschnittsanalyse.geometrie|Querschnittsanalyse.geometrie]]).

## Inhalt

### Lastfall

```python
@dataclass(frozen=True)
class Lastfall
```

Ein Lastfall der Analyse, in SI-Basis: N in N, Momente in Nm.

Vorzeichen wie in der Beschreibung: N > 0 Zug, M_y > 0 zieht unten, M_z > 0
links, V_y und V_z in Achsrichtung, T im Gegenuhrzeigersinn.

- `name: str`
- `N: float = 0.0`
- `M_y: float = 0.0`
- `M_z: float = 0.0`
- `V_y: float = 0.0`
- `V_z: float = 0.0`
- `T: float = 0.0`

#### Lastfall.kennung

```python
@property
def kennung(self) -> str
```

### Flaechenteil

```python
@dataclass(frozen=True)
class Flaechenteil
```

Ein Polygon der Zeichnung -- Ecken in mm, ohne Material eine Aussparung.

- `name: str`
- `kennung: str`
- `punkte: Tuple[Punkt, ...]`
- `stoff: Optional[Baustoff]`

### Stabgruppe

```python
@dataclass(frozen=True)
class Stabgruppe
```

Ein Bewehrungselement der Zeichnung: ein Einzelstab oder eine Stablinie.

`punkte` sind die Stabmitten in mm, bei einer verschmierten Flaeche leer.
`flaeche` ist die ganze Stahlflaeche des Elements in mm².

- `name: str`
- `kennung: str`
- `art: str` – `stab` oder eine [[opencivil.querschnitt.geometrie#Linienart|Linienart]].
- `stahl: Baustoff`
- `durchmesser: float`
- `punkte: Tuple[Punkt, ...]`
- `flaeche: float`
- `von: Punkt`
- `bis: Punkt`
- `linie: Optional[geo.Stablinie] = None`
- `gewaehlt: Optional[float] = None` – Bei einer Linie nach Teilung der eingegebene Abstand.

### Wandangabe

```python
@dataclass(frozen=True)
class Wandangabe
```

Eine Schubwand, wie gezeichnet: Achse in mm, Bügel, und der Beton, in dem sie liegt.

- `name: str`
- `kennung: str`
- `von: Punkt`
- `bis: Punkt`
- `dicke: float`
- `durchmesser: float`
- `teilung: float`
- `schnitte: int`
- `stahl: Optional[Baustoff]`
- `beton: Baustoff`

#### Wandangabe.laenge

```python
@property
def laenge(self) -> float
```

#### Wandangabe.a_sw_s

```python
@property
def a_sw_s(self) -> float
```

Buegelquerschnitt je Laenge, `n · π⌀²/4 / s`, in mm²/mm.

### Meldung

```python
@dataclass(frozen=True)
class Meldung
```

Was an der Zeichnung nicht stimmt, und welche Elemente es betrifft. Der
Text nennt sie beim Namen, `elemente` traegt ihre Kennungen.

- `text: str`
- `elemente: Tuple[str, ...]`

### Zeichnung

```python
class Zeichnung
```

Die Zeichnung einer Analyse, geprueft -- in mm und ohne Rechenwerk.

Sammelt jede Meldung, statt bei der ersten abzubrechen: das Zeichenfenster
zeigt sie alle auf einmal, jede an ihrem Element. Das Bauteil
([[opencivil.querschnitt.analyse#Querschnittsanalyse|Querschnittsanalyse]]) baut darauf und bricht bei der ersten ab --
gerechnet wird nur, was ganz stimmt. Dieselben Pruefungen an einer Stelle.

Jedes Element ist ein Woerterbuch mit `name` und `kennung`, wie sie
[[opencivil.querschnitt.analyse#Zeichnung|QuerschnittsanalyseEintrag.elemente]] vergibt -- benannt wird hier
nichts. `polygone` tragen `punkte` und `traegt` (ohne Material ist
es eine Aussparung), `staebe` `lage` und `durchmesser`, `linien`
und `waende` die Felder der Beschreibung.

#### Zeichnung.gueltig

```python
@property
def gueltig(self) -> bool
```

#### Zeichnung.gewicht

```python
def gewicht(self, i: int) -> float
```

+1 fuer ein Polygon mit Material, -1 fuer eine Aussparung darin, sonst 0.

#### Zeichnung.innerstes

```python
def innerstes(self, p: Punkt) -> Optional[int]
```

#### Zeichnung._linie

```python
def _linie(self, l: Mapping) -> Optional[geo.Stablinie]
```

Die aufgeloeste Linie -- auch wenn ein Stab danebenliegt, fuer die Zeichnung.

#### Zeichnung._zellen

```python
def _zellen(self, waende: Sequence[Mapping]) -> List[Tuple[List[Punkt], float]]
```

Die geschlossenen Flaechen der Wandachsen, als Umriss und Flaeche, in mm.

Gesucht wird in Metern, wie im Nachweis: die Toleranz, ab der zwei
Wandenden ein Knoten sind, ist eine Laenge. In Millimetern gesucht,
hiesse sie hier etwas anderes als dort -- und das Fenster zeigte eine
Zelle nicht, mit der gerechnet wird.

### QuerschnittsaufbauProzedur

```python
class QuerschnittsaufbauProzedur(Prozedur)
```

Polygone, Bruttoquerschnitt, Bewehrung und Schubwaende -- in Tabellen.

#### QuerschnittsaufbauProzedur.rechne

```python
def rechne(self, e: Eingaben, p: Protokoll) -> Mapping[str, Groesse]
```

### Querschnittsanalyse

```python
class Querschnittsanalyse
```

Ein gezeichneter Querschnitt, fertig fuer das Rechenwerk und die Nachweise.

#### Querschnittsanalyse.beton_an

```python
def beton_an(self, p: Punkt) -> Optional[Baustoff]
```

Der Werkstoff des innersten Polygons an dieser Stelle.

#### Querschnittsanalyse.abschnitt

```python
@property
def abschnitt(self) -> Abschnitt
```

#### Querschnittsanalyse.id_von

```python
def id_von(self, kurzname: str) -> str
```

#### Querschnittsanalyse.ins_rechenwerk

```python
def ins_rechenwerk(self, werk) -> 'Querschnittsanalyse'
```

#### Querschnittsanalyse.baustoffe

```python
@property
def baustoffe(self) -> List[Baustoff]
```

Jeder Baustoff, den die Analyse benutzt: erst die der Flaechen, dann die Staehle.

#### Querschnittsanalyse.aufbau_protokollieren

```python
def aufbau_protokollieren(self, p: Protokoll) -> Dict[str, Groesse]
```

#### Querschnittsanalyse.angaben

```python
def angaben(self) -> Tuple[GleichungBlock, TabellenBlock]
```

Was ueber der Nachweistabelle steht: Werkstoffe, Flaeche, Schwerpunkt; die Bewehrung.

#### Querschnittsanalyse.satz

```python
def satz(self, stoff: Baustoff) -> str
```

#### Querschnittsanalyse.betongesetz

```python
def betongesetz(self, stoff: Baustoff) -> str
```

#### Querschnittsanalyse.werkstoffbezuege

```python
def werkstoffbezuege(self) -> List[Eingabebezug]
```

Die Kennwerte jedes Baustoffs der Analyse, als Eingaben der Nachweise.

#### Querschnittsanalyse.kennwert

```python
def kennwert(self, e: Eingaben, stoff: Baustoff, kennwert: str) -> float
```

#### Querschnittsanalyse.werkstoffe

```python
def werkstoffe(self, e: Eingaben) -> Tuple[List[Werkstoff], Callable[[Baustoff], int]]
```

Die Werkstoffe der Interaktion, mit den gewaehlten Rechenwerten.

Beton: Parabel-Rechteck oder Spannungsblock, gedrueckt bis `-eps_c2d`
samt C-Punkt, verdraengt von den Staeben. Betonstahl: bilinear,
`±eps_ud`. Die Rechenwerte bestimmen, wo die Plateaus liegen
(`f_cd` oder `f_ck`, `f_yd` oder `f_yk`); Moduln und
Dehnungsgrenzen bleiben -- wie beim Loeser der Platte
([[opencivil.nachweis.querschnittsloeser#Werkstoffsatz|Werkstoffsatz]]).

#### Querschnittsanalyse.werkstoffe_protokollieren

```python
def werkstoffe_protokollieren(self, p: Protokoll, e: Eingaben, basis: str) -> None
```

Die Gesetze, mit denen gerechnet wird, und die Werte darin.

#### Querschnittsanalyse.grundbezuege

```python
def grundbezuege(self) -> List[Eingabebezug]
```

Was jeder Nachweis der Analyse liest: den Schwerpunkt und die Werkstoffe.

#### Querschnittsanalyse.interaktion

```python
def interaktion(self, e: Eingaben) -> Tuple[Querschnitt, List[str]]
```

Der Querschnitt im Bruchzustand, mit den gewaehlten Werkstoffgesetzen
und dem Schwerpunkt aus dem Rechenwerk als Bezugspunkt -- dazu je
Bewehrung der Name ihres Elements.

#### Querschnittsanalyse.geometrie

```python
def geometrie(self, index_von: Callable[[Baustoff], int]) -> Tuple[List[Teil], List[Bewehrung], List[str]]
```

Polygone und Bewehrung in Metern, mit den Werkstoffen als Index --
dazu je Bewehrung der Name ihres Elements, fuer die Kraefte in der Probe.

#### Querschnittsanalyse.schubwaende

```python
def schubwaende(self, f_sd: Callable[[Wandangabe], float], f_cd: Callable[[Wandangabe], float], k_c: float) -> List[Wand]
```

Die Schubwaende in Metern, mit den Festigkeiten, die der Nachweis waehlt.

#### Querschnittsanalyse.beton_ecken

```python
@property
def beton_ecken(self) -> List[Tuple[Punkt, Baustoff]]
```

Jede Ecke eines Polygons mit Material -- fuer das Rissmoment, in mm.


## Konstanten

- `KENNWERTE = {Baustoffart.BETON: ('f_ck', 'f_cd', 'eps_c1d', 'eps_c2d', 'k_sigma',…` – Die Kennwerte, die die Nachweise eines Werkstoffs lesen -- je Art alle, die eine der Wahlen braucht. Das Rechenwerk rechnet sie ohnehin.
- `_K_SIGMA = next((v for v in BETON_VORLAGEN if v.kurzname == 'k_sigma'))` – Die Regel fuer k_sigma steht beim Beton. Mit charakteristischen Werten gilt dieselbe, mit f_ck statt f_cd -- also wird sie von dort genommen.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.material.basis]]
- [[opencivil.material.beton]]
- [[opencivil.querschnitt.geometrie]]
- [[opencivil.querschnitt.interaktion]]
- [[opencivil.querschnitt.schubwaende]]
- [[opencivil.querschnitt.werkstoffgesetz]]

## Gebraucht von

- [[opencivil.nachweis.richtungsnachweise]]
- [[opencivil.nachweis.schiefe_biegung]]
- [[opencivil.nachweis.schubwandnachweis]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.querschnitt.schnittanalyse]]
- [[opencivil.web.api]]

## Formeln aus diesem Modul

- [[Bilineare Beziehung des Betonstahls]] · `Querschnittsanalyse.werkstoffe_protokollieren`
- [[Bügelquerschnitt je Länge einer Schubwand (n Schnitte)]] · `Querschnittsanalyse._waende_protokollieren`
- [[Fläche und Schwerpunkt eines Polygons (Satz von Gauss)]] · `Querschnittsanalyse.aufbau_protokollieren`
- [[Krümmungsbeiwert der Spannungs-Dehnungs-Beziehung]] · `Querschnittsanalyse.werkstoffe_protokollieren`
- [[Parabel-Rechteck-Beziehung des Betons]] · `Querschnittsanalyse.werkstoffe_protokollieren`
- [[Spannungsblock des Betons]] · `Querschnittsanalyse.werkstoffe_protokollieren`
- [[Teilung einer Stablinie – gleiche Felder, auf die Länge gerundet]] · `Querschnittsanalyse._bewehrung_protokollieren`
- [[Trägheitsmomente eines Polygons, bezogen auf den Schwerpunkt]] · `Querschnittsanalyse.aufbau_protokollieren`
