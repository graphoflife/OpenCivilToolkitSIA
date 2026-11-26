---
erzeugt: 6a3679b318ce
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
Polygone, Bruttoquerschnitt, Bewehrung, Schubwaende. Dazu, fuer sich,
`I_T` ([[opencivil.querschnitt.torsion|torsion]]): es braucht nur ein Stab
im Raum, und das Rechenwerk rechnet nur, was ein Ziel braucht. Die Nachweise bekommen
das Bauteil und lesen daraus die Geometrie; seine Zahlen beziehen sie ueber
das Rechenwerk, damit jede rueckverfolgbar bleibt.


## DIE ZEICHNUNG WIRD HIER GEPRUEFT

Kreuzt sich ein Polygon, ueberlappen sich zwei, liegt ein Stab nicht ganz im
Beton oder eine Wand ausserhalb -- dann entsteht kein Bauteil, sondern ein
[[opencivil.querschnitt.geometrie#GeometrieFehler|GeometrieFehler]] mit dem Element,
das nicht stimmt. Ebenso, wenn die Baustoffe zusammen keine Bauweise sind
([[opencivil.querschnitt.bauweise|bauweise]]): ein Polygon ist aus Beton,
Baustahl oder Holz, Bewehrung liegt nur im Beton. Erst hier und nicht beim Oeffnen der Datei: eine Analyse
mit einem verunglueckten Polygon soll sich oeffnen und korrigieren lassen.


## KOORDINATEN UND EINHEITEN

Die Beschreibung zeichnet in Millimetern, y nach rechts, z nach oben. Die
Tabellen der Herleitung bleiben in Millimetern; fuer die Nachweise wird
einmal in Meter umgerechnet ([[opencivil.querschnitt.analyse#Querschnittsanalyse.geometrie|Querschnittsanalyse.geometrie]]).

## Inhalt

### werkstoff

```python
def werkstoff(stoff: Baustoff, wert: Callable[[str], float], wahl: Rechenwahl, *, ungerissen: bool=False) -> Werkstoff
```

Ein Baustoff als Werkstoff der Interaktion -- die eine Stelle, die ihn
baut, fuer den gezeichneten Querschnitt und den Pfahl. `wert` liefert
zu einer Wert-ID die Zahl in SI.

Beton: das Gesetz seiner Rechenart, gebaut wie bei der Platte
([[opencivil.querschnitt.gesetzwahl#betongesetz|betongesetz]]), der Beiwert der
Parabel also aus `E_cm/(1+phi)` -- oder, `ungerissen`, linear in
Druck und Zug mit demselben Modul, aus derselben Stelle; gedrueckt bis
`-eps_c2d` samt Punkt C, verdraengt von den Staeben. Betonstahl: bilinear,
`±eps_ud`. Baustahl: elastisch-plastisch, in Zug und Druck gleich,
`±eps_ud`. Holz: in Faserrichtung linear bis zum Bruch oder, wie die
Wahl es sagt, auf Druck elastisch-plastisch bis `-eps_cu`
([[opencivil.querschnitt.gesetzwahl#holzgesetz|holzgesetz]]). Der Wertesatz
bestimmt, wo die Plateaus liegen (`f_cd` oder `f_ck`, `f_yd` oder
`f_yk`, beim Baustahl `f_yd` oder `f_y`); Moduln und
Dehnungsgrenzen bleiben
([[opencivil.querschnitt.gesetzwahl#Werkstoffsatz|Werkstoffsatz]]). Das Holz hat
keinen: SIA 265:2012 nennt nur Bemessungswerte. Welche Kennwerte ein
Gesetz nimmt, sagt [[opencivil.querschnitt.gesetzwahl#Rechenwahl.kennwerte|kennwerte]].
Jeder Werkstoff traegt das Wort seiner Art, fuer die Namen seiner Grenzen.

Bis 2026-10-16 baute die Spannung-Dehnung-Analyse ihre Werkstoffe
selbst, und der Bruchzustand nahm den Beiwert der Parabel aus `E_cd`.

### gesetz_protokollieren

```python
def gesetz_protokollieren(p: Protokoll, e: Eingaben, stoff: Baustoff, gesetz: Gesetz, wahl: Rechenwahl, basis: str) -> None
```

Das Gesetz eines Baustoffs in die Herleitung, mit den Kennwerten, aus
denen es gebaut ist ([[opencivil.querschnitt.analyse#werkstoff|werkstoff]]) -- gelesen aus `e` unter
[[opencivil.material.basis#Baustoff.eingabename|eingabename]].

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
- `profil: Optional[Profillage] = None` – Beim Umriss eines Stahlprofils seine Lage -- daraus kennt der Stahlbau seine Bleche.

#### Flaechenteil.herkunft

```python
@property
def herkunft(self) -> str
```

Was es ist, wenn mehr als ein Polygon: beim Stahlprofil «HEB 300» -- so steht es im Bericht.

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

Buegelquerschnitt je Laenge, in mm²/mm ([[opencivil.querschnitt.geometrie#buegelgehalt|buegelgehalt]]).

### Meldung

```python
@dataclass(frozen=True)
class Meldung
```

Was an der Zeichnung nicht stimmt, und welche Elemente es betrifft. Der
Text nennt sie beim Namen, `elemente` traegt ihre Kennungen.

- `text: str`
- `elemente: Tuple[str, ...]`
- `fehler: bool = True` – Ob etwas nicht stimmt -- sonst fehlt nur etwas, und die Zeichnung ist unfertig: «Es gibt kein Polygon mit Material» bei Bewehrung allein.

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
nichts. `polygone` tragen `punkte`, `traegt` (ohne Material ist
es eine Aussparung) und `beton`: ob Bewehrung in ihm liegen darf
([[opencivil.querschnitt.bauweise#Konstanten|BEWEHRT]]). `staebe` `lage`
und `durchmesser`, `linien` und `waende` die Felder der
Beschreibung, `spannglieder` wie die Staebe, mit dem Durchmesser ihrer
Flaeche.

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

### Herleitungsteil

```python
class Herleitungsteil(Prozedur)
```

Ein Teil der Herleitung des Querschnitts -- die Analyse schreibt ihn selbst.

#### Herleitungsteil.rechne

```python
def rechne(self, e: Eingaben, p: Protokoll) -> Mapping[str, Groesse]
```

### Querschnittsanalyse

```python
class Querschnittsanalyse(Rechenobjekt)
```

Ein gezeichneter Querschnitt, fertig fuer das Rechenwerk und die Nachweise.

- `WAS = 'Querschnittsanalyse'`

#### Querschnittsanalyse.beton_an

```python
def beton_an(self, p: Punkt) -> Optional[Baustoff]
```

Der Werkstoff des innersten Polygons an dieser Stelle.

#### Querschnittsanalyse.zugseiten

```python
@property
def zugseiten(self) -> Tuple[Zugseite, ...]
```

Die Seiten, die je ein Nachweis ziehen laesst ([[opencivil.querschnitt.biegung#Biegung|Biegung.zugseiten]]).

#### Querschnittsanalyse.abschnitt

```python
@property
def abschnitt(self) -> Abschnitt
```

#### Querschnittsanalyse.baustoffe

```python
@property
def baustoffe(self) -> List[Baustoff]
```

Jeder Baustoff, den die Analyse benutzt: erst die der Flaechen, dann
die Staehle, zuletzt der Spannstahl.

#### Querschnittsanalyse.baustoffe_mit_werkstoff

```python
@property
def baustoffe_mit_werkstoff(self) -> List[Baustoff]
```

Die Baustoffe mit je einem Werkstoff im Querschnitt -- alle ausser dem
Spannstahl: jedes Spannglied hat seinen eigenen, nach diesen
([[opencivil.querschnitt.analyse#Querschnittsanalyse.werkstoffe|werkstoffe]]).

#### Querschnittsanalyse.aufbau_protokollieren

```python
def aufbau_protokollieren(self, p: Protokoll) -> Dict[str, Groesse]
```

#### Querschnittsanalyse.torsion_protokollieren

```python
def torsion_protokollieren(self, p: Protokoll) -> Dict[str, Groesse]
```

`I_T` nach St. Venant, numerisch -- mit den beiden Gittern, aus denen
es kommt. Unter eigener Ueberschrift: gerechnet wird es, wenn es einer
braucht, oft nach den Nachweisen.

#### Querschnittsanalyse.angaben

```python
def angaben(self) -> Tuple[GleichungBlock, Optional[TabellenBlock]]
```

Was ueber der Nachweistabelle steht: die Werkstoffe der Flaechen,
Flaeche, Schwerpunkt; die Bewehrung -- ohne Stab, Spannglied und Wand,
etwa beim Stahl, keine Tabelle.

#### Querschnittsanalyse.werkstoffbezuege

```python
def werkstoffbezuege(self) -> List[Eingabebezug]
```

Die Kennwerte jedes Baustoffs der Analyse, als Eingaben der Nachweise.

#### Querschnittsanalyse.stoff_von_werkstoff

```python
def stoff_von_werkstoff(self, w: int) -> Baustoff
```

Der Baustoff hinter einem Werkstoff des Querschnitts ([[opencivil.querschnitt.analyse#Querschnittsanalyse.werkstoffe|werkstoffe]])
-- bei dem eines Spannglieds sein Spannstahl.

#### Querschnittsanalyse.kennwert

```python
def kennwert(self, e: Eingaben, stoff: Baustoff, kennwert: str) -> float
```

#### Querschnittsanalyse.werkstoffe

```python
def werkstoffe(self, wert: Callable[[str], float], wahl: Rechenwahl, *, ungerissen: bool=False) -> Tuple[List[Werkstoff], Callable[[Baustoff], int]]
```

Die Werkstoffe des Querschnitts, je Baustoff einer ([[opencivil.querschnitt.analyse#werkstoff|werkstoff]]),
danach je Spannglied seiner
([[opencivil.querschnitt.spannglieder#Spannglieder.werkstoffe|werkstoffe]]).
`wert` liefert zu einer Wert-ID die Zahl in SI; `wahl` ist die
Rechenwahl: im Bruchzustand die der Analyse ([[opencivil.querschnitt.analyse#Querschnittsanalyse|wahl]]), fuer
Spannungen und Knicken die des Kapitels.

#### Querschnittsanalyse.querschnitt

```python
def querschnitt(self, wert: Callable[[str], float], wahl: Rechenwahl, *, ungerissen: bool=False) -> Tuple[Querschnitt, List[Bewehrungselement], Dict[int, Stahlgesetz]]
```

Der Querschnitt mit den Gesetzen einer Rechenwahl -- dazu je
Bewehrung ihr Element und je Stahl sein Gesetz,
nach dem Index des Werkstoffs. `wert` liefert zu einer Wert-ID die
Zahl in SI. Zerlegt in so viele Streifen, wie die Platte Fasern hat
([[opencivil.querschnitt.fasern#Konstanten|FASERN]]).

#### Querschnittsanalyse.werkstoffe_protokollieren

```python
def werkstoffe_protokollieren(self, p: Protokoll, e: Eingaben, basis: str) -> None
```

Die Gesetze, mit denen gerechnet wird, je Material mit seiner Wahl --
jedes schreibt sich selbst, mit den Werten darin. Ohne Kriechen: die
Parabel haengt hier an `E_cm`.

#### Querschnittsanalyse.gliedgesetze_protokollieren

```python
def gliedgesetze_protokollieren(self, p: Protokoll, e: Eingaben, werkstoffe: Sequence[Werkstoff], wahl: Rechenwahl, *, titel: Callable[[Spannglied], str], basis: str) -> None
```

Die Gesetze der Spannglieder -- `werkstoffe` die von [[opencivil.querschnitt.analyse#Querschnittsanalyse.werkstoffe|werkstoffe]].

#### Querschnittsanalyse.grundbezuege

```python
def grundbezuege(self) -> List[Eingabebezug]
```

Was jeder Nachweis der Analyse liest: den Schwerpunkt, die Werkstoffe
und die Spannung und Vordehnung jedes Spannglieds.

#### Querschnittsanalyse.interaktion

```python
def interaktion(self, e: Eingaben) -> Tuple[Querschnitt, List[Bewehrungselement]]
```

Der Querschnitt im Bruchzustand, mit den gewaehlten Werkstoffgesetzen
und dem Schwerpunkt aus dem Rechenwerk als Bezugspunkt -- dazu je
Bewehrung das Element, aus dem sie stammt.

#### Querschnittsanalyse.geometrie

```python
def geometrie(self, index_von: Callable[[Baustoff], int]) -> Tuple[List[Teil], List[Bewehrung], List[Bewehrungselement]]
```

Polygone und Bewehrung in Metern, mit den Werkstoffen als Index --
dazu je Bewehrung das Element, aus dem sie stammt: sein Name steht in
der Probe, sein Durchmesser bestimmt die Rissbreite. Die Spannglieder
kommen zuletzt, je mit ihrem eigenen Werkstoff, der nach denen der
Baustoffe steht ([[opencivil.querschnitt.analyse#Querschnittsanalyse.werkstoffe|werkstoffe]]): so bleibt jede Stelle des
Betonstahls dort, wo sie ohne Spannglied waere.

#### Querschnittsanalyse.schubwaende

```python
def schubwaende(self, f_yd: Callable[[Wandangabe], float], f_cd: Callable[[Wandangabe], float], k_c: float) -> List[Wand]
```

Die Schubwaende in Metern, mit den Festigkeiten, die der Nachweis waehlt.

#### Querschnittsanalyse.schubwaende_mit

```python
def schubwaende_mit(self, e: Eingaben) -> List[Wand]
```

Die Schubwaende mit den Festigkeiten ihrer Werkstoffe, wie deren
Rechenwahl sie waehlt: `f_yd` der Buegel -- ohne Buegel null --,
`f_cd` des Betons, in dem die Wand liegt. Der Nachweis der Waende
und die Kennzahlen lesen sie hier.

#### Querschnittsanalyse.neigungsgrenzen

```python
def neigungsgrenzen(self, e: Eingaben) -> Tuple[int, int]
```

`α_min` und `α_max` der Druckdiagonalen, ganzgradig.

#### Querschnittsanalyse.schubbezuege

```python
def schubbezuege(self) -> List[Eingabebezug]
```

Was die Schubwaende ausser den Werkstoffen lesen: die Neigungsgrenzen und k_c.

#### Querschnittsanalyse.beton_ecken

```python
@property
def beton_ecken(self) -> List[Tuple[Punkt, Baustoff]]
```

Jede Ecke eines Polygons mit Material -- fuer das Rissmoment, in mm.


## Konstanten

- `KENNWERTE = {Baustoffart.BETON: ('f_ck', 'f_cd', 'eps_c1d', 'eps_c2d', 'f_ctm', '…` – Die Kennwerte, die die Nachweise eines Werkstoffs lesen -- je Art alle, die eine der Wahlen braucht. Das Rechenwerk rechnet sie ohnehin. Aus `E_cm` entsteht der Beiwert der Parabel, wie bei der Platte, beim Knicken aus `E_cd`; der Gebrauchszustand rechnet mit `E_cm/(1+phi)`.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.rechenobjekt]]
- [[opencivil.core.wert]]
- [[opencivil.material.basis]]
- [[opencivil.querschnitt.bauweise]]
- [[opencivil.querschnitt.bewehrungselemente]]
- [[opencivil.querschnitt.biegung]]
- [[opencivil.querschnitt.fachwerk]]
- [[opencivil.querschnitt.fasern]]
- [[opencivil.querschnitt.geometrie]]
- [[opencivil.querschnitt.gesetzwahl]]
- [[opencivil.querschnitt.interaktion]]
- [[opencivil.querschnitt.schubwaende]]
- [[opencivil.querschnitt.spannglieder]]
- [[opencivil.querschnitt.torsion]]
- [[opencivil.querschnitt.werkstoffgesetz]]
- [[opencivil.querschnitt.zugseite]]
- [[opencivil.stahlprofile.lage]]

## Gebraucht von

- [[opencivil.nachweis.qa_gebrauch]]
- [[opencivil.nachweis.qa_holz]]
- [[opencivil.nachweis.qa_holz_kennzahlen]]
- [[opencivil.nachweis.qa_holz_stabilitaet]]
- [[opencivil.nachweis.qa_holz_werte]]
- [[opencivil.nachweis.qa_kennzahlen]]
- [[opencivil.nachweis.qa_knicken]]
- [[opencivil.nachweis.qa_stahl]]
- [[opencivil.nachweis.qa_stahl_kennzahlen]]
- [[opencivil.nachweis.qa_stahl_stabilitaet]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.nachweis.richtungsnachweise]]
- [[opencivil.nachweis.rissgroessen]]
- [[opencivil.nachweis.schiefe_biegung]]
- [[opencivil.nachweis.schubwandnachweis]]
- [[opencivil.nachweis.stabgrenzen]]
- [[opencivil.pfahl.innen]]
- [[opencivil.pfahl.innen_quer]]
- [[opencivil.pfahl.quer]]
- [[opencivil.projekt.aufbau.querschnittsanalyse]]
- [[opencivil.spannungsanalyse.analysen]]
- [[opencivil.spannungsanalyse.rissfrei]]
- [[opencivil.spannungsanalyse.schnitt]]
- [[opencivil.stahlbau.querschnitt]]
- [[opencivil.web.zeichengeometrie]]

## Formeln aus diesem Modul

- [[Bügelquerschnitt je Länge einer Schubwand (n Schnitte)]] · `Querschnittsanalyse._waende_protokollieren`
- [[Fläche und Schwerpunkt eines Polygons (Satz von Gauss)]] · `Querschnittsanalyse.aufbau_protokollieren`
- [[Spannungsfunktion von Prandtl]] · `Querschnittsanalyse.torsion_protokollieren`
- [[Teilung einer Stablinie – gleiche Felder, auf die Länge gerundet]] · `Querschnittsanalyse._bewehrung_protokollieren`
- [[Torsionsträgheitsmoment aus der Spannungsfunktion]] · `Querschnittsanalyse.torsion_protokollieren`
- [[Torsionsträgheitsmoment, nach Richardson aus beiden Gittern]] · `Querschnittsanalyse.torsion_protokollieren`
- [[Trägheitsmomente eines Polygons, bezogen auf den Schwerpunkt]] · `Querschnittsanalyse.aufbau_protokollieren`
- [[Verschmierte Stahlfläche aus Stäben]] · `Querschnittsanalyse._bewehrung_protokollieren`
