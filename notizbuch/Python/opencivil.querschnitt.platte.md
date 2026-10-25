---
erzeugt: c0a73fc0f46c
art: modul
tags: [modul]
---
> [!abstract] opencivil/querschnitt/platte.py
> Stahlbeton-Plattenquerschnitt.
> Paket [[opencivil.querschnitt]] · [Quelltext](../../opencivil/querschnitt/platte.py)

## VERANTWORTUNG

Beschreibt die Geometrie einer Platte und erzeugt daraus die Berechnungen fuer
Bewehrungsquerschnitte und statische Hoehen. Wie der Lagenaufbau Tiefe und
Querschnitt je Posten rechnet und wie ein Posten zu den Nachweisen reist,
steht in [[opencivil.querschnitt.lagenaufbau]].


## AUFBAU -- VIER LAGEN

Eine Platte hat vier Bewehrungslagen, von unten nach oben durchgezaehlt:

```
Überdeckung oben
    4. Lage      Richtung waehlbar
    3. Lage      Gegenrichtung zur 4. Lage
    ---- Plattenmitte ----
    2. Lage      Gegenrichtung zur 1. Lage
    1. Lage      Richtung waehlbar
Überdeckung unten
```

Jede Lage besteht aus einer **Grundbewehrung** und einer optionalen **Zulage**.
Beide liegen auf derselben Hoehe -- sie beruehren dieselbe Huellebene und sind
je um ihren eigenen Halbmesser eingerueckt. Die Huelle fuer die naechste Lage
richtet sich nach dem groesseren der beiden Durchmesser.


## X UND Y SIND GETRENNTE TRAGRICHTUNGEN

Bewehrung in y-Richtung traegt nichts zum Momentenwiderstand um die x-Achse bei.
Deshalb liefert [[opencivil.querschnitt.platte#Plattenquerschnitt.lagen_in_richtung|Plattenquerschnitt.lagen_in_richtung]] die Lagen je
Richtung, und der Nachweis wird je Richtung eigens gefuehrt.


## Z-ACHSE

`z` wird von der Oberkante nach unten gemessen, 0 \<= z \<= h. Damit gilt fuer
alle Lagen dieselbe Rechnung, und die Interaktionsrechnung braucht keine
Sonderfaelle. Die statische Hoehe einer unteren Lage ist ihr `z`, die einer
oberen `h - z` ([[opencivil.querschnitt.lagenaufbau#statische_hoehe|statische_hoehe]]).

## Inhalt

### Richtung

```python
class Richtung(Wahl)
```

Tragrichtung einer Bewehrungslage.

- `X = 'x'`
- `Y = 'y'`

#### Richtung.gegenrichtung

```python
@property
def gegenrichtung(self) -> 'Richtung'
```

#### Richtung.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Richtung.breite

```python
@property
def breite(self) -> str
```

Der Name der Breite, je die in dieser Richtung gerechnet wird: `b`
in x, `b_y` in y -- in y stets je Laufmeter ([[opencivil.querschnitt.platte#Konstanten|BREITE_Y_MM]]).

### Postenart

```python
class Postenart(str, Enum)
```

Grundbewehrung oder Zulage innerhalb einer Lage.

- `GRUND = 'grund'`
- `ZULAGE = 'zulage'`

#### Postenart.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Postenart.kuerzel

```python
@property
def kuerzel(self) -> str
```

### Bewehrungsposten

```python
@dataclass
class Bewehrungsposten
```

Ein Satz gleicher Staebe innerhalb einer Lage.

Die Menge wird entweder ueber die Teilung (Regelfall bei Platten) oder ueber
die Stabzahl angegeben. Ein Durchmesser von null bedeutet: nicht vorhanden.

- `durchmesser: Groesse = field(default_factory=lambda: Groesse(0, MM))`
- `abstand: Optional[Groesse] = None`
- `anzahl: Optional[float] = None`

#### Bewehrungsposten.vorhanden

```python
@property
def vorhanden(self) -> bool
```

#### Bewehrungsposten.ueber_abstand

```python
@property
def ueber_abstand(self) -> bool
```

#### Bewehrungsposten.flaeche

```python
def flaeche(self, b: Groesse) -> Groesse
```

Bewehrungsquerschnitt, bezogen auf die Breite `b`.

#### Bewehrungsposten.menge_text

```python
def menge_text(self) -> str
```

### Bewehrungslage

```python
@dataclass
class Bewehrungslage
```

Eine der vier Lagen, bestehend aus Grundbewehrung und Zulage.

- `nummer: int` – 1 = unterste Lage, 4 = oberste.
- `richtung: Richtung`
- `stahl: Baustoff`
- `grund: Bewehrungsposten = field(default_factory=Bewehrungsposten)`
- `zulage: Bewehrungsposten = field(default_factory=Bewehrungsposten)`
- `unguenstig: bool = True` – Wie Grundbewehrung und Zulage innerhalb der Lage liegen. `False` (guenstig): beide beruehren dieselbe Huellebene und sind je um ihren eigenen Halbmesser eingerueckt -- die **aeusseren** Kanten fluchten. Das ist die guenstigste Anordnung; der duennere Stab bekommt den groessten Hebelarm. `True` (unguenstig, Vorgabe): die **inneren** Kanten fluchten, der duennere Stab wird also zur Plattenmitte hin geschoben. Bei den unteren Lagen heisst das: gleiche Oberkante; bei den oberen: gleiche Unterkante. Massgebend ist je der dickere Stab. Auf der Baustelle laesst sich nicht steuern, welche Kante fluchtet -- deshalb ist das die Vorgabe.

#### Bewehrungslage.von_unten

```python
@property
def von_unten(self) -> bool
```

Lagen 1 und 2 werden von der Unterkante aus gestapelt.

#### Bewehrungslage.seite

```python
@property
def seite(self) -> Zugseite
```

Die Seite, an der sie liegt -- und die ein Moment ziehen muss, damit sie traegt.

#### Bewehrungslage.stapelrang

```python
@property
def stapelrang(self) -> int
```

0 = aussen (direkt auf der Überdeckung), 1 = darüber.

#### Bewehrungslage.vorhanden

```python
@property
def vorhanden(self) -> bool
```

#### Bewehrungslage.groesster_durchmesser

```python
@property
def groesster_durchmesser(self) -> Groesse
```

#### Bewehrungslage.posten

```python
def posten(self) -> Iterator[Bewehrungsposten]
```

#### Bewehrungslage.benannte_posten

```python
def benannte_posten(self) -> Iterator[Tuple[Postenart, Bewehrungsposten]]
```

#### Bewehrungslage.beschriftung

```python
def beschriftung(self) -> str
```

#### Bewehrungslage.index

```python
@property
def index(self) -> str
```

Der Symbolindex der Lage, z.B. `1,x` -- der eines Postens haengt die Art an.

### Querkraftbewehrung

```python
@dataclass
class Querkraftbewehrung
```

Bügelbewehrung einer Platte -- ein Raster über die ganze Fläche.

Ein Durchmesser, eine Teilung in x und eine in y. In y darf statt der
Teilung eine Stabzahl über die betrachtete Breite `b` stehen; in x
nicht. Der Widerstand bezieht sich auf den Laufmeter in Tragrichtung, und
eine Stabzahl in x hätte darin keinen Bezug -- wer sie angibt, bekommt
deshalb nur noch Nachweise in x-Richtung.

`alpha_min` und `alpha_max` begrenzen die Neigung der Druckdiagonalen.
Gesucht wird darin ganzgradig die Neigung mit dem grössten Widerstand;
Zwischenwerte sind eine Genauigkeit, die das Fachwerkmodell nicht hergibt.

- `durchmesser: Groesse = field(default_factory=lambda: Groesse(0, MM))`
- `stahl: Optional[Baustoff] = None`
- `abstand_x: Optional[Groesse] = None`
- `abstand_y: Optional[Groesse] = None`
- `anzahl_y: Optional[float] = None`
- `alpha_min: int = ALPHA_MIN`
- `alpha_max: int = ALPHA_MAX`

#### Querkraftbewehrung.vorhanden

```python
@property
def vorhanden(self) -> bool
```

#### Querkraftbewehrung.ueber_abstand_y

```python
@property
def ueber_abstand_y(self) -> bool
```

Ob die Menge in y über die Teilung angegeben ist (statt über die Zahl).

#### Querkraftbewehrung.flaeche

```python
@property
def flaeche(self) -> Groesse
```

Querschnitt **eines** Bügelschenkels.

#### Querkraftbewehrung.menge_text

```python
def menge_text(self) -> str
```

#### Querkraftbewehrung.grenzen

```python
def grenzen(self, zugkraft: bool) -> Tuple[int, int]
```

Die beiden Grenzwinkel in Grad -- siehe [[opencivil.querschnitt.platte#druckfeldgrenzen|druckfeldgrenzen]].

### druckfeldgrenzen

```python
def druckfeldgrenzen(alpha_min: int, alpha_max: int, zugkraft: bool) -> Tuple[int, int]
```

Die beiden Grenzwinkel der Druckdiagonalen in Grad, angepasst an das
Vorzeichen von `N_Ed` -- fuer die Buegel der Platte wie fuer die
Schubwaende der Querschnittsanalyse.

Bei Normalzug steilt sich die Druckdiagonale auf: `alpha_min` wird auf
40° gesetzt und `alpha_max` notfalls mitgehoben, damit der Bereich
nicht leer wird.

### Plattenquerschnitt

```python
@dataclass
class Plattenquerschnitt
```

Stahlbeton-Platte mit vier Bewehrungslagen.

`b` ist die betrachtete Breite; bei Platten ueblicherweise 1 m, dann sind
alle Schnittgroessen Werte pro Laufmeter.

- `name: str`
- `h: Groesse`
- `b: Groesse`
- `beton: Baustoff`
- `lagen: List[Bewehrungslage] = field(default_factory=list)`
- `ueberdeckung_unten: Groesse = field(default_factory=lambda: Groesse(30, MM))`
- `ueberdeckung_oben: Groesse = field(default_factory=lambda: Groesse(30, MM))`
- `d_max: Groesse = field(default_factory=lambda: Groesse(32, MM))` – Grösstkorndurchmesser -- geht in den Querkraftwiderstand ein.
- `einlagenhoehe: Groesse = field(default_factory=lambda: Groesse(0, MM))` – Höhe einer Einlage; verringert den Hebelarm d_v, wenn h/6 \< e \< d.
- `k_c: Groesse = field(default_factory=lambda: Groesse(K_C, EINHEITSLOS))` – Abminderung der Betondruckfestigkeit in der Druckdiagonalen.
- `querkraftbewehrung: Optional[Querkraftbewehrung] = None` – Bügel, sofern welche angegeben sind. `None` heisst: ohne.
- `praefix: Optional[str] = None`
- `definitionen: Dict[str, WertDef] = field(default_factory=dict, init=False)`
- `berechnungen: List[Berechnung] = field(default_factory=list, init=False)`
- `posten: List[Postenbezug] = field(default_factory=list, init=False)` – Die vorhandenen Posten, von der 1. Lage an, je Lage erst die Grundbewehrung.

#### Plattenquerschnitt.id_von

```python
def id_von(self, kurzname: str) -> str
```

#### Plattenquerschnitt.id_breite

```python
def id_breite(self, richtung: Richtung) -> str
```

Kennung der Breite, die fuer diese Tragrichtung gilt.

Eine Platte wird in y stets je Laufmeter nachgewiesen -- die Angabe
`b` beschreibt den Streifen in x. Wer beides dieselbe Breite nehmen
laesst, bekommt bei b != 1000 mm in y einen Widerstand, der zur
eingegebenen Bewehrung nicht passt.

#### Plattenquerschnitt.lagen_in_richtung

```python
def lagen_in_richtung(self, richtung: Richtung) -> List[Bewehrungslage]
```

#### Plattenquerschnitt.posten_in_richtung

```python
def posten_in_richtung(self, richtung: Richtung) -> List[Postenbezug]
```

#### Plattenquerschnitt.posten_der_lage

```python
def posten_der_lage(self, lage: Bewehrungslage) -> List[Postenbezug]
```

Grundbewehrung und Zulage der Lage, soweit vorhanden.

#### Plattenquerschnitt.richtungen_mit_bewehrung

```python
@property
def richtungen_mit_bewehrung(self) -> List[Richtung]
```

#### Plattenquerschnitt.staehle

```python
@property
def staehle(self) -> List[Baustoff]
```

#### Plattenquerschnitt.ins_rechenwerk

```python
def ins_rechenwerk(self, werk) -> 'Plattenquerschnitt'
```

#### Plattenquerschnitt.abschnitt

```python
@property
def abschnitt(self) -> Abschnitt
```

Ueberschrift, unter der die ganze Platte in der Herleitung steht.

#### Plattenquerschnitt.hat_buegel

```python
@property
def hat_buegel(self) -> bool
```

#### Plattenquerschnitt._querkraftbewehrung_aufbauen

```python
def _querkraftbewehrung_aufbauen(self, abschnitt: Abschnitt) -> None
```

Die Werte der Bügel -- Durchmesser, Teilungen, Grenzwinkel, k_c.

`k_c` entsteht auch ohne Bügel: er gehört zur Platte, nicht zur
Bewehrung, und eine Vorgabe, die je nach Eingabe da ist oder nicht,
macht die Rückverfolgung von der Bestückung abhängig.

Der Bügelquerschnitt ist eine **Formel** und keine Vorgabe: er wird aus
dem Durchmesser gerechnet, und wer ihn nachrechnen will, soll die
Rechnung sehen statt nur die Zahl.


## Konstanten

- `LAGENZAHL = 4` – Anzahl Lagen einer Platte. Bewusst fest -- eine Platte hat unten und oben je eine Haupt- und eine Querlage, mehr braucht es nicht, weniger waere ein Sonderfall mit leeren Lagen.
- `BREITE_Y_MM = 1000.0` – Breite, auf die sich eine y-Lage bezieht: in y wird immer je Laufmeter gerechnet, `b` ist der Streifen in x.
- `ALPHA_MIN = 30` – Vorgabe fuer die Neigung der Druckdiagonalen, in Grad.
- `ALPHA_MAX = 45`
- `ALPHA_ZUG = 40` – Bei einer Normalzugkraft steilt sich die Druckdiagonale auf. Beide Grenzen werden dann auf mindestens diesen Wert gehoben.
- `K_C = 0.55` – Vorgabe fuer den Abminderungsbeiwert der Betondruckfestigkeit in der Druckdiagonalen.
- `UEBERDECKUNGEN = 'Überdeckungen'` – Die beiden Kaesten, in denen die Plattenangaben zusammenstehen. Der erste traegt die Betonsorte im Namen: sie ist keine gerechnete Groesse und hat darum keine eigene Kette, an der sie haengen koennte -- als Aufschrift des Kastens gilt sie dagegen immer, denn eine Platte hat genau einen Beton.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wahl]]
- [[opencivil.core.wert]]
- [[opencivil.material.basis]]
- [[opencivil.material.betonstahl]]
- [[opencivil.querschnitt.lagenaufbau]]
- [[opencivil.querschnitt.zugseite]]

## Gebraucht von

- [[opencivil.bericht.zusammenfassung]]
- [[opencivil.bewehrungssuche.bewertung]]
- [[opencivil.bewehrungssuche.laengs]]
- [[opencivil.nachweis.biegung_normalkraft]]
- [[opencivil.nachweis.duktilitaet]]
- [[opencivil.nachweis.fehlende_bewehrung]]
- [[opencivil.nachweis.kennzahlen]]
- [[opencivil.nachweis.knicken]]
- [[opencivil.nachweis.mindestbewehrung]]
- [[opencivil.nachweis.querkraft]]
- [[opencivil.nachweis.querkraft_buegel]]
- [[opencivil.nachweis.spannungsbegrenzung]]
- [[opencivil.nachweis.sproedes_versagen]]
- [[opencivil.nachweis.verformung]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.aufbau.platte]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.platte]]
- [[opencivil.projekt.projekt]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.querschnitt.lagenaufbau]]
- [[opencivil.querschnitt.schubwaende]]
- [[opencivil.spannungsanalyse.modul]]
- [[opencivil.spannungsanalyse.platte]]
- [[opencivil.web.diagrammdaten]]

## Formeln aus diesem Modul

- [[Querschnitt eines Bügelschenkels]] · `Plattenquerschnitt._querkraftbewehrung_aufbauen`
