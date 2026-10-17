---
erzeugt: 4c96b69f369b
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/knicken.py
> Nachweis am verformten System.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/knicken.py)

## VERANTWORTUNG

Prueft je Knickfall, ob sich unter der Druckkraft ueberhaupt eine
Gleichgewichtslage einstellt -- und wenn ja, ob der Querschnitt das dabei
entstehende Moment aufnimmt.


## DAS VERFAHREN


```
alpha_i = min[ max(0.01/sqrt(l); 1/300) ; 1/200 ]      Schiefstellung
e_0d    = max( d/30 ; alpha_i * l_cr/2 )               ungewollte Ausmitte
e_1d    = |M_Ed,1 / N_Ed|                              gewollte Ausmitte
e_2d    = |chi| * l_cr^2 / pi^2                        Ausmitte 2. Ordnung

wiederhole:
    M_ziel = |N| * (e_0d + e_1d + e_2d)
    (eps_m, chi) = Gleichgewicht zu (N, M_ziel)
    e_2d neu aus chi
bis M_ziel sich nicht mehr aendert
```

Die Kruemmung haengt am Moment, das Moment an der Ausmitte und die Ausmitte
wieder an der Kruemmung. Es gibt dafuer keine geschlossene Loesung; gesucht
wird der Fixpunkt. Laeuft die Folge ein, gibt es eine Gleichgewichtslage.
Waechst sie, kippt das System -- und zwar nicht wegen einer ueberschrittenen
Spannung, sondern weil es gar kein Gleichgewicht gibt. Genau das ist Knicken.


## DER ERFUELLUNGSGRAD IST EIN VERHAELTNIS VON NORMALKRAEFTEN


```
N_Rd = groesste Druckkraft, die der Stab noch traegt
alpha_eff = N_Rd / |N_Ed|
```

Gesucht wird `N_Rd` durch Halbieren: zu jeder Probekraft laeuft das
Verfahren oben, und getragen ist sie, wenn die Folge einlaeuft *und* der
Querschnitt das dabei entstehende Moment aufnimmt. Die gewollte Ausmitte
`e_1d` bleibt dabei fest -- sie ist eine Eigenschaft des Systems, nicht der
Last; `M_Ed,1` waechst also mit. `e_0d` ist rein geometrisch und aendert
sich ohnehin nicht.

Ueber `M_Rd` zu vergleichen waere das naechstliegende gewesen und ist
trotzdem falsch: beim Knicken gibt es Faelle, in denen gar kein Moment mehr
herauskommt, weil die Folge davonlaeuft. Dann steht da kein Widerstand,
sondern nichts -- und ein Nachweis ohne Zahl sagt nicht, wie weit er daneben
liegt. Die Normalkraft dagegen hat immer einen Grenzwert.


## ZWEI WAHLEN

Womit gerechnet wird, waehlt das Kapitel zweimal ([[opencivil.querschnitt.gesetzwahl#Rechenwahl|Rechenwahl]]):

* **Verformung (e_2d)** -- die Gesetze des Loesers, der zu jedem Moment die
  Kruemmung sucht. Immer praezise ohne Vereinfachung, gewaehlt werden
  Kriechzahl und Werte (Vorgabe Bemessungswerte); die Kriechzahl weicht den
  Beton auf, und ein weicher Beton verformt sich mehr. Den Spannungsblock
  gibt es hier nicht mehr ([[opencivil.nachweis.rechenwahl#Konstanten|VERFORMUNGSARTEN]],
  Benutzer, 2026-10-15): mit ihm hat das Moment ueber der Kruemmung flache
  Stuecke, und die Ausmitte ist nahe der Grenzkraft nicht eindeutig.
* **Widerstand (N_Rd)** -- die Resistenzlinie, die sagt, ob der Querschnitt
  das Moment am verformten System aufnimmt. Vorgabe die
  0.85·x-Vereinfachung mit Bemessungswerten. Waehlt das Kapitel dasselbe wie
  die Tragsicherheit, ist es deren Linie; sonst baut es eine eigene, mit
  eigener Herleitung.

Die Handrechnung steht bei keiner der beiden zur Wahl
([[opencivil.nachweis.rechenwahl#Konstanten|FASERARTEN]]): beim Knicken zaehlt
die Normalkraft genau, Ebene fuer Ebene, und ein Polygon aus Eckpunkten
waere hier nur eine schlechtere Vereinfachung. Bis 2026-10-12 war sie die
Vorgabe des Widerstands.


## NUR IN X-RICHTUNG

Ein Knicknachweis braucht eine Knicklaenge, und die gehoert zu einer
Tragrichtung. Gerechnet wird darum nur mit der Bewehrung in x -- in y waere
die Breite der Platte die Laenge, und die ist keine Stuetze.


## DER LOESER

Die Iteration und die Suche nach N_Rd folgen sich in hunderten Ebenen mit
wenig verschiedenen Schnittgroessen. Gesucht werden sie darum mit Illinois,
von der zuletzt gefundenen Ebene aus
([[opencivil.nachweis.querschnittsloeser#QuerschnittsloeserIllinois|QuerschnittsloeserIllinois]]):
an den Pruefprojekten ein Drittel der Faserdurchlaeufe, dieselben
Grenzkraefte auf 0.01 kN. Wo ein Gesetz springt, halbiert der Loeser wie
vorher -- dort ist die Ebene nicht eindeutig; die Verformung rechnet seit
2026-10-15 ohnehin nur noch praezise.


## DAS VERFAHREN GEHOERT KEINEM QUERSCHNITT

Die Iteration und die Suche nach `N_Rd` brauchen vom Stab nur dreierlei:
die Ebene zu N und M, den Momentenwiderstand bei N und die statische Hoehe
([[opencivil.nachweis.knicken#Knickstab|Knickstab]]). Sie stehen darum in [[opencivil.nachweis.knicken#Knickverfahren|Knickverfahren]]; die
Platte ([[opencivil.nachweis.knicken#Knicken|Knicken]]) und der gezeichnete Querschnitt
([[opencivil.nachweis.qa_knicken#KnickenQA|KnickenQA]]) sagen, woher die drei
kommen.


## WAS IN DIE MITSCHRIFT GEHOERT

Die Iteration Durchlauf fuer Durchlauf -- sie *ist* hier das Verfahren und
nicht bloss eine Nullstellensuche, die man auch anders haette machen koennen.
Dazu die Probe, dass die gefundene Dehnungsebene genau diese Schnittgroessen
erzeugt, und die Suche nach `N_Rd` als Verfahren beschrieben: von der
laeuft nur das Ergebnis mit, sonst stuenden vierzig Iterationstabellen da.

## Inhalt

### Knickfall

```python
@dataclass(frozen=True)
class Knickfall
```

Eine zu pruefende Kombination aus Druckkraft und Moment 1. Ordnung.

- `name: str`
- `N_Ed: Groesse` – Druck negativ -- wie ueberall in diesem Werkzeug.
- `M_Ed_1: Groesse`
- `laenge: Groesse`
- `knicklaenge: Groesse`

#### Knickfall.kennung

```python
@property
def kennung(self) -> str
```

### Durchlauf

```python
@dataclass(frozen=True)
class Durchlauf
```

Ein Schritt der Ausmitten-Iteration -- eine Zeile der Mitschrift.

- `nummer: int`
- `e_2d_vorher: float` – Ausmitte, mit der dieser Durchlauf begonnen hat -- im ersten null.
- `M_ziel: float` – Moment am verformten System, aus `e_2d_vorher`.
- `chi: float` – Kruemmung im Gleichgewicht dazu. `nan`, wenn es keine gibt.
- `e_2d: float` – Ausmitte, die aus `chi` folgt -- der Start des naechsten Durchlaufs.

### Gleichgewicht

```python
@dataclass
class Gleichgewicht
```

Was bei einer Probekraft herauskommt.

- `traegt: bool = False`
- `stabil: bool = False` – Ob die Ausmitten-Iteration eingelaufen ist.
- `e_2d: float = 0.0`
- `M_ges: float = 0.0`
- `M_Rd: float = 0.0`
- `eps_m: float = 0.0`
- `chi: float = 0.0`
- `N_int: float = 0.0`
- `M_int: float = 0.0`
- `schritte: List[Durchlauf] = field(default_factory=list)`

### Knickergebnis

```python
@dataclass
class Knickergebnis
```

Alle Zwischenwerte eines Knickfalls.

- `fall: Knickfall`
- `alpha_i: float = 0.0`
- `d: float = 0.0` – Statische Hoehe der untersten x-Lage, in m -- fuer die Mindestausmitte.
- `e_0d: float = 0.0`
- `e_1d: float = 0.0`
- `e_2d: float = 0.0`
- `M_ges: float = 0.0` – Moment am verformten System, in Nm.
- `eps_m: float = 0.0`
- `chi: float = 0.0`
- `N_int: float = 0.0`
- `M_int: float = 0.0`
- `durchlaeufe: int = 0`
- `stabil: bool = False`
- `M_Rd: float = 0.0` – Momentenwiderstand bei dieser Normalkraft, in Nm.
- `N_Rd: float = 0.0` – Groesste Druckkraft mit Gleichgewicht, als Betrag in N.
- `M_bei_N_Rd: float = 0.0` – Das Moment am verformten System bei `N_Rd`, in Nm. Dort liegt der Stab an seiner Grenze, also ist es zugleich sein Momentenwiderstand bei dieser Normalkraft -- der Punkt sitzt damit auf der Interaktionslinie. Im M-N-Diagramm ist das der Widerstandspunkt des Knicknachweises.
- `schritte: List[Durchlauf] = field(default_factory=list)` – Die Ausmitten-Iteration bei N_Ed -- Zeile fuer Zeile.
- `halbierungen: int = 0`
- `erfuellungsgrad: float = 0.0`
- `erfuellt: bool = False`
- `begruendung: str = ''`
- `hinweis: str = ''`

### Knickbefund

```python
@dataclass
class Knickbefund
```

Was der Knicknachweis festhaelt: die Linie seines Widerstands, je Fall
die Zwischenwerte und den Loeser -- wer nachrechnen will, was bei einer
anderen Druckkraft herauskaeme, braucht denselben. Steht nach dem Lauf in
der Loesung, nicht am Nachweis.

- `linie: Widerstandslinie` – Die Linie des Widerstands: die eigene, oder mit derselben Wahl die der Tragsicherheit -- dasselbe Objekt, einmal gerechnet.
- `loeser: Querschnittsloeser`
- `ergebnisse: List[Knickergebnis] = field(default_factory=list)`

### schiefstellung

```python
def schiefstellung(laenge: float) -> float
```

`alpha_i = min[ max(0.01/sqrt(l); 1/300) ; 1/200 ]`, `l` in m.

### Knickstab

```python
@dataclass(frozen=True)
class Knickstab
```

Was das Verfahren vom Stab wissen muss -- siehe Dateikopf.

- `loeser: Faserloeser` – Die Ebene zu einer Normalkraft und einem Moment, fuer die Verformung.
- `moment_bei: Callable[[float, bool], Optional[float]]` – Der Momentenwiderstand bei der Druckkraft `N` (Betrag) -- auf der Seite des positiven Moments oder der anderen. `None`, wo es keinen gibt.
- `d: float` – Die statische Hoehe in m, fuer die Mindestausmitte.

### Knickverfahren

```python
class Knickverfahren(Nachweis)
```

Nachweis am verformten System, je Knickfall -- das Verfahren, ohne zu
sagen, woher der Stab kommt ([[opencivil.nachweis.knicken#Knickstab|Knickstab]]).

Der Nachweis ist erfüllt, wenn die Ausmitten-Iteration einläuft **und**
der Querschnitt das Moment zweiter Ordnung aufnimmt.

- `THEMA = 'Knicken'`
- `widerstand: Rechenwahl`
- `schnell: bool = False`

#### Knickverfahren._m_rd_symbol

```python
def _m_rd_symbol(self, erg: 'Knickergebnis') -> str
```

Das Zeichen des Momentenwiderstands bei N_Ed in der Herleitung.

#### Knickverfahren._gleichgewicht

```python
def _gleichgewicht(self, stab: Knickstab, N: float, erg: Knickergebnis, l_cr: float) -> Gleichgewicht
```

Die Ausmitten-Iteration bei der Druckkraft `N` (Betrag).

Getragen ist `N`, wenn die Folge einlaeuft **und** der Querschnitt
das Moment am verformten System aufnimmt. Beides gehoert zusammen: ein
Stab, der kippt, ist so wenig nachgewiesen wie einer, dessen
Querschnitt aufreisst.

#### Knickverfahren._grenzkraft

```python
def _grenzkraft(self, stab: Knickstab, N_Ed: float, erg: Knickergebnis, l_cr: float, *, traegt: bool) -> float
```

Die groesste getragene Druckkraft, durch Halbieren.

Bei `N = 0` traegt der Stab immer: mit der Last verschwindet auch
das Moment, denn `e_1d` ist fest. Das ist die untere Schranke, die
das Halbieren braucht -- sie muss nicht gesucht werden.

#### Knickverfahren._n_rd

```python
def _n_rd(self, erg: Knickergebnis) -> Wert
```

Die Grenzkraft -- der Widerstand in Tabelle und Herleitung.

#### Knickverfahren._protokoll_verfahren

```python
def _protokoll_verfahren(self, p: Protokoll) -> None
```

Was jeder Knicknachweis vorweg schreibt: das Verfahren und seine Ausmitten.

#### Knickverfahren._protokoll_iteration

```python
def _protokoll_iteration(self, p: Protokoll, erg: Knickergebnis) -> None
```

Die Ausmitten-Iteration, Durchlauf fuer Durchlauf.

Anders als bei den Nullstellensuchen im Faserloeser steht sie hier
vollstaendig da: sie ist nicht ein Weg zum Ergebnis, sondern das
Verfahren selbst. Dass die Folge einlaeuft, *ist* die Aussage des
Nachweises -- und das sieht man nur, wenn man die Folge sieht.

#### Knickverfahren._protokoll_grenzkraft

```python
def _protokoll_grenzkraft(self, p: Protokoll, erg: Knickergebnis) -> None
```

Der Erfuellungsgrad -- und wie N_Rd gefunden wurde.

Von der Halbierung steht nur das Verfahren da. Jede Probekraft zieht
eine eigene Ausmitten-Iteration nach sich; die alle abzudrucken hiesse,
dreissig Tabellen fuer eine einzige Zahl zu zeigen.

### Knicken

```python
class Knicken(Knickverfahren)
```

Nachweis am verformten System, je Knickfall -- an der Platte, nur in
x-Richtung: die Iteration rechnet mit ihrem Querschnittsloeser, der
Widerstand kommt aus ihrer Resistenzlinie.

#### Knicken.stab

```python
@staticmethod
def stab(loeser: Querschnittsloeser, linie: Widerstandslinie) -> Knickstab
```

Die Platte als Stab: ihr Loeser, ihre Resistenzlinie und die statische
Hoehe der untersten x-Lage. Aus dem Befund wieder zu bauen, wer
nachrechnen will (`befund.loeser`, `befund.linie`).

#### Knicken.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll)
```


## Konstanten

- `VERFORMUNG = Rechenwahl(art=Rechenart.PARABEL)` – Die Vorgaben der beiden Wahlen -- siehe Dateikopf.
- `WIDERSTAND = Rechenwahl(art=Rechenart.BLOCK)`
- `DURCHLAEUFE = 40` – Groesste Zahl an Durchlaeufen der Ausmitten-Iteration.
- `SCHRANKE = 0.0001` – Wann die Iteration als eingelaufen gilt -- Aenderung des Moments.
- `HALBIERUNGEN = 14` – Durchlaeufe der Halbierung, die N_Rd sucht. Das Fenster ist so breit wie die getragene Kraft selbst; 14 Schritte bringen es auf deren Sechzehntausendstel, bei 2000 kN also auf ein Zehntel Kilonewton. Jeder weitere Schritt kostet eine vollstaendige Ausmitten-Iteration und aendert nichts mehr an der Zahl, die in der Tabelle steht.
- `OBERGRENZE = 64.0` – Wie weit die Suche nach oben gehen darf, als Vielfaches von \|N_Ed\|. Wer einen Stab mit alpha_eff > 64 baut, hat kein Knickproblem.
- `ALPHA_UNTEN = 1.0 / 300.0` – Riegel der Schiefstellung, SIA 262:2025, 4.3.7.
- `ALPHA_OBEN = 1.0 / 200.0`
- `VERFORMUNG_NACH_WAHL = 'Die Verformung rechnet präzise, mit der Parabel; Kriechzahl und Wert…` – Warum die Wahl der Verformung zaehlt -- fuer jeden Knicknachweis derselbe Satz.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.nachweis.biegung_normalkraft]]
- [[opencivil.nachweis.dehnungsfaecher]]
- [[opencivil.nachweis.querschnittsloeser]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.nachweis.resistenzlinie]]
- [[opencivil.querschnitt.gesetzwahl]]
- [[opencivil.querschnitt.platte]]

## Gebraucht von

- [[opencivil.nachweis.qa_knicken]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.aufbau.platte]]

## Formeln aus diesem Modul

- [[Gewollte Ausmitte]] · `Knickverfahren._protokoll_fall`
- [[Gewollte Ausmitte und Ausmitte 2. Ordnung – allgemein]] · `Knickverfahren._protokoll_verfahren`
- [[Iteration der Ausmitte 2. Ordnung]] · `Knickverfahren._protokoll_iteration`
- [[Schiefstellung]] · `Knickverfahren._protokoll_fall`
- [[Ungewollte Ausmitte]] · `Knickverfahren._protokoll_fall`
- [[Ungewollte Ausmitte – allgemein]] · `Knickverfahren._protokoll_verfahren`
