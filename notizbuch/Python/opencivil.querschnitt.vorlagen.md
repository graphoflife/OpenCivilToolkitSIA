---
erzeugt: acc3a474859c
art: modul
tags: [modul]
---
> [!abstract] opencivil/querschnitt/vorlagen.py
> Querschnitte zum Anfangen.
> Paket [[opencivil.querschnitt]] · [Quelltext](../../opencivil/querschnitt/vorlagen.py)

## VERANTWORTUNG

Sieben Vorlagen – Rechteck, T-Balken, Doppel-T, Trapez, Hohlkasten, Platte
mit Aufbeton und Kreis. Jede kennt ihre Masse samt Vorgabe und ihre Lagen
von Laengsstaeben und baut daraus [[opencivil.querschnitt.vorlagen#Teile|Teile]] in mm, den Ursprung unten
links: die Polygone, auf Wunsch die Bewehrung und die Schubwaende, und fuer
die Skizze im Zeichenfenster die Masslinien, die Staebe der Linien und je
Lage, was aus ihr wird.

Die Vorlagen stehen nur hier. Die Oberflaeche fragt nach ihnen: `vorlage`
fuer die Skizze, waehrend man tippt, `vorlage_einsetzen` zum Einsetzen.
Vorher stand das Rechteck zweimal da, in Python und in JS.

Was eine Vorlage nicht sagt, kommt aus den Vorgaben der Eintraege – der
Stahl, die Schnitte einer Schubwand. Eine Vorlage ist ein Anfang, kein
Entwurf.


## DIE BEWEHRUNG (Benutzer, 2026-11-27)

Je Lage ein Durchmesser und eine Teilung, beim Kreis Durchmesser und Anzahl.
Die Teilung ist ein Wunsch wie beim Zeichnen einer Stablinie: die Lage wird
eine Stablinie mit Teilung, gerundet auf den naechsten Abstand, der aufgeht
([[opencivil.querschnitt.geometrie#stablinie|stablinie]]). Die Ueberdeckung c_nom
misst bis zum aeussersten Stab, mit Schubwaenden also bis zum Buegel: die
Achse eines Stabs liegt c_nom + ⌀_b + ⌀/2 vom Rand, ohne Waende c_nom + ⌀/2.
Bei b = 300, c_nom = 35, Buegeln ⌀10 und unten ⌀20 mit s = 100 sind das
55 mm; dazwischen bleiben 190 mm, zwei Felder zu 95 mm, drei Staebe. Bis
2026-11-27 lag jede Achse 50 mm vom Rand («Achsabstand»), mit festen
Staeben: drei ⌀20 unten, zwei ⌀12 oben. So beginnt noch das Rechteck der
Skripte ([[opencivil.querschnitt.vorlagen#rechteck_der_skripte|rechteck_der_skripte]]): auf ihm bauen Skripte und Tests auf.

Die Schubwaende enden auf der Hoehe der Stabachsen – ohne Bewehrung dort,
wo sie laege. Ihre Buegel haben Durchmesser und Teilung ([[opencivil.querschnitt.vorlagen#Konstanten|BUEGEL]]).


## NACH VORGABE, NICHT NACHGESCHLAGEN (notizbuch/Notizen/TODO.md)

Im Trapez ist die Schubwand so dick wie die engste Stelle zwischen den
Lagen – die kleinere Breite gibt den kleineren Widerstand der Druckstrebe.


## DAS MASS

Ein [[opencivil.querschnitt.vorlagen#Mass|Mass]] steht fuer die Vorlagen hier und die der Stabquerschnitte
([[opencivil.stabwerk.querschnitte]]). Seine Grenze ist ein
[[opencivil.core.bereich#Bereich|Bereich]] wie die eines Feldes: derselbe
Satz, dieselbe Angabe fuer die Maske. Bis 2026-11-20 hatte jede Seite ihre
eigene Klasse, ihren eigenen Satz und im Fenster ihren eigenen Mindestwert –
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
sagt – oder, `ganzzahlig`, eine Anzahl, wie die der Staebe im Kreis.
Jedes ist groesser als null; was die Masse untereinander verlangen,
prueft die Vorlage.

- `schluessel: str`
- `symbol: str` – Wie es in der Skizze heisst – leer, wo es dort nicht steht.
- `beschriftung: str`
- `vorgabe: float`
- `einheit: Einheit = MM`
- `ganzzahlig: bool = False`
- `pfeil: float = 0.0` – Um wie viel ein Pfeil am Feld den Wert aendert – 0: um 1 bei einer Anzahl, sonst um 10.

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

Um wie viel ein Pfeil am Feld den Wert aendert – siehe [[opencivil.querschnitt.vorlagen#Mass|pfeil]].

#### Mass.grund

```python
def grund(self, wert: float) -> str
```

Was an `wert` nicht geht, als Satz mit Punkt – leer, wenn er geht.

#### Mass.als_dict

```python
def als_dict(self) -> Dict[str, Any]
```

Fuer den Katalog: wie es heisst, seine Vorgabe, der Schritt der
Pfeile und, was die Maske wie bei einem Feld braucht (`angabe`:
Einheit, Grenze, Satz, bei einer Anzahl `ganz`).

### Lage

```python
@dataclass(frozen=True)
class Lage
```

Eine Lage Laengsstaebe einer Vorlage – oder ihre Buegel: ein
Durchmesser und eine Teilung, beim Kreis die Anzahl. `name` steht vor
ihrer Zeile im Fenster und in den Saetzen, die sie betreffen.

- `schluessel: str`
- `name: str`
- `durchmesser: Mass`
- `menge: Mass`

#### Lage.masse

```python
@property
def masse(self) -> Tuple[Mass, Mass]
```

#### Lage.als_dict

```python
def als_dict(self) -> Dict[str, Any]
```

Fuer den Katalog: Name, die zwei Masse und wie sie in der Zeile heissen – ⌀ und s oder n.

### lage

```python
def lage(schluessel: str, name: str, durchmesser: float, teilung: float) -> Lage
```

Eine Lage mit Teilung; ihre Masse heissen nach dem ersten Buchstaben, ⌀_u und s_u.

### Teile

```python
@dataclass
class Teile
```

Was eine Vorlage baut – in mm, der Ursprung unten links.

- `polygone: List[dict] = field(default_factory=list)` – Je Polygon `punkte`, `aussparung` und `stoff`: leer fuer das Material der Vorlage.
- `staebe: List[dict] = field(default_factory=list)` – Je Stab `lage` und `durchmesser`.
- `stablinien: List[dict] = field(default_factory=list)` – Je Linie `von`, `bis` und die Felder, die von der Vorgabe abweichen.
- `schubwaende: List[dict] = field(default_factory=list)` – Je Wand `von`, `bis`, `dicke`, Durchmesser und Teilung ihrer Buegel.
- `bleche: List[dict] = field(default_factory=list)` – Je Profilblech `punkte`, seine Linie – nur in der Skizze einer Blechverbunddecke.
- `masslinien: List[dict] = field(default_factory=list)` – Nur fuer die Skizze: `von`, `bis`, `text` und `seite` ('unten', 'oben', 'links', 'rechts') – wohin sie neben dem Bauteil steht.
- `stabmitten: List[dict] = field(default_factory=list)` – Nur fuer die Skizze: die Staebe der Linien, je `lage` und `durchmesser`.
- `lagen: Dict[str, str] = field(default_factory=dict)` – Nur fuer das Fenster: je Lage, was aus ihr wird – «3 Stäbe, Abstand 95 mm».

#### Teile.als_dict

```python
def als_dict(self) -> dict
```

### masslinie

```python
def masslinie(von: Punkt, bis: Punkt, name: str, wert: float, seite: str) -> dict
```

Eine Masslinie der Skizze, «b = 300», auf der `seite` neben dem Bauteil – auch fuer ein Stahlprofil.

### umriss

```python
def umriss(punkte: Sequence[Punkt], stoff: str='') -> dict
```

Ein tragendes Polygon einer Vorlage – aus ihrem Material oder dem `stoff`, den sie zur Wahl stellt.

### loch

```python
def loch(punkte: Sequence[Punkt]) -> dict
```

Eine Aussparung einer Vorlage.

### kreispunkte

```python
def kreispunkte(mitte: Punkt, radius: float, ecken: int=KREISECKEN) -> List[Punkt]
```

`ecken` Punkte, gleich verteilt auf einem Kreis, der erste rechts, auf
Tausendstel gerundet: die Ecken eines Kreises als Vieleck – oder die
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

Ein T, der Flansch oben und mittig ueber dem Steg – der Ursprung unten links.

### t_pruefen

```python
def t_pruefen(b: float, h: float, b_w: float, h_f: float) -> Optional[str]
```

Was an einem T nicht geht – `None`, wenn alles geht. Ein Steg so breit
wie der Flansch gaebe ein Rechteck mit doppelten Ecken: dafuer gibt es das
Rechteck.

### _stabzahl

```python
def _stabzahl(punkte: Sequence[Punkt], abstand: float) -> str
```

Was aus einer Lage wird, in Worten: «3 Stäbe, Abstand 95 mm».

### Linie

```python
@dataclass(frozen=True)
class Linie
```

Die Achse einer Lage, von links nach rechts: die Staebe nach Teilung wie
auf einer gezeichneten Stablinie, die Enden besetzt.

- `von: Punkt`
- `bis: Punkt`

#### Linie.hat_platz

```python
@property
def hat_platz(self) -> bool
```

#### Linie.staebe

```python
def staebe(self, teilung: float) -> Tuple[Tuple[Punkt, ...], float]
```

Die Stabmitten und ihr Abstand – die Teilung gerundet, bis sie aufgeht.

#### Linie.einsetzen

```python
def einsetzen(self, teile: Teile, durchmesser: float, teilung: float, punkte: Sequence[Punkt]) -> None
```

### Ring

```python
@dataclass(frozen=True)
class Ring
```

Die Achsen der Staebe eines Kreises: gleich verteilt, der erste rechts.

- `mitte: Punkt`
- `radius: float`

#### Ring.hat_platz

```python
@property
def hat_platz(self) -> bool
```

#### Ring.staebe

```python
def staebe(self, anzahl: float) -> Tuple[Tuple[Punkt, ...], float]
```

Die Stabmitten und ihr Abstand, die Sehne zwischen zwei Nachbarn.

#### Ring.einsetzen

```python
def einsetzen(self, teile: Teile, durchmesser: float, anzahl: float, punkte: Sequence[Punkt]) -> None
```

### Form

```python
@dataclass
class Form
```

Was eine Form aus ihren Massen zeichnet: ihre Polygone, je Lage, wo ihre
Staebe liegen, ihre Schubwaende ohne Buegel und die Masslinien.

- `polygone: List[dict]`
- `reihen: Dict[str, Union[Linie, Ring]]`
- `schubwaende: List[dict] = field(default_factory=list)`
- `masslinien: List[dict] = field(default_factory=list)`

### Stoff

```python
@dataclass(frozen=True)
class Stoff
```

Ein zweites Material, das eine Vorlage zur Wahl stellt – der Aufbeton einer Platte.

- `schluessel: str`
- `beschriftung: str`
- `titel: str`
- `arten: Tuple[str, ...]` – Welche Materialarten es sein darf.

#### Stoff.als_dict

```python
def als_dict(self) -> Dict[str, Any]
```

### Vorlage

```python
@dataclass(frozen=True)
class Vorlage
```

Eine Vorlage: ihre Masse, ihre Lagen und wie sie daraus eine Form
zeichnet. `pruefen` sagt, was an den Massen untereinander nicht geht,
mit dem Abstand der Lagen vom Rand; ob die Staebe im Querschnitt Platz
haben, prueft [[opencivil.querschnitt.vorlagen#Vorlage.bauen|bauen]] fuer alle gleich.

- `schluessel: str`
- `name: str`
- `masse: Tuple[Mass, ...]`
- `lagen: Tuple[Lage, ...]`
- `form: Callable[[Mapping[str, float], Abstand], Form]`
- `pruefen: Callable[[Mapping[str, float], Abstand], Optional[str]]`
- `hat_waende: bool = True`
- `stoffe: Tuple[Stoff, ...] = ()`

#### Vorlage.alle_masse

```python
@property
def alle_masse(self) -> Tuple[Mass, ...]
```

Die Masse der Form, die Ueberdeckung, die der Lagen und die der Buegel.

#### Vorlage.bauen

```python
def bauen(self, masse: Optional[Mapping[str, float]]=None, bewehrung: bool=True, schubwaende: bool=True) -> Teile
```

Die Teile zu diesen Massen – was fehlt, nach Vorgabe; `masse`
traegt auch Ueberdeckung, Lagen und Buegel. Ohne `bewehrung` keine
Staebe und Linien, ohne `schubwaende` keine Waende. Passen die
Masse nicht zueinander oder die Staebe nicht in den Querschnitt, ein
`ValueError` mit dem Grund.

#### Vorlage._lage_einsetzen

```python
def _lage_einsetzen(self, teile: Teile, l: Lage, reihe: Union[Linie, Ring], werte: Mapping[str, float]) -> None
```

Die Staebe einer Lage – nur, wenn jeder ganz im Querschnitt liegt und keiner im naechsten.

### rechteck_der_skripte

```python
def rechteck_der_skripte() -> Teile
```

Das Rechteck, mit dem [[opencivil.projekt.projekt#Projekt.querschnittsanalyse|querschnittsanalyse]]
eine Analyse beginnt: 300 × 600 mm, drei ⌀20 unten und zwei ⌀12 oben,
ihre Achsen 50 mm vom Rand, ohne Schubwand. So sah die Vorlage
«Rechteck» bis 2026-11-27 aus; Skripte und Tests behalten so ihre Zahlen.

### _doppel_t_punkte

```python
def _doppel_t_punkte(m: Mapping[str, float]) -> List[Punkt]
```

Ein I aus zwei Gurten und dem Steg, alle mittig – der Ursprung unten links.

### _nichts

```python
def _nichts(m: Mapping[str, float], a: Abstand) -> Optional[str]
```

Masse, die untereinander nichts verlangen: ob die Staebe Platz haben, prueft das Bauen.

### _unten_oben

```python
def _unten_oben(unten: Tuple[float, float], oben: Tuple[float, float]) -> Tuple[Lage, Lage]
```

Die Lagen unten und oben, je ⌀ und s nach der Vorgabe ihrer Vorlage.

### vorlage

```python
def vorlage(schluessel: str) -> Vorlage
```

Die Vorlage zu einem Schluessel – `ValueError`, wenn es sie nicht gibt.


## Konstanten

- `KREISECKEN = 48` – Ecken eines Kreises. Sie liegen auf dem Kreis; was das an Flaeche kostet, rechnet die Geometrie wie bei jedem anderen Polygon.
- `UEBERDECKUNG = Mass('c_nom', 'c_nom', 'Überdeckung', 35.0)` – Die Ueberdeckung: vom Rand bis zum aeussersten Stab, mit Schubwaenden bis zum Buegel – ein Mass jeder Vorlage hier. Vorgabe 35 mm wie bei einer neuen Platte; bis 2026-11-27 stand hier der Achsabstand, 50 mm.
- `BUEGEL = Lage('buegel', 'Bügel', Mass('d_b', '⌀_b', 'Bügeldurchmesser', 10.0),…` – Die Buegel der Schubwaende, Vorgabe wie bei einer neuen Wand ([[opencivil.projekt.querschnittsanalyse#SchubwandEintrag|SchubwandEintrag]]).
- `Abstand = Callable[[str], float]` – Wie weit die Achsen einer Lage vom Rand liegen, nach ihrem Schluessel.
- `ZU_NIEDRIG = 'Der Querschnitt ist zu niedrig für Überdeckung, Bügel und Stäbe oben…` – Zu niedrig fuer Staebe und Wand: die Achsen oben und unten liegen uebereinander, die Wand dazwischen haette keine Laenge.
- `AUFBETON = Stoff('aufbeton', 'Aufbeton', 'Woraus der Aufbeton ist – die Platte d…` – Der Aufbeton einer Platte: ein Beton, der nicht der der Platte sein muss.
- `VORLAGEN = (Vorlage('rechteck', 'Rechteck', (Mass('b', 'b', 'Breite', 300.0), Ma…`

## Braucht

- [[opencivil.core.bereich]]
- [[opencivil.core.einheiten]]
- [[opencivil.querschnitt.geometrie]]

## Gebraucht von

- [[opencivil.pfahl.innen]]
- [[opencivil.projekt.beispiele_verbund]]
- [[opencivil.projekt.projekt]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.querschnitt.profilblech]]
- [[opencivil.stabwerk.querschnitte]]
- [[opencivil.stahlprofile.formen]]
- [[opencivil.stahlprofile.lage]]
- [[opencivil.stahlprofile.tabelle]]
- [[opencivil.web.api]]
- [[opencivil.web.dienst]]
