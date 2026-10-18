---
erzeugt: 5b4b0dfabba2
art: modul
tags: [modul]
---
> [!abstract] opencivil/spannungsanalyse/linie.py
> die Linien eines Querschnitts.
> Paket [[opencivil.spannungsanalyse]] · [Quelltext](../../opencivil/spannungsanalyse/linie.py)

## VERANTWORTUNG

Die Momenten-Kruemmungs- und die Normalkraft-Dehnungs-Linie eines Paars von
Loesern, gerissen und ungerissen -- und was ein solches Paar dafuer bieten
muss ([[opencivil.spannungsanalyse.linie#Paar|Paar]]). Die Platte bietet es je Tragrichtung
([[opencivil.spannungsanalyse.platte#Loeserpaar|Loeserpaar]]), der gezeichnete
Querschnitt je Zugseite
([[opencivil.spannungsanalyse.schnitt#Schnittpaar|Schnittpaar]]); bis 2026-10-17
hiess es an den Funktionen dafuer `paar: Any`.


## DIE EBENEN

Jede Linie fragt einen Zustand des Paars nach Ebenen: zu N und M, zu einer
Kruemmung bei N, zu einer Dehnung bei M ([[opencivil.spannungsanalyse.linie#Ebenensuche|Ebenensuche]]). Die Antwort
ist eine [[opencivil.spannungsanalyse.linie#Dehnungsebene|Dehnungsebene]] in der Richtung ihres Loesers. Bei der
Platte und beim gezeichneten Querschnitt «einachsig» bleibt die Nulllinie
parallel zur Achse der Biegung ([[opencivil.spannungsanalyse.linie#FesteNulllinie|FesteNulllinie]]); sonst kippt sie,
bis kein Moment um die andere Achse bleibt
([[opencivil.spannungsanalyse.schnitt#KippendeNulllinie|KippendeNulllinie]]). Die Linie
selbst weiss davon nichts: sie liest Kraft und Verformung der Ebene.

## Inhalt

### Dehnungsebene

```python
@dataclass(frozen=True)
class Dehnungsebene
```

Eine Dehnungsebene eines Paars -- in der Richtung ihres Loesers, also
senkrecht zu ihrer Nulllinie. Kippt die Nulllinie um [[opencivil.spannungsanalyse.linie#Dehnungsebene|neigung]],
zaehlen Moment und Kruemmung, wie sie zur Achse der Biegung stehen: das
Moment um diese Achse und die Kruemmung senkrecht zu ihr.

- `loeser: Faserloeser` – Der Querschnitt in der Richtung der Ebene.
- `eps_m: float`
- `chi: float` – Dehnung am Arm null und Kruemmung senkrecht zur Nulllinie.
- `neigung: float = 0.0` – Wie weit die Nulllinie gegen die Achse der Biegung gedreht ist, rad -- gegen den Uhrzeiger.
- `grenznamen: Tuple[str, ...] = ()` – Je Grenze des Loesers, was sie ist -- fuer «massgebend».
- `verfehlt: bool = False` – Ob die Suche an einem Sprung des Spannungsblocks haengen blieb ([[opencivil.nachweis.querschnittsloeser#Ebene|verfehlt]]). Eine Linie nimmt eine solche Ebene: sie fragt nach der Verformung, bei der ihre Kraft einen Wert durchlaeuft, und am Sprung ist das seine Stelle, auch wenn dort keine Ebene die Kraft genau erzeugt. Ein Bild dagegen braucht die Ebene selbst.

#### Dehnungsebene.kraefte

```python
@cached_property
def kraefte(self) -> 'Schnittkraefte'
```

`N`, `M` und `M_quer` in der Richtung des Loesers.

#### Dehnungsebene.N

```python
@property
def N(self) -> float
```

#### Dehnungsebene.M

```python
@property
def M(self) -> float
```

Das Moment um die Achse der Biegung -- bei gekippter Nulllinie aus beiden Anteilen.

#### Dehnungsebene.M_quer

```python
@property
def M_quer(self) -> float
```

Das Moment um die andere Achse -- unter reiner Biegung null.

#### Dehnungsebene.kruemmung

```python
@property
def kruemmung(self) -> float
```

Die Kruemmung senkrecht zur Achse der Biegung -- ueber sie laeuft die M-χ-Linie.

#### Dehnungsebene.eps_oben

```python
@property
def eps_oben(self) -> float
```

Die Dehnung am oberen Rand des Betons, dem gedrueckten bei positivem Moment.

#### Dehnungsebene.eps_unten

```python
@property
def eps_unten(self) -> float
```

#### Dehnungsebene.fliesst

```python
@property
def fliesst(self) -> bool
```

Ob eine Lage die Fliessdehnung erreicht -- jede die ihres eigenen Stahls.

#### Dehnungsebene.massgebend

```python
@property
def massgebend(self) -> str
```

Welche Grenzdehnung die Ebene erreicht -- die mit dem kleinsten Abstand.

### Ebenensuche

```python
class Ebenensuche(Protocol)
```

Wie ein Zustand eines Paars -- gerissen oder ungerissen -- zu seinen
Ebenen kommt. Jede Frage hat ihre Ebene oder `None`, wo es kein
Gleichgewicht gibt; `M` ist das Moment um die Achse der Biegung,
`chi` die Kruemmung senkrecht zu ihr.

#### Ebenensuche.zu_kraeften

```python
def zu_kraeften(self, N: float, M: float) -> Optional[Dehnungsebene]
```

Die Ebene, die `N` und `M` traegt -- auch eine verfehlte (siehe dort).

#### Ebenensuche.zur_kruemmung

```python
def zur_kruemmung(self, chi: float, N: float) -> Optional[Dehnungsebene]
```

Die Ebene mit der Kruemmung `chi`, die `N` traegt.

#### Ebenensuche.zur_dehnung

```python
def zur_dehnung(self, eps_m: float, M: float) -> Optional[Dehnungsebene]
```

Die Ebene mit der Dehnung `eps_m` am Arm null, die `M` traegt.

### FesteNulllinie

```python
@dataclass(frozen=True)
class FesteNulllinie
```

Die Ebenen in einer festen Richtung: die Nulllinie bleibt parallel zur
Achse der Biegung, und jede Frage ist eine Suche des Loesers. So rechnet
die Platte, so rechnet der gezeichnete Querschnitt «einachsig».

- `loeser: Faserloeser`
- `grenznamen: Tuple[str, ...] = ()`

#### FesteNulllinie.zu_kraeften

```python
def zu_kraeften(self, N: float, M: float) -> Optional[Dehnungsebene]
```

#### FesteNulllinie.zur_kruemmung

```python
def zur_kruemmung(self, chi: float, N: float) -> Optional[Dehnungsebene]
```

#### FesteNulllinie.zur_dehnung

```python
def zur_dehnung(self, eps_m: float, M: float) -> Optional[Dehnungsebene]
```

### Zustaende

```python
class Zustaende(NamedTuple)
```

Die beiden Zustaende eines Paars, je mit seiner Ebenensuche.

- `gerissen: Ebenensuche`
- `ungerissen: Ebenensuche`

### Paar

```python
class Paar(Protocol)
```

Die beiden Loeser eines Querschnitts, gerissen und ungerissen, und was die
Fragen und ihre Herleitung sonst von ihm wissen muessen. Was nur die Art
des Bauteils weiss -- die Tiefe, den Riss, die Dehnung am Ende, den reinen
Betonquerschnitt --, schreibt das Paar selbst in die Herleitung.

- `gerissen: Faserloeser`
- `ungerissen: Faserloeser` – Die beiden Loeser in der Richtung des Paars -- fuer das Bild aus Randdehnungen.
- `wahl: Rechenwahl` – Womit gerechnet wird -- Kriechzahl, Wertesatz, Rechenart.
- `ids: Mapping[str, str]` – Kurzname -> Wert-ID der Eingaben, fuer die Herleitung.
- `staehle: Tuple[Any, ...]` – Die Staehle der Bewehrung, jeder einmal -- fuer die Fliessdehnung.
- `E_cm: float` – Der Modul des Betons -- daran misst sich der aequivalente Modul.
- `bezugsort: str` – Wo die Mitteldehnung gilt -- dort greift N an.

#### Paar.ebenen

```python
def ebenen(self) -> Zustaende
```

Wie die beiden Zustaende ihre Ebenen finden -- fuer jede Linie und
jedes Bild neu: eine Suche, die bei der zuletzt gefundenen Neigung
anfaengt, hinge sonst an dem, was vorher gerechnet wurde.

#### Paar.I_c

```python
@property
def I_c(self) -> float
```

#### Paar.A_c

```python
@property
def A_c(self) -> float
```

#### Paar.rissmoment_bei

```python
def rissmoment_bei(self, N: float) -> float
```

#### Paar.rissnormalkraft_bei

```python
def rissnormalkraft_bei(self, M: float) -> float
```

#### Paar.tiefe

```python
def tiefe(self, w: 'Zwischenwerte', ein: Callable[[str], 'Wert']) -> 'Wert'
```

#### Paar.herleitung_riss

```python
def herleitung_riss(self, p: 'Protokoll', w: 'Zwischenwerte', linie: 'Linie', ein: Callable[[str], 'Wert'], h: 'Wert') -> None
```

#### Paar.herleitung_dehnung_am_ende

```python
def herleitung_dehnung_am_ende(self, p: 'Protokoll', w: 'Zwischenwerte', bruch: 'Grenzzustand', oben: 'Wert', unten: 'Wert', h: 'Wert') -> None
```

#### Paar.herleitung_bezug

```python
def herleitung_bezug(self, p: 'Protokoll', w: 'Zwischenwerte', momente: bool, ein: Callable[[str], 'Wert'], h: 'Wert') -> 'Wert'
```

### Linienpunkt

```python
@dataclass(frozen=True)
class Linienpunkt
```

Ein Punkt einer Linie: die Kraft -- `M` bzw. `N` --, die Verformung,
die dort gilt -- `chi` bzw. `eps_m` --, und beide Zustaende zum
Vergleich.

- `kraft: float`
- `verformung: float` – Was gilt: ungerissen bis zum Riss, darueber gerissen.
- `gerissen: bool`
- `verformung_I: Optional[float]` – Ungerissen -- `None` ueber dem Riss, wo der Beton dafuer Zug ohne Grenze braeuchte, und wo der Zustand keine Loesung hat.
- `verformung_II: Optional[float]` – Gerissen, ohne Zugfestigkeit des Betons.

### Eckpunkt

```python
@dataclass(frozen=True)
class Eckpunkt
```

Ein benannter Punkt einer Linie.

- `kraft: float`
- `verformung: float`

### Grenzzustand

```python
@dataclass(frozen=True)
class Grenzzustand(Eckpunkt)
```

Das Ende einer Linie -- und welche Grenzdehnung es bestimmt.

- `eps_oben: float = 0.0`
- `eps_unten: float = 0.0`
- `massgebend: str = ''`
- `ebene: Optional[Dehnungsebene] = field(default=None, compare=False, repr=False)` – Die Ebene am Ende -- mit ihrer Richtung, fuer die Herleitung.

### Linie

```python
@dataclass
class Linie
```

`M(chi)` bei festgehaltener Normalkraft oder `N(eps_m)` bei
festgehaltenem Moment -- welche, sagt [[opencivil.spannungsanalyse.linie#Linie|art]].

- `art: Analyseart`
- `fest: float` – Was festgehalten wird: `N` in N oder `M` in Nm.
- `riss: float` – Die Kraft, bei der der Querschnitt reisst: `M_Riss(N)` oder `N_Riss(M)`.
- `punkte: List[Linienpunkt] = field(default_factory=list)`
- `bruch: Optional[Grenzzustand] = None`
- `fliessen: Optional[Eckpunkt] = None` – Wo der Stahl der am staerksten gezogenen Lage zu fliessen beginnt.
- `hinweis: str = ''`

#### Linie.hinweisen

```python
def hinweisen(self, satz: str) -> None
```

Einen Satz vor die bisherigen Hinweise stellen.

#### Linie.tragfaehig

```python
@property
def tragfaehig(self) -> bool
```

#### Linie.sprung

```python
@property
def sprung(self) -> Optional[Tuple[Linienpunkt, Linienpunkt]]
```

Die beiden Punkte des Risses: vor und nach dem Reissen, bei derselben Kraft.

### _Weg

```python
@dataclass(frozen=True)
class _Weg
```

Wie eine Linie laeuft -- der einzige Unterschied zwischen M-chi und N-eps.

`ebene` fuehrt von einer Verformung zur gerissenen Ebene oder zu
`None`, wo es kein Gleichgewicht gibt; `kraft` liest aus der Ebene die
Kraft der Linie; `verformung_I` und `verformung_II` suchen zu einer
Kraft die Verformung, ungerissen und gerissen.

- `ebene: Callable[[float], Optional[Dehnungsebene]]`
- `kraft: Callable[[Dehnungsebene], float]`
- `verformung_I: Callable[[float], Optional[float]]`
- `verformung_II: Callable[[float], Optional[float]]`
- `obergrenze: float` – Eine Verformung, ueber der es sicher kein Gleichgewicht mehr gibt.

### _grenze

```python
def _grenze(gut: Callable[[float], bool], unten: float, oben: float) -> float
```

Wo `gut` endet, zwischen `unten` (gut) und `oben` -- durch Halbieren.

### _linie

```python
def _linie(paar: Paar, weg: _Weg, art: Analyseart, fest: float, riss: float) -> Linie
```

Die Linie von null bis zum Bruch: ungerissen bis `riss`, dort der
Sprung, darueber gerissen -- ueber die Verformung gerechnet, mit dem
Fliessbeginn als Punkt der Linie.

### moment_kruemmung

```python
def moment_kruemmung(paar: Paar, *, N: float) -> Linie
```

Die Momenten-Kruemmungs-Linie bei der Normalkraft `N` (Zug positiv):
ungerissen bis `M_Riss(N)`, dort der Sprung, darueber gerissen bis zum
Bruch.

### normalkraft_dehnung

```python
def normalkraft_dehnung(paar: Paar, *, M: float) -> Linie
```

Die Normalkraft-Dehnungs-Linie beim Moment `M`, auf Zug: ungerissen
bis `N_Riss(M)`, dort der Sprung, darueber gerissen bis zum Bruch.
Die Dehnung ist die am Arm null -- dort greift `N` an: bei der Platte
auf halber Hoehe, beim gezeichneten Querschnitt im Schwerpunkt.


## Konstanten

- `SUCHE_DER_ANALYSEN = ILLINOIS_VON_VORN` – Wie die Loeser der Analysen suchen, bei der Platte wie am gezeichneten Querschnitt: mit Illinois, jede Frage im ganzen Fenster -- eine Linie fragt ihre Punkte in einer Reihenfolge, und keiner soll an ihr haengen. Wo ein Gesetz springt, halbierend ([[opencivil.nachweis.querschnittsloeser#wirksame_suche|wirksame_suche]]): dort faende Illinois auf einem flachen Stueck einen anderen Punkt. Bis 2026-10-18 halbierten alle; so rechnen alle Analysen des Pruefprojekts in 4.0 statt 5.2 s, die der Platte etwa fuenfmal schneller, und ihre Zahlen bewegen sich erst ab der siebten Stelle (Benutzer, 2026-10-18).
- `KURVENPUNKTE = 40` – Punkte des gerissenen Teils einer Linie -- vor dem Fliessen ein Drittel, danach der Rest, denn dort waechst die Verformung am staerksten.
- `PUNKTE_UNGERISSEN = 10` – Punkte des ungerissenen Teils. Er ist beinahe gerade.

## Braucht

- [[opencivil.core.protokoll]]
- [[opencivil.core.suche]]
- [[opencivil.core.wert]]
- [[opencivil.nachweis.querschnittsloeser]]
- [[opencivil.querschnitt.fasern]]
- [[opencivil.querschnitt.gesetzwahl]]
- [[opencivil.querschnitt.werkstoffgesetz]]
- [[opencivil.spannungsanalyse.art]]

## Gebraucht von

- [[opencivil.spannungsanalyse]]
- [[opencivil.spannungsanalyse.analysen]]
- [[opencivil.spannungsanalyse.bild]]
- [[opencivil.spannungsanalyse.herleitung]]
- [[opencivil.spannungsanalyse.modul]]
- [[opencivil.spannungsanalyse.platte]]
- [[opencivil.spannungsanalyse.schnitt]]
