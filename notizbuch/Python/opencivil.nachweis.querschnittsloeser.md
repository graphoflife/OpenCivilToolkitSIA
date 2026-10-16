---
erzeugt: 76cdda00e6ee
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/querschnittsloeser.py
> Dehnungsebene zu gegebenen Schnittgrössen.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/querschnittsloeser.py)

## VERANTWORTUNG

Sucht zu `(N_Ed, M_Ed)` die Dehnungsebene `(eps_m, chi)`, die den
Querschnitt ins Gleichgewicht bringt -- und liefert damit die Spannungen in
jeder Lage.


## WARUM EIN EIGENER LOESER

Mit Normalkraft gibt es keine geschlossene Loesung mehr. Zwei Unbekannte, zwei
Gleichgewichtsbedingungen; das Werkstoffgesetz des Betons ist nichtlinear. Ein
fremdes Paket kaeme dafuer nicht in Frage: dieses Werkzeug laeuft auch im
Browser ueber Pyodide, ohne Abhaengigkeiten.


## DAS VERFAHREN

Zwei ineinandergeschachtelte Bisektionen. Bei festem `chi` waechst
`N(eps_m)` monoton -- mehr Dehnung heisst mehr Zug --, also laesst sich
`eps_m` eindeutig so waehlen, dass `N = N_Ed`. Damit wird `M` eine
Funktion von `chi` allein, und die waechst ebenfalls monoton. Die aeussere
Bisektion sucht darin die Kruemmung.

**Beide Bisektionen brauchen einen gueltigen Dehnungsbereich.** Jenseits der
Bruchdehnungen geben die Werkstoffgesetze null zurueck; dort ist nichts mehr
monoton, und die Suche findet Scheinloesungen. Das Fenster fuer `eps_m`
haengt darum von `chi` ab -- siehe [[opencivil.nachweis.querschnittsloeser#Querschnittsloeser|Querschnittsloeser._fenster]].

Beide Bisektionen sind robust: kein Startwert kann danebenliegen, kein
Newton-Schritt kann davonlaufen. Sie kosten mehr Auswertungen als ein
Newton-Verfahren -- bei rund 60 Fasern und 60 Halbierungen ist das
unbedeutend.


## WAS IN DIE MITSCHRIFT GEHOERT

Nicht die Suche, sondern die **Probe**. Geschrieben wird die gefundene Ebene
und der Nachweis, dass mit ihr `N_int = N_Ed` und `M_int = M_Ed`
herauskommt. Wer das nachrechnen will, integriert zwei Mal ueber die Hoehe --
das geht von Hand. Den Weg dorthin muss er nicht nachvollziehen. Dasselbe
Vorgehen wie bei der Neigungssuche des Querkraftnachweises.

Die Probe rechnet der Loeser auch selbst ([[opencivil.nachweis.querschnittsloeser#Faserloeser._mit_probe|Faserloeser._mit_probe]]):
die Suchen enden, wo ihr Fenster eng genug ist, und erst die Probe sagt, ob
dort `N_Ed` und `M_Ed` herauskommen. Springt ein Gesetz -- der
Spannungsblock --, endet eine Suche auch an einem Sprung, wo es keine Ebene
gibt. Dann ist sie verfehlt ([[opencivil.nachweis.querschnittsloeser#Ebene|Ebene.verfehlt]]), und der Nachweis sagt
das statt der Probe. Bis 2026-10-15 stand die Probe dort trotzdem, mit
Haekchen: an einer Platte h = 250 mm, ⌀12 oben und unten, unter
N = -600 kN und M = 14.5 kNm erzeugte die Ebene der 0.85·x-Vereinfachung
mit charakteristischen Werten -170 kN und 1.4 kNm.


## VORZEICHEN

```
eps > 0   Zug
N   > 0   Zug
M   > 0   Zug unten
```
`chi` ist die Kruemmung: `eps(z) = eps_m + chi * (z - h/2)`, mit `z` ab
Oberkante. Ein positives `chi` zieht also unten.


## JEDER QUERSCHNITT AUS FASERN

Die Suche braucht nur zweierlei: die Fasern mit ihren Kraeften und die
Dehnungsgrenzen, in denen jede gilt. Das steht in [[opencivil.nachweis.querschnittsloeser#Faserloeser|Faserloeser]]. Die
Platte baut beides aus Hoehe, Breite und Lagen ([[opencivil.nachweis.querschnittsloeser#Querschnittsloeser|Querschnittsloeser]]),
der gezeichnete Querschnitt je Zugseite aus seinen Polygonen
([[opencivil.querschnitt.schnittanalyse]]). Dort ist `eps_m` die Dehnung
im Schwerpunkt statt auf halber Hoehe; `oben` und `unten` sagen, wo die
Raender liegen.


## EINHEITEN

Alles in SI-Basis.

## Inhalt

### Stahllage

```python
@dataclass(frozen=True)
class Stahllage
```

Eine Bewehrungslage samt ihrem Stahl -- die eine Gestalt, in der jede
Rechnung am Plattenquerschnitt eine Lage sieht: der Loeser, die genaue
Resistenzlinie, die Handrechnung, die Spannung-Dehnung-Analyse. Gebaut
wird sie an einer Stelle,
[[opencivil.nachweis.rechenwahl#stahllagen|stahllagen]].

- `a_s: float` – Querschnitt in m^2, bezogen auf die betrachtete Breite.
- `z: float` – Tiefenlage ab Oberkante, in m.
- `stahl: Stahlgesetz` – Der Stahl dieser Lage, mit den Festigkeiten des Wertesatzes -- `f_yd` oder `f_yk` im Feld `f_yd`. Jede Lage traegt ihren eigenen: der Editor laesst je Seite einen anderen Stahl waehlen. Bis 2026-10-12 bekam der Loeser einen einzigen, den der ersten Lage, und unten B700B mit oben B500B rechnete die obere Lage mit f_yd = 609 statt 435 N/mm².
- `sorte: str = ''` – Die Kennung des Stahls (`s1`) -- unter ihr heissen seine Eingaben.
- `nummer: int = 0` – Nur zur Zuordnung in der Mitschrift.
- `von_unten: Optional[bool] = None` – Ob die Lage zur unteren Seite gehoert -- bei der Platte die 1. und 2. Lage ([[opencivil.nachweis.querschnittsloeser#Stahllage|Bewehrungslage.von_unten]]). Die Handrechnung fasst je Seite zusammen ([[opencivil.nachweis.querschnittsloeser#lagen_je_seite|lagen_je_seite]]); ohne Angabe entscheidet die Tiefe.
- `text: str = ''` – Wie die Lage in Tabellen heisst -- «2. Lage Grundbewehrung».

### lagen_je_seite

```python
def lagen_je_seite(lagen: Sequence[Stahllage], h: float) -> List[Stahllage]
```

Je Seite eine Lage, im Schwerpunkt ihrer Flaechen -- wie die Handrechnung.

Die Seite sagt [[opencivil.nachweis.querschnittsloeser#Stahllage|Stahllage.von_unten]], sonst die Tiefe gegen
`h/2`. Unten zuerst; eine Seite ohne Flaeche faellt weg. Die
zusammengefasste Lage behaelt den Stahl ihrer Seite. Zwei verschiedene
Staehle auf einer Seite liessen sich nicht zu einer Lage machen -- die
Platte hat sie nicht, je Seite und Richtung liegt eine Lage, und Grund-
und Zulage teilen ihren Stahl.

### bruchdehnung

```python
def bruchdehnung(lagen: Sequence[Stahllage]) -> float
```

Wie weit das Suchfenster im Zug reicht: bis zur kleinsten Bruchdehnung
der Lagen. Jenseits davon gaebe das Gesetz dieser Lage null zurueck, und
die Bisektion faende Scheinloesungen. Bei einer Sorte ist es ihr
`eps_ud`; bei zweien die kleinere -- das Fenster gilt an beiden
Raendern. Ohne Lage gilt [[opencivil.nachweis.querschnittsloeser#Konstanten|EPS_ZUG]].

### Ebene

```python
@dataclass(frozen=True)
class Ebene
```

Die gefundene Dehnungsebene samt Proberechnung.

- `eps_m: float` – Dehnung auf halber Hoehe.
- `chi: float` – Kruemmung in 1/m.
- `N_int: float`
- `M_int: float` – Was die Ebene tatsaechlich erzeugt -- die Probe.
- `sigma_s: Tuple[float, ...]` – Stahlspannung je Lage, in Pa.
- `eps_s: Tuple[float, ...]` – Stahldehnung je Lage.
- `konvergiert: bool = True`
- `verfehlt: bool = False` – Die Suche lief zu Ende, aber ihre Ebene erzeugt die Einwirkung nicht: sie blieb an einem Sprung haengen, wie ihn der Spannungsblock hat. Bei viel Druck und wenig Moment liegt der Block immer ganz an einem Rand und gibt mehr Moment, als einwirkt -- dazwischen gibt es keine Ebene. Dann ist `konvergiert` falsch, und `eps_m` und `chi` sind die Stelle des Sprungs, durch die eine Linie laeuft ([[opencivil.spannungsanalyse#moment_kruemmung|moment_kruemmung]]).

#### Ebene.bei

```python
def bei(self, z: float, h: float) -> float
```

Die Dehnung in der Tiefe `z`.

### wirksamer_modul

```python
def wirksamer_modul(E_cm: float, phi: float) -> float
```

`E_c,eff = E_cm / (1 + phi)` -- das Kriechen weicht den Beton auf.

### protokoll_wirksamer_modul

```python
def protokoll_wirksamer_modul(p, E_cm, phi, basis: str, *, titel: str, nachsatz: str='') -> None
```

Die Zeile zu [[opencivil.nachweis.querschnittsloeser#wirksamer_modul|wirksamer_modul]], aus den Werten `E_cm` und
`phi` -- fuer jeden Nachweis, der mit dem aufgeweichten Beton rechnet.

### protokoll_verfahren

```python
def protokoll_verfahren(p, *, eps_druck: float, eps_zug: float, fasern: int=FASERN, verdraengt: bool=True, suche: Optional[str]=None) -> None
```

Der Ablauf der Suche, in die Mitschrift geschrieben.

Steht hier und nicht bei den Nachweisen, die den Loeser benutzen: sonst
stuende dieselbe Beschreibung zweimal da, und beim naechsten Eingriff in
das Verfahren aendert man eine davon.

Beschrieben wird der *Ablauf*, nicht jeder Zwischenwert. Die Halbierungen
abzudrucken hiesse, hundert Zeilen zu zeigen, von denen nur die letzte
etwas behauptet -- und die wird ohnehin durch die Probe belegt. Wie
gesucht wird, sagt der Loeser selbst (`suche`, sein
[[opencivil.nachweis.querschnittsloeser#Faserloeser.suche|Faserloeser.suche]]); ohne Angabe das Halbieren.

### probenschranken

```python
def probenschranken(querschnitt: Faserquerschnitt, grenzen: Dehnungsgrenzen) -> Tuple[float, float]
```

Wie weit `N_int` und `M_int` einer gefundenen Ebene neben dem Ziel
liegen duerfen ([[opencivil.nachweis.querschnittsloeser#Konstanten|PROBE_SCHRANKE]]): gemessen an der Druckkraft des
ganzen Querschnitts bei seiner Grenzstauchung, das Moment dazu mal seiner
Hoehe. Am Querschnitt, nicht an der Einwirkung: wie genau eine Suche
trifft, haengt an ihm -- eine kleine Last auf einem grossen Querschnitt
trifft sie nicht genauer.

### plattenfasern

```python
def plattenfasern(*, h: float, b: float, beton: Callable[[float], float], staebe: Sequence[Tuple[float, float, Callable[[float], float]]], fasern: int=FASERN, gemittelt: bool=False, verdraengt: bool=True) -> Faserquerschnitt
```

Die Platte als Fasern: gleich dicke Scheiben ueber die Hoehe, der Arm ab
der Mittelebene, dazu je Lage `(Flaeche, z, Gesetz)` ein Stab.

Der Loeser und die genaue Resistenzlinie
([[opencivil.nachweis.resistenzlinie#Ebenenlinie|Ebenenlinie]]) rechnen mit
demselben Querschnitt -- darum steht er einmal da. `gemittelt` und
`verdraengt` wie bei [[opencivil.nachweis.querschnittsloeser#Querschnittsloeser|Querschnittsloeser]]. Die Ausdruecke
stehen genau so da wie vor dem Umbau: dieselben Zahlen bis aufs letzte
Bit, und damit derselbe Bericht.

### Faserloeser

```python
class Faserloeser
```

Ein Querschnitt aus Fasern, mit Suche nach der Dehnungsebene.

`querschnitt` sind die Fasern samt Staeben, `grenzen` die
Dehnungsgrenzen, innerhalb derer jedes Gesetz gilt -- mehr braucht die
Suche nicht. Dazu, was Bilder und Linien vom Querschnitt wissen muessen:
die Arme der Raender `oben` und `unten` -- oben ist gedrueckt, wenn
ein positives Moment wirkt --, die Lagen mit ihrem Stahl, eine je Stab
der Fasern, und die Spannung des Betons an einer Stelle
(`beton(arm, eps)`). `eps_druck` und `eps_zug` sind die
aeussersten Dehnungen, fuer die die Gesetze gelten. Wer nur sucht -- ein
Nachweis, der die Ebene zu einem Lastfall braucht --, laesst sie weg.

Eine Lage liegt in der Tiefe `z` unter dem oberen Rand; ihr Arm ist
`z + oben`.

- `SUCHE = 'Gesucht wird in zwei geschachtelten Halbierungen. Innen: zu einer fe…` – Wie gesucht wird, in der Mitschrift ([[opencivil.nachweis.querschnittsloeser#protokoll_verfahren|protokoll_verfahren]]).

#### Faserloeser.suche

```python
@property
def suche(self) -> str
```

Wie dieser Loeser sucht, in Worten -- fuer die Mitschrift.

#### Faserloeser._fenster

```python
def _fenster(self, chi: float) -> Optional[Tuple[float, float]]
```

In welchem Bereich `eps_m` liegen darf, damit keine Faser aus dem
gueltigen Dehnungsbereich faellt. Bei der Platte: beide Raender
zwischen `-eps_druck` und `eps_zug`, siehe
[[opencivil.querschnitt.fasern#Dehnungsgrenzen.fenster|Dehnungsgrenzen.fenster]].

#### Faserloeser._eps_zu_normalkraft

```python
def _eps_zu_normalkraft(self, chi: float, N_ziel: float) -> Optional[float]
```

Die mittlere Dehnung, bei der `N = N_ziel` gilt -- bei festem `chi`.

`N(eps_m)` waechst im gueltigen Bereich monoton: mehr Dehnung heisst
mehr Zug. Eine Bisektion findet die Stelle also sicher, sofern sie im
Fenster liegt.

#### Faserloeser.mitteldehnung

```python
def mitteldehnung(self, chi: float, N: float) -> Optional[float]
```

Die Dehnung auf halber Hoehe, bei der die Ebene mit der Kruemmung
`chi` die Normalkraft `N` traegt -- `None`, wo es keine gibt.
Fuer Linien, die ueber die Kruemmung laufen statt ueber das Moment.

#### Faserloeser.kruemmung

```python
def kruemmung(self, eps_m: float, M: float) -> Optional[float]
```

Die Kruemmung, bei der die Ebene mit der Dehnung `eps_m` auf halber
Hoehe das Moment `M` traegt -- `None`, wo es keine gibt.

Bei fester Dehnung waechst das Moment mit der Kruemmung: die eine
Seite wird mehr gedehnt, die andere mehr gestaucht. Gesucht wird darum
wie in [[opencivil.nachweis.querschnittsloeser#Faserloeser._eps_zu_normalkraft|_eps_zu_normalkraft]] durch Halbieren, innerhalb dessen,
was die Grenzen bei dieser Dehnung zulassen.

#### Faserloeser.loese

```python
def loese(self, *, N_Ed: float, M_Ed: float) -> Ebene
```

Die Dehnungsebene zu diesen Schnittgroessen.

Aeussere Bisektion ueber `chi`: zu jedem `chi` wird `eps_m` so
bestimmt, dass die Normalkraft stimmt, und das uebrig bleibende Moment
gegen `M_Ed` gehalten. `M(chi)` waechst monoton -- mehr Kruemmung
heisst mehr Moment --, solange der Querschnitt nicht versagt.

#### Faserloeser._probenschranken

```python
@cached_property
def _probenschranken(self) -> Tuple[float, float]
```

[[opencivil.nachweis.querschnittsloeser#probenschranken|probenschranken]] dieses Querschnitts -- einmal gerechnet.

#### Faserloeser._mit_probe

```python
def _mit_probe(self, eps_m: float, chi: float, N_Ed: float, M_Ed: float) -> Ebene
```

Die gefundene Ebene, mit ihrer Probe: erzeugt sie `N_Ed` und
`M_Ed` nicht, ist sie verfehlt ([[opencivil.nachweis.querschnittsloeser#Ebene|Ebene.verfehlt]]).

#### Faserloeser._suchen

```python
def _suchen(self, f: Callable[[float], Optional[float]], unten: float, oben: float, schranke: float, f_unten: Optional[float]=None, f_oben: Optional[float]=None) -> Optional[float]
```

Wo `f` zwischen `unten` und `oben` null wird -- `f` steigt,
unten ist es negativ, oben nicht. Halbiert, bis das Fenster schmaler
ist als `schranke`; `None`, wenn `f` unterwegs keinen Wert hat.
`f_unten` und `f_oben` braucht das Halbieren nicht -- sie sind
fuer eine Suche, die mit ihnen schneller ist
([[opencivil.nachweis.querschnittsloeser#FaserloeserIllinois|FaserloeserIllinois]]).

#### Faserloeser._rand

```python
def _rand(self, start: float, N_Ed: float, moment: Callable[[float], Optional[float]], M_Ed: float, *, nach_oben: bool) -> Tuple[Optional[float], None]
```

Eine Kruemmung, bei der das Moment `M_Ed` sicher ueber- bzw.
unterschreitet -- der Startpunkt der aeusseren Bisektion.

Von der theoretischen Grenze aus wird herangetastet: dort ist das
Fenster leer oder die Normalkraft nicht erreichbar. Zwanzig
Halbierungen genuegen, um auf eine loesbare Stelle zu kommen.

Nahe am Widerstand genuegen sie nicht. Zwischen der letzten Stufe
ohne Gleichgewicht und der ersten mit -- an der Platte des Beispiels
0.08 und 0.04 1/m -- liegen Kruemmungen, die das Moment noch
erreichen, und das Halbieren springt ueber sie hinweg: 234.9 kNm
hiessen dort «kein Gleichgewicht», obwohl der Querschnitt bis
235.4 kNm traegt. Trifft das Halbieren nicht, wird darum die Grenze
zwischen den beiden Stufen gesucht -- die groesste Kruemmung mit
Gleichgewicht -- und dort noch einmal gefragt. Wo das Halbieren
trifft, bleibt alles, wie es war.

### FaserloeserIllinois

```python
class FaserloeserIllinois(Faserloeser)
```

Derselbe Loeser, der eine Nullstelle mit dem Illinois-Verfahren sucht
statt durch Halbieren -- in denselben Klammern, bis auf dieselbe Breite.

Fuer den gezeichneten Querschnitt unter Gebrauchslast
([[opencivil.nachweis.qa_gebrauch]]): dort wird je Lastfall die
Nulllinie gedreht, und jede Neigung ist eine ganze Suche. Halbiert
braucht eine Suche rund vierzig Schritte, mit Illinois ein Viertel davon:
zwischen zwei Knicken der Gesetze ist die Kraft eine Gerade, und dort
trifft die Sekante.

Dazu faengt er bei der Kruemmung und der Dehnung an, die er zuletzt
gefunden hat ([[opencivil.nachweis.querschnittsloeser#FaserloeserIllinois.loese|loese]]): beim Knicken folgen sich viele Ebenen mit
wenig verschiedenen Schnittgroessen, und das Eingrenzen von der groessten
Kruemmung her kostete jede von ihnen mehr als die Suche selbst. Darum
sucht auch das Knicken der Platte so ([[opencivil.nachweis.querschnittsloeser#QuerschnittsloeserIllinois|QuerschnittsloeserIllinois]]);
ihre Stahlspannungen und Analysen halbieren weiter.

**Nur wo die Ebene eindeutig ist.** Springt ein Gesetz -- der
Spannungsblock --, hat das Moment ueber der Kruemmung flache Stuecke: dort
traegt jede Kruemmung dasselbe Moment, und welche gefunden wird, haengt am
Weg der Suche. Mit einem Gedaechtnis hinge das Ergebnis dann an der
Reihenfolge der Rechnungen -- an der Stuetze des Pruefprojekts war die
Grenzkraft so 4200 statt 4099.5 kN. Mit springendem Gesetz sucht er darum
wie jeder [[opencivil.nachweis.querschnittsloeser#Faserloeser|Faserloeser]], halbiert und von vorn ([[opencivil.nachweis.querschnittsloeser#FaserloeserIllinois|halbiert]]).
Gesetze ohne Sprung -- Parabel, elastisch -- haben flache Stuecke erst am
vollplastischen Querschnitt; an den Pruefprojekten bleibt dort jede Zahl,
wie sie war.

- `SUCHE = 'Gesucht wird in zwei geschachtelten Suchen. Innen: zu einer festgeha…`

#### FaserloeserIllinois.suche

```python
@property
def suche(self) -> str
```

#### FaserloeserIllinois._eps_zu_normalkraft

```python
def _eps_zu_normalkraft(self, chi: float, N_ziel: float) -> Optional[float]
```

Wie beim [[opencivil.nachweis.querschnittsloeser#Faserloeser|Faserloeser]], aber von der zuletzt gefundenen
Dehnung aus eingegrenzt: die Kruemmungen einer Suche liegen nahe
beieinander, und mit ihnen die Dehnungen.

#### FaserloeserIllinois._eps_von

```python
def _eps_von(self, chi: float, N_ziel: float, eps: float) -> Optional[float]
```

Von `eps` aus mit wachsenden Schritten eingrenzen, im Fenster -- dann Illinois.

#### FaserloeserIllinois.loese

```python
def loese(self, *, N_Ed: float, M_Ed: float) -> Ebene
```

Die Dehnungsebene -- von der zuletzt gefundenen Kruemmung aus
eingegrenzt, wo es eine gibt, sonst wie jeder [[opencivil.nachweis.querschnittsloeser#Faserloeser|Faserloeser]].
Was die naechste Suche nicht eingrenzen kann oder verfehlt, sucht sie
von vorn.

#### FaserloeserIllinois._von_zuletzt

```python
def _von_zuletzt(self, N_Ed: float, M_Ed: float, chi: float) -> Optional[Ebene]
```

Von `chi` aus mit wachsenden Schritten, bis das Moment die Seite
wechselt -- das Moment waechst mit der Kruemmung --, dann Illinois.
`None`, wo unterwegs keine Ebene die Normalkraft traegt; die Ebene
mit ihrer Probe, die auch verfehlt sein kann ([[opencivil.nachweis.querschnittsloeser#Faserloeser._mit_probe|_mit_probe]]).

### Querschnittsloeser

```python
class Querschnittsloeser(Faserloeser)
```

Der Querschnitt einer Platte als Faserintegral -- aus Hoehe, Breite und
Lagen gebaut, gesucht wird wie bei jedem [[opencivil.nachweis.querschnittsloeser#Faserloeser|Faserloeser]].

`beton` ist ein Werkstoffgesetz `eps -> sigma` in SI
([[opencivil.querschnitt.werkstoffgesetz]]), `stahl` macht aus dem
Stahl einer Lage eines -- ohne Angabe das [[opencivil.querschnitt.werkstoffgesetz#Stahlgesetz|Stahlgesetz]] der Lage
selbst, jenseits von `eps_ud` null; die Handrechnung gibt ihren Stahl
nur auf Zug mit. Damit bleibt der Loeser
frei von Annahmen ueber das Werkstoffgesetz: die Spannungsbegrenzung rechnet
elastisch mit Kriechen und charakteristischen Festigkeiten, der
Knicknachweis mit dem nichtlinearen Gesetz der Norm und Bemessungswerten
-- siehe [[opencivil.nachweis.querschnittsloeser#Werkstoffsatz|Werkstoffsatz]].

**Das Suchfenster muss zu den Gesetzen passen.** `eps_druck` und
`eps_zug` duerfen nicht weiter reichen als der Bereich, in dem beide
Gesetze monoton sind -- jenseits ihrer Bruchdehnung geben sie null zurueck,
und dort findet die Bisektion Scheinloesungen. Ohne `eps_zug` reicht das
Fenster darum bis zur kleinsten Bruchdehnung der Lagen; `eps_druck`
passt zur Parabel ([[opencivil.querschnitt.werkstoffgesetz#Betongesetz|Betongesetz]]),
wer es weitet, muss das Gesetz mitweiten.

Ohne `grenzen` gelten beide Werte an beiden Raendern. Wer andere
Grenzen braucht -- die Spannung-Dehnung-Analyse die des Dehnungsfaechers,
mit `eps_ud` am Stahl statt am Betonrand --, gibt sie mit.
`gemittelt` laesst ein Gesetz, das springt (der Spannungsblock), ueber
jede Faser mitteln statt in ihrer Mitte lesen: sonst springt mit ihm die
Normalkraft, und keine Ebene trifft sie genau. Ohne `verdraengt` zaehlt
der Beton auch dort, wo der Stahl liegt -- so rechnet die Handrechnung.

Welche Gesetze zu welcher Wahl gehoeren, sagt
[[opencivil.nachweis.rechenwahl#gesetze|opencivil.nachweis.rechenwahl.gesetze]].

### QuerschnittsloeserIllinois

```python
class QuerschnittsloeserIllinois(FaserloeserIllinois, Querschnittsloeser)
```

Die Fasern der Platte ([[opencivil.nachweis.querschnittsloeser#Querschnittsloeser|Querschnittsloeser]]), gesucht wie am
gezeichneten Querschnitt: mit Illinois, von der zuletzt gefundenen Ebene
aus ([[opencivil.nachweis.querschnittsloeser#FaserloeserIllinois|FaserloeserIllinois]]). Fuer das Knicken der Platte -- dort
kostete das Halbieren beinahe die ganze Rechenzeit (Benutzer,
2026-10-15).

### Werkstoffsatz

```python
class Werkstoffsatz(str, Enum)
```

Mit welchen Festigkeiten die Werkstoffgesetze rechnen.

**Bemessung** -- `f_cd` und `f_yd`. Fuer die Tragsicherheit: gefragt
ist, was der Querschnitt *darf*, und dahinein gehoert der
Teilsicherheitsbeiwert.

**Charakteristisch** -- `f_ck` und `f_yk`. Fuer die
Gebrauchstauglichkeit: gefragt ist, was der Querschnitt *tut*, und Stahl
fliesst bei `f_yk`, nicht bei `f_yd`. Mit dem Plateau bei `f_yd`
laege jede Stahlspannung unter 435 N/mm², und eine Grenze darueber --
`f_yk` bei normaler Rissanforderung -- waere nie zu ueberschreiten: ein
Nachweis, der per Konstruktion immer aufgeht.

Der Satz bestimmt, **wo die Plateaus liegen**, und sonst nichts. Die
Moduln und Dehnungsgrenzen sind in beiden Saetzen dieselben. Er steht hier
als Name und nicht als zwei Zahlen an jeder Aufrufstelle: welche Werte ein
Nachweis ansetzt, ist eine Entscheidung, und eine Entscheidung soll man
lesen koennen, statt sie aus `f_sd=...` erschliessen zu muessen. Jeder
Nutzer des Loesers nennt darum seinen Satz -- der Knicknachweis
`BEMESSUNG`, die Spannungsbegrenzung `CHARAKTERISTISCH`; die
Spannung-Dehnung-Analyse waehlt ihn je Analyse.

- `BEMESSUNG = 'bemessung'`
- `CHARAKTERISTISCH = 'charakteristisch'`

#### Werkstoffsatz.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Werkstoffsatz.kurz

```python
@property
def kurz(self) -> str
```

Fuer schmale Zeilen.

#### Werkstoffsatz.kuerzel

```python
@property
def kuerzel(self) -> str
```

Der Buchstabe am Index: `d` (design) oder `k` (charakteristisch).

#### Werkstoffsatz.widerstandsindex

```python
@property
def widerstandsindex(self) -> str
```

Der Index an einem Widerstand: `M_{Rd}` oder `M_{Rk}`.

#### Werkstoffsatz.stahl_druck

```python
@property
def stahl_druck(self) -> str
```

Kurzname der Stahlfestigkeit auf Druck -- dort beginnt das Plateau.

#### Werkstoffsatz.stahl

```python
@property
def stahl(self) -> str
```

Kurzname der Stahlfestigkeit -- dort beginnt das Fliessplateau.

#### Werkstoffsatz.beton

```python
@property
def beton(self) -> str
```

Kurzname der Betonfestigkeit -- dort endet der Anstieg im Druck.

#### Werkstoffsatz.stahl_zeichen

```python
@property
def stahl_zeichen(self) -> str
```

Das Formelzeichen dazu, fuer die Herleitung -- `f_{yd}`.

#### Werkstoffsatz.stahl_druck_zeichen

```python
@property
def stahl_druck_zeichen(self) -> str
```

Das Zeichen des Plateaus auf Druck -- `f_{yd}^{-}`.

#### Werkstoffsatz.beton_zeichen

```python
@property
def beton_zeichen(self) -> str
```

Das Formelzeichen dazu, fuer die Herleitung -- `f_{cd}`.


## Konstanten

- `FASERN = 60` – Fasern ueber die Plattenhoehe. 60 reichen: die Betonspannung ist stetig, und der Fehler der Mittelpunktsregel faellt mit dem Quadrat der Faserdicke.
- `SCHRITTE = 60` – Obergrenze der Halbierungen je Bisektion. Erreicht wird sie fast nie -- abgebrochen wird ueber die Schranken darunter, sobald das Fenster eng genug ist. Die Zahl steht nur da, damit keine Schleife ewig laeuft.
- `EPS_SCHRANKE = 1e-11` – Wann das Dehnungsfenster eng genug ist. Der Startbereich ist rund 0.05 breit; 1e-11 ist ein Zehntausendstel eines Promille und liegt weit unter allem, was eine Eingabe hergibt. Ohne diese Schranke lief die Bisektion stur sechzig Mal -- die letzten zehn Durchlaeufe aendern in doppelter Genauigkeit nichts mehr und kosten doch jedesmal einen Faserdurchgang.
- `CHI_SCHRANKE = 1e-10` – Dasselbe fuer die Kruemmung, in 1/m.
- `PROBE_SCHRANKE = 1e-06` – Wie genau die gefundene Ebene ihre Schnittgroessen treffen muss -- als Teil der Druckkraft des ganzen Querschnitts bei seiner Grenzstauchung, beim Moment mal seiner Hoehe ([[opencivil.nachweis.querschnittsloeser#probenschranken|probenschranken]]). Die Suchen treffen weit genauer: in den beiden Pruefprojekten bleiben 1684 Ebenen unter 0.4 % der Schranke (2026-10-15). Eine Ebene, die an einem Sprung des Spannungsblocks haengen bleibt, liegt um Hunderte Kilonewton daneben.
- `EPS_DRUCK = 0.003` – Aeusserste Dehnungen, innerhalb derer gesucht wird -- Stauchung und Dehnung. **Der Suchbereich muss im gueltigen Bereich beider Gesetze bleiben:** jenseits der Bruchdehnung geben sie null zurueck, und damit waere `N(eps_m)` nicht mehr monoton. Genau daran scheiterte die erste Fassung -- die Bisektion sah bei -0.5 dieselbe Normalkraft wie bei 0.
- `EPS_ZUG = 0.045`
- `VERFEHLTE_EBENE = 'Erzeugt die gefundene Ebene die Einwirkung nicht, gibt es zu ihr kei…` – Was die Mitschrift ueber eine verfehlte Ebene sagt ([[opencivil.nachweis.querschnittsloeser#Ebene|Ebene.verfehlt]]) -- bei der Platte wie am gezeichneten Querschnitt.

## Braucht

- [[opencivil.core.protokoll]]
- [[opencivil.querschnitt.fasern]]
- [[opencivil.querschnitt.werkstoffgesetz]]

## Gebraucht von

- [[opencivil.nachweis.biegung_normalkraft]]
- [[opencivil.nachweis.gebrauchsebene]]
- [[opencivil.nachweis.handrechnung]]
- [[opencivil.nachweis.knicken]]
- [[opencivil.nachweis.qa_gebrauch]]
- [[opencivil.nachweis.qa_knicken]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.nachweis.resistenzlinie]]
- [[opencivil.nachweis.spannungsbegrenzung]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.querschnitt.schnittanalyse]]
- [[opencivil.spannungsanalyse]]
- [[opencivil.web.api]]

## Formeln aus diesem Modul

- [[Dehnungsebene und innere Kräfte]] · `protokoll_verfahren`
- [[Wirksamer Elastizitätsmodul]] · `protokoll_wirksamer_modul`
