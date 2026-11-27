---
erzeugt: bd382251f232
art: modul
tags: [modul]
---
> [!abstract] opencivil/querschnitt/spannglieder.py
> Spannglieder im gezeichneten Querschnitt.
> Paket [[opencivil.querschnitt]] · [Quelltext](../../opencivil/querschnitt/spannglieder.py)

## VERANTWORTUNG

Ein Spannglied der Querschnittsanalyse ([[opencivil.querschnitt.spannglieder#Spannglied|Spannglied]]): wo es liegt,
aus welchem Erzeugnis und wie vielen davon oder mit welcher Flaeche, wie es
wirkt – und was daraus folgt: die Spannung nach dem Spannen und nach allen
Verlusten, die Vordehnung, die Kraft, sein Gesetz im Querschnitt und seine
Grenzdehnung. Jede Regel dazu steht hier, einmal: die Herleitung
([[opencivil.querschnitt.spannglieder#Spannglieder|Spannglieder]]), der Aufbau und das Zeichenfenster
([[opencivil.web.zeichengeometrie]]) fragen alle hier ([[opencivil.querschnitt.spannglieder#was_fehlt|was_fehlt]],
[[opencivil.querschnitt.spannglieder#aus_glied|aus_glied]], [[opencivil.querschnitt.spannglieder#vorspannung|vorspannung]], [[opencivil.querschnitt.spannglieder#grenzen_verletzt|grenzen_verletzt]]).


## DIE FLAECHE ([[opencivil.querschnitt.spannglieder#Flaechenangabe|Flaechenangabe]])

Aus einem Erzeugnis – ein Draht, eine Litze oder ein Stab, den Tabelle 7
fuer die Sorte nennt, mit seiner Flaeche aus der Tabelle, und wie viele
davon –, oder eingegeben, etwa fuer ein Glied aus zwoelf Litzen oder ein
Erzeugnis, das die Tabelle nicht fuehrt. Dann zaehlt nur noch die Art: von
ihr haengt E_p ab, 195 000 N/mm² fuer Litzen, 200 000 fuer Draehte und
Staebe (3.3.2.4). Die Art muss es in der Sorte geben, wie das Erzeugnis.


## DIE VORSPANNUNG ALS WIDERSTAND

Die Zugkraft im Spannstahl zaehlt zum Widerstand (SIA 262:2025, 4.1.5.5.1):
die Lastfaelle sind ohne die Vorspannung einzugeben. Mit Verbund traegt ein
Glied mit seiner Vordehnung (4.1.5.1.5), ueber der Dehnung `eps` des
Querschnitts an seiner Stelle:

```python
sigma_p(eps) = sigma_Figur17(eps + eps_p)        eps_p = sigma_pinf / E_p
```

Ohne Verbund wirkt die Kraft nach allen Verlusten, ohne Zuwachs (4.1.5.1.6):
`sigma_p = sigma_pinf`, gleich welche Dehnung – und keine Grenzdehnung.


## SCHLAFF MIT RESTFESTIGKEIT

Wer die Vorspannung schon als Einwirkung angesetzt hat (4.1.5.5.2), zaehlt
im Widerstand nur, was das Glied darueber hinaus traegt: das Gesetz mit
Vordehnung, um `sigma_pinf` gesenkt. Es beginnt bei null und endet bei
`f_pd - sigma_pinf`; gedrueckt verliert es bis `sigma_pinf`. Ohne
Verbund bleibt davon nichts.


## DIE SPANNUNGEN

Eingegeben sind zwei Faktoren, je hoechstens 1: `sigma_p0 = k_p0 f_pk`
und `sigma_pinf = k_pinf sigma_p0`. Vorgabe `k_p0 = 0.70` und ``k_pinf
= 0.85`` – nach Vorgabe, nicht nachgeschlagen (Benutzer, 2026-11-25). Die
Verluste haengen am Bauwerk (4.1.5.3); die Vorgabe ersetzt ihre Rechnung
nicht. Bis 2026-11-27 waren die Spannungen selbst die Felder, leer die
Vorgabe: so blieb die Zahl nach einem Wechsel der Sorte stehen, und
`sigma_pinf` durfte `sigma_p0` nicht uebersteigen – mit einem Faktor
bis 1 kann es das nicht. Die Vordehnung ist `sigma_pinf/E_p` mit dem
Modul der Art: die Stauchung des Betons beim Vorspannen faellt weg – nach
Vorgabe, nicht nachgeschlagen.


## DIE NEIGUNG

Ein Glied mit Vordehnung darf gegen die Stabachse geneigt sein, um
`beta_p` in der lotrechten Ebene (Figur 18). Seine lotrechte Kraft
`F · sin beta_p` zaehlt in der Querkraft ([[opencivil.querschnitt.spannglieder#lotrecht|lotrecht]]):
`beta_p > 0` heisst, sie wirkt wie ein positives `V_z`. Wirkt sie in
einem Lastfall wie dessen `V_z`, traegt sie es mit, mit `F = P_inf`
([[opencivil.querschnitt.spannglieder#guenstig|guenstig]]; 4.3.3.4.8, Gleichung (50)); wirkt sie entgegen, kommt
sie dazu, mit der groessten Kraft im Glied (4.3.3.4.9) – was der
Nachweis der Schubwaende rechnet
([[opencivil.nachweis.schubwandnachweis]]). Schlaff zaehlt die Neigung
nicht: dort steht die Vorspannung schon samt ihr in den Lastfaellen
(Benutzer, 2026-11-25). Im Biegewiderstand und im Gebrauch zaehlt ein
geneigtes Glied, als laege es laengs: `cos beta_p` ist bis
[[opencivil.querschnitt.spannglieder#Konstanten|GRENZE_NEIGUNG]] mindestens 0.94 – nach Vorgabe, nicht
nachgeschlagen.


## DIE GRENZEN

Nach dem Spannen `sigma_p0 <= min(0.75 f_pk; 0.85 f_p0.1k)` (4.1.5.2.2,
Gleichung (22)), nach allen Verlusten `sigma_pinf >= 0.45 f_pk`
(4.1.5.2.3). Wer sie verletzt, bekommt einen roten Hinweis am Glied und
in der Herleitung; gerechnet wird mit seinen Zahlen.


## EINHEITEN

Lage und Durchmesser in mm, Flaechen in mm², die Spannungen in N/mm² –
wie in der Zeichnung. Die Gesetze rechnen in SI.

## Inhalt

### Spannwirkung

```python
class Spannwirkung(Wahl)
```

Wie ein Spannglied im Widerstand zaehlt – siehe Dateikopf.

- `VORDEHNUNG = 'vordehnung'`
- `RESTFESTIGKEIT = 'restfestigkeit'`

#### Spannwirkung.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Spannwirkung.kurz

```python
@property
def kurz(self) -> str
```

Im Schalter des Zeichenfensters, wo der Platz knapp ist.

#### Spannwirkung.mit_neigung

```python
@property
def mit_neigung(self) -> bool
```

Ob die Neigung zaehlt – nur mit Vordehnung, siehe Dateikopf.

#### Spannwirkung.erklaerung

```python
@property
def erklaerung(self) -> str
```

### Verbund

```python
class Verbund(Wahl)
```

Ob das Glied mit dem Beton verbunden ist – siehe Dateikopf.

- `MIT = 'mit'`
- `OHNE = 'ohne'`

#### Verbund.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Verbund.kurz

```python
@property
def kurz(self) -> str
```

Im Schalter hinter dem Wort «Verbund».

#### Verbund.erklaerung

```python
@property
def erklaerung(self) -> str
```

### Flaechenangabe

```python
class Flaechenangabe(Wahl)
```

Woher die Flaeche eines Glieds kommt – siehe Dateikopf.

- `ERZEUGNIS = 'erzeugnis'`
- `FLAECHE = 'flaeche'`

#### Flaechenangabe.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Flaechenangabe.erklaerung

```python
@property
def erklaerung(self) -> str
```

### vorspannung

```python
def vorspannung(f_pk: float, anteil_p0: float, anteil_pinf: float) -> Tuple[float, float]
```

`sigma_p0 = k_p0 f_pk` und `sigma_pinf = k_pinf sigma_p0` – in der
Einheit von `f_pk`.

### grenze_nach_spannen

```python
def grenze_nach_spannen(f_pk: float, f_p01k: float) -> float
```

`min(0.75 f_pk; 0.85 f_p0.1k)` – Gleichung (22).

### grenzen_verletzt

```python
def grenzen_verletzt(p0: float, pinf: float, f_pk: float, f_p01k: float) -> List[str]
```

Was an den Spannungen eines Glieds nicht stimmt, je ein Satz ohne Punkt
– alles in N/mm². Leer, wenn alles stimmt.

### was_fehlt

```python
def was_fehlt(g: Mapping) -> str
```

Warum ein Glied der Beschreibung noch nicht rechnet, als Satzteil – leer,
wenn es rechnet. `g["stahl"]` ist sein Spannstahl als Baustoff. Es fehlt
nur eine Wahl: ein Erzeugnis, das Tabelle 7 fuer die Sorte nennt, oder,
wo die Flaeche eingegeben ist, eine Art, die es in ihr gibt – etwa nach
dem Wechsel zu Y1030, das es nur in Staeben gibt.

### _stellen

```python
def _stellen(zahl: float) -> int
```

Mit so vielen Stellen steht ein Faktor in der Herleitung: zwei, mehr nur wo er sie hat.

### geneigt

```python
def geneigt(g: 'Spannglied') -> bool
```

Ob ein Glied mit seiner Neigung in der Querkraft zaehlt – siehe Dateikopf.

### lotrecht

```python
def lotrecht(kraft: float, neigung: float) -> float
```

Die lotrechte Kraft eines Glieds, das `kraft` traegt und um `neigung` Grad geneigt ist.

### guenstig

```python
def guenstig(neigung: float, V_z: float) -> bool
```

Ob die lotrechte Kraft eines Glieds die Querkraft `V_z` mittraegt:
beide gleich gerichtet. Ohne `V_z` kommt sie dazu – unguenstig.

### flaechendurchmesser

```python
def flaechendurchmesser(flaeche: float) -> float
```

Der Durchmesser eines Kreises mit dieser Flaeche – so gross zeichnet sich ein Glied.

### VorgedehnterSpannstahl

```python
@dataclass(frozen=True)
class VorgedehnterSpannstahl(Gesetz)
```

Ein Spannglied mit Verbund, ueber der Dehnung des Querschnitts an seiner
Stelle: das Gesetz des Spannstahls (Figur 17), um die Vordehnung
verschoben (4.1.5.1.5). Bei `eps = 0` traegt es `sigma_pinf`.

- `NAME = IM_QUERSCHNITT`
- `WORT = 'mit Vordehnung'`
- `REFERENZ = f'{REFERENZ_VORDEHNUNG}; {REFERENZ_WIDERSTAND}; 4.2.3.3, Figur 17'`
- `ROLLEN = ('f_p', 'E_p', 'eps_ud', 'eps_p')`
- `WERTTITEL = 'Werte des Spannglieds'`
- `stahl: Spannstahlgesetz`
- `eps_p: float` – Die Vordehnung, positiv.

#### VorgedehnterSpannstahl.abzug

```python
def abzug(self) -> float
```

Was vom Gesetz abgeht – mit Vordehnung nichts.

#### VorgedehnterSpannstahl.eps_yd

```python
@property
def eps_yd(self) -> float
```

Die Dehnung des Querschnitts, bei der das Glied zu fliessen beginnt.

#### VorgedehnterSpannstahl.eps_ud

```python
@property
def eps_ud(self) -> float
```

Die Dehnung des Querschnitts, bei der das Glied reisst.

#### VorgedehnterSpannstahl.formel

```python
def formel(self, werte: Werte) -> str
```

#### VorgedehnterSpannstahl.latex

```python
def latex(self, zug: str='f_{pd}') -> str
```

### Restfestigkeit

```python
@dataclass(frozen=True)
class Restfestigkeit(VorgedehnterSpannstahl)
```

Ein schlaffes Spannglied mit Verbund: was es ueber `sigma_pinf` hinaus
traegt, wenn die Vorspannung schon als Einwirkung zaehlt (4.1.5.5.2) –
das Gesetz mit Vordehnung, um `sigma_pinf` gesenkt.

- `WORT = 'schlaff mit Restfestigkeit'`
- `REFERENZ = f'{REFERENZ_EINWIRKUNG}; {REFERENZ_VORDEHNUNG}; 4.2.3.3, Figur 17'`
- `ROLLEN = ('f_p', 'E_p', 'eps_ud', 'eps_p', 'sigma_pinf')`
- `sigma_pinf: float = 0.0` – Die Spannung nach allen Verlusten in N/m² – sie zaehlt schon als Einwirkung.

#### Restfestigkeit.abzug

```python
def abzug(self) -> float
```

#### Restfestigkeit.latex

```python
def latex(self, zug: str='f_{pd}') -> str
```

### FesteSpannung

```python
@dataclass(frozen=True)
class FesteSpannung(Gesetz)
```

Ein Spannglied ohne Verbund: die Spannung nach allen Verlusten, gleich
welche Dehnung der Querschnitt an seiner Stelle hat (4.1.5.1.6). Schlaff
angesetzt ist sie null – das Glied traegt nichts bei.

- `NAME = IM_QUERSCHNITT`
- `WORT = 'ohne Verbund'`
- `REFERENZ = REFERENZ_OHNE_VERBUND`
- `ROLLEN = ('sigma_pinf',)`
- `WERTTITEL = 'Werte des Spannglieds'`
- `sigma: float` – Die feste Spannung in N/m².
- `eps_yd: ClassVar[float] = math.inf` – Es fliesst nie: seine Kraft haengt an keiner Dehnung.

#### FesteSpannung.formel

```python
def formel(self, werte: Werte) -> str
```

#### FesteSpannung.protokoll

```python
def protokoll(self, p: Protokoll, werte: Werte, *, titel: str, basis: str='') -> None
```

### Spannglied

```python
@dataclass(frozen=True)
class Spannglied(Bewehrungselement)
```

Ein Spannglied der Zeichnung – `von` und `bis` sind seine Lage,
`flaeche` ist `anzahl` mal die des Erzeugnisses (Tabelle 7) oder
eingegeben. Die Spannungen stehen als Faktoren da, siehe Dateikopf.

- `art: Erzeugnisart` – Draht, Litze oder Stab: daran haengt E_p (3.3.2.4).
- `erzeugnis: Optional[Erzeugnis]` – Die Zeile von Tabelle 7 – `None`, wo die Flaeche eingegeben ist.
- `anzahl: int` – Wie viele Stuecke des Erzeugnisses; wo die Flaeche eingegeben ist, zaehlt sie nicht.
- `wirkung: Spannwirkung`
- `verbund: Verbund`
- `anteil_p0: float` – `k_p0`: `sigma_p0 = k_p0 f_pk`.
- `anteil_pinf: float` – `k_pinf`: `sigma_pinf = k_pinf sigma_p0`.
- `neigung: float` – `beta_p` in Grad, siehe Dateikopf.
- `vorgespannt: ClassVar[bool] = True`

#### Spannglied.punkte

```python
@property
def punkte(self) -> Tuple[Tuple[float, float], ...]
```

#### Spannglied.lage

```python
@property
def lage(self) -> Mathe
```

#### Spannglied.stuecke

```python
@property
def stuecke(self) -> str
```

Woraus es besteht: «4 × Litze ⌀15.7» – mit eingegebener Flaeche die Art, «Litzen».

#### Spannglied.bezeichnung

```python
@property
def bezeichnung(self) -> str
```

Wie Tabelle 7 es nennt, «Y1860S7-15.7» – mit eingegebener Flaeche die Art, «Litzen».

#### Spannglied.menge

```python
@property
def menge(self) -> Zelle
```

#### Spannglied.kurzmenge

```python
@property
def kurzmenge(self) -> Zelle
```

#### Spannglied.rissdurchmesser

```python
@property
def rissdurchmesser(self) -> float
```

Nur der Form halber: die Rissbreite pruefen die Staebe aus Betonstahl.

#### Spannglied.durchmesser

```python
@property
def durchmesser(self) -> float
```

Wie gross es sich zeichnet: ein Kreis mit seiner Flaeche ([[opencivil.querschnitt.spannglieder#flaechendurchmesser|flaechendurchmesser]]).

#### Spannglied.als_bewehrung

```python
def als_bewehrung(self, stahl: int, verdraengt: Verdraengt) -> List[Bewehrung]
```

`stahl` ist der Index seines eigenen Werkstoffs, nicht der seines Spannstahls.

#### Spannglied.stahlflaechen

```python
def stahlflaechen(self) -> Flaechen
```

Ein Quadrat seiner Flaeche, wie ein Stab – im Verbund rechnet das Werkzeug keins.

### aus_glied

```python
def aus_glied(g: Mapping) -> Spannglied
```

Ein Spannglied der Beschreibung ([[opencivil.projekt.querschnittsanalyse#QuerschnittsanalyseEintrag.elemente|QuerschnittsanalyseEintrag.elemente]]),
mit seinem Spannstahl als Baustoff unter `stahl` – eines, dem nichts
fehlt ([[opencivil.querschnitt.spannglieder#was_fehlt|was_fehlt]]): sein Erzeugnis kommt aus Tabelle 7.

### Spannglieder

```python
class Spannglieder(Prozedur)
```

Die Spannglieder einer Analyse: je Glied `A_p`, `sigma_p0`,
`sigma_pinf`, `eps_p` und `P_inf` als Werte des Rechenwerks, mit
ihrer Herleitung – und daraus je Glied sein Werkstoff im Querschnitt
([[opencivil.querschnitt.spannglieder#Spannglieder.werkstoffe|werkstoffe]]). Die Nachweise lesen die Werte ueber
[[opencivil.querschnitt.spannglieder#Spannglieder.gliedbezuege|gliedbezuege]], damit jede Spannkraft rueckverfolgbar bleibt.

#### Spannglieder.index

```python
def index(self, g: Spannglied) -> str
```

Was an den Symbolen eines Glieds unten steht: «,2» – bei nur einem nichts.

#### Spannglieder.gliedbezuege

```python
def gliedbezuege(self, kurze: Sequence[str]=('sigma_pinf', 'eps_p', 'P_inf'), glieder: Optional[Sequence[Spannglied]]=None) -> List[Eingabebezug]
```

Was ein Nachweis von den Gliedern liest, als `{kurz}__{kennung}` –
jeder `sigma_pinf`, `eps_p` und `P_inf` von allen; wer mehr
braucht, nennt die Werte und die Glieder.

#### Spannglieder.spannkraefte

```python
def spannkraefte(self) -> List[Tuple[Spannglied, str]]
```

Die Glieder, deren Kraft den Beton schon ohne Last drueckt – die mit
Vordehnung, mit oder ohne Verbund –, je mit der ID ihres `P_inf`.
Schlaff angesetzt steht die Vorspannung schon in den Lastfaellen.

#### Spannglieder.werkstoffe

```python
def werkstoffe(self, wert: Callable[[str], float], wahl) -> List[Werkstoff]
```

Je Glied sein Werkstoff, in der Folge der Glieder: das Gesetz nach
Wirkung und Verbund, mit der Fliessgrenze des Wertesatzes seines
Stahls und dem Modul seines Erzeugnisses. `wert` liefert zu einer
Wert-ID die Zahl in SI.

#### Spannglieder.gesetze_protokollieren

```python
def gesetze_protokollieren(self, p: Protokoll, e: Eingaben, wahl, werkstoffe: Sequence[Werkstoff], *, titel: Callable[[Spannglied], str], basis: str) -> None
```

Je Glied sein Gesetz, mit seinen Werten – `werkstoffe` die von
[[opencivil.querschnitt.spannglieder#Spannglieder.werkstoffe|werkstoffe]], `titel` wie die Zeile eines Glieds heisst.

#### Spannglieder.rechne

```python
def rechne(self, e: Eingaben, p: Protokoll) -> Dict[str, Groesse]
```

#### Spannglieder._glied

```python
def _glied(self, e: Eingaben, p: Protokoll, g: Spannglied, ergebnis: Dict[str, Groesse]) -> List[Zelle]
```

Die Werte eines Glieds, hergeleitet – und seine Zeile der Tabelle.


## Konstanten

- `REFERENZ_WIDERSTAND = 'SIA 262:2025, 4.1.5.5.1'`
- `REFERENZ_VORDEHNUNG = 'SIA 262:2025, 4.1.5.1.5'`
- `REFERENZ_OHNE_VERBUND = 'SIA 262:2025, 4.1.5.1.6'`
- `REFERENZ_EINWIRKUNG = 'SIA 262:2025, 4.1.5.5.2'`
- `REFERENZ_NACH_SPANNEN = 'SIA 262:2025, 4.1.5.2.2, (22)'`
- `REFERENZ_NACH_VERLUSTEN = 'SIA 262:2025, 4.1.5.2.3'`
- `REFERENZ_VERLUSTE = 'SIA 262:2025, 4.1.5.3'`
- `REFERENZ_GUENSTIG = 'SIA 262:2025, 4.3.3.4.8, (50)'`
- `REFERENZ_UNGUENSTIG = 'SIA 262:2025, 4.3.3.4.9'`
- `NACH_VORGABE = 'nach Vorgabe, nicht nachgeschlagen'`
- `ANTEIL_SPANNEN = 0.7` – `k_p0`, womit ein neues Glied beginnt: `sigma_p0 = 0.70 f_pk` – nach Vorgabe, nicht nachgeschlagen (Benutzer, 2026-11-25).
- `ANTEIL_NACH_VERLUSTEN = 0.85` – `k_pinf`, womit ein neues Glied beginnt: `sigma_pinf = 0.85 sigma_p0` – nach Vorgabe, nicht nachgeschlagen (Benutzer, 2026-11-25).
- `FAKTOREN = ({'feld': 'anteil_p0', 'vor': 'σ_p0 =', 'nach': '· f_pk', 'spannung':…` – Wie die Faktoren im Zeichenfenster stehen – «σ_p0 = [0.70] · f_pk = 1302 N/mm²»: vor und nach dem Feld, und welche Spannung des Glieds die Zeile dahinter nennt, sobald der Kern sie kennt.
- `GRENZE_F_PK = 0.75` – Gleichung (22): `sigma_p0 <= min(0.75 f_pk; 0.85 f_p0.1k)`.
- `GRENZE_F_P01K = 0.85`
- `MINDESTENS_F_PK = 0.45` – 4.1.5.2.3: nach allen Verlusten mindestens `0.45 f_pk`.
- `GRENZE_NEIGUNG = 20.0` – Wie steil ein Glied hoechstens liegt, in Grad, nach oben wie nach unten: bis dahin zaehlt es im Biegewiderstand laengs, `cos 20° = 0.94` – nach Vorgabe, nicht nachgeschlagen.
- `KENNWERTE = ('f_pk', 'f_p01k', 'E_p', 'E_p_litze')` – Die Kennwerte des Spannstahls, die die Herleitung der Glieder liest.
- `NEIGUNG_ERKLAERT = {'titel': f'Neigung gegen die Stabachse in Grad, höchstens {GRENZE_NE…` – Was das Feld der Neigung im Zeichenfenster sagt: als Titel, in einer Zeile darunter – und an seiner Stelle, wo sie nicht zaehlt.
- `DEHNUNG_AM_GLIED = 'Bei einem Spannglied ist ε die Dehnung des Betons an seiner Stelle: …` – Was eine Tabelle oder ein Bild sagt, das die Dehnung eines Glieds zeigt: es ist die des Betons an seiner Stelle, nicht die des Stahls.
- `FLAECHE = 'Querschnitt eines Spannglieds'` – Die Seiten im Notizbuch, je Groesse eine: Querschnitt, Spannungen, Vordehnung und Kraft eines Glieds, die Grenzen seiner Spannung, sein Gesetz im Querschnitt – dieses eine fuer alle drei Arten.
- `GESPANNT = 'Spannung im Spannglied'`
- `VORDEHNUNG = 'Vordehnung eines Spannglieds'`
- `SPANNKRAFT = 'Spannkraft eines Spannglieds'`
- `GRENZEN = 'Grenzen der Spannung im Spannstahl'`
- `IM_QUERSCHNITT = 'Spannglied im Querschnitt'`

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wahl]]
- [[opencivil.core.wert]]
- [[opencivil.material.basis]]
- [[opencivil.material.spannstahl]]
- [[opencivil.querschnitt.bewehrungselemente]]
- [[opencivil.querschnitt.interaktion]]
- [[opencivil.querschnitt.werkstoffgesetz]]

## Gebraucht von

- [[opencivil.nachweis.schiefe_biegung]]
- [[opencivil.nachweis.schubwandnachweis]]
- [[opencivil.projekt.aufbau.querschnittsanalyse]]
- [[opencivil.projekt.frueher]]
- [[opencivil.projekt.spannglieder]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.spannungsanalyse.bild]]
- [[opencivil.web.api]]
- [[opencivil.web.zeichengeometrie]]

## Formeln aus diesem Modul

- [[Grenzen der Spannung im Spannstahl]] · `Spannglieder._glied`
- [[Grenzen der Spannung im Spannstahl]] · `Spannglieder.rechne`
- [[Querschnitt eines Spannglieds]] · `Spannglieder._glied`
- [[Spannkraft eines Spannglieds]] · `Spannglieder._glied`
- [[Spannkraft eines Spannglieds]] · `Spannglieder.rechne`
- [[Spannung im Spannglied]] · `Spannglieder._glied`
- [[Spannung im Spannglied]] · `Spannglieder.rechne`
- [[Vordehnung eines Spannglieds]] · `Spannglieder._glied`
