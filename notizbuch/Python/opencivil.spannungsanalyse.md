---
erzeugt: 9c3181ca3a9f
art: modul
tags: [modul]
---
> [!abstract] opencivil/spannungsanalyse.py
> den Querschnitt ansehen, ohne ihn nachzuweisen.
> Paket [[opencivil]] · [Quelltext](../../opencivil/spannungsanalyse.py)

## VERANTWORTUNG

Sechs Auswertungen am selben Faserintegral, das auch die Nachweise benutzen:

1. **Aus Schnittgroessen** -- `N` und `M` hinein, Dehnungsebene und
   Spannungsverteilung heraus.
2. **Aus Dehnungen** -- Randdehnungen hinein, Spannungen und Schnittgroessen
   heraus. Die Umkehrung von 1, und ohne Suche: die Ebene steht ja schon da.
3. **Momenten-Kruemmungs-Linie** -- eine Normalkraft hinein, der Verlauf
   `M(chi)` von null bis zum Bruch heraus.
4. **Normalkraft-Dehnungs-Linie** -- ein Moment hinein, der Verlauf
   `N(eps_m)` von null bis zum Bruch auf Zug heraus.
5. **Aequivalenter E-Modul ueber dem Moment** -- die Linie aus 3,
   umgerechnet in den Modul, den ein reiner, ungerissener, elastischer
   Betonquerschnitt braeuchte, um sich gleich stark zu kruemmen.
6. **Aequivalenter E-Modul ueber der Normalkraft** -- dasselbe aus der
   Linie in 4, fuer die Dehnung.


## KEIN NACHWEIS

Hier wird nichts gegen etwas gehalten. Es gibt keinen Erfuellungsgrad und kein
Urteil -- das ist der Unterschied zu allem anderen in diesem Werkzeug und der
Grund, warum die Auswertungen nicht im [[opencivil.core.rechenwerk#Rechenwerk|Rechenwerk]] stehen. Sie
beantworten eine Frage, die man beim Entwerfen stellt: *was passiert
eigentlich im Querschnitt?*


## JE ANALYSE GEWAEHLT

Jede Analyse ([[opencivil.projekt.eintraege#SpannungsfallEintrag|SpannungsfallEintrag]]) waehlt als
[[opencivil.nachweis.rechenwahl#Rechenwahl|Rechenwahl]]

* die Kriechzahl;
* der Wertesatz -- Bemessung (`f_cd`, `f_yd`) oder charakteristisch
  (`f_ck`, `f_yk`), siehe [[opencivil.nachweis.querschnittsloeser#Werkstoffsatz|Werkstoffsatz]];
* die Rechenart -- die 0.85·x-Vereinfachung oder praezise ohne Vereinfachung,
  die Parabel mit `E_c,eff`. Die Handrechnung gibt es hier nicht
  ([[opencivil.nachweis.rechenwahl#Konstanten|FASERARTEN]]): eine Linie rechnet die
  Normalkraft Ebene fuer Ebene genau, ein Polygon aus Eckpunkten haette dort
  nichts zu suchen.

Moduln und Grenzdehnungen sind in beiden Wertesaetzen dieselben, wie ueberall
im Werkzeug.


## DIE BEIDEN LINIEN

Unter dem Riss ist der Querschnitt ungerissen (Zustand I) und deutlich
steifer, als die Nachweise ihn rechnen -- dort wird der Beton auf Zug
grundsaetzlich nicht angesetzt. Beim Riss springt die Verformung bei
derselben Kraft vom ungerissenen auf den gerissenen Wert (Zustand II), im
Bild ein waagrechtes Stueck. Darueber gilt Zustand II bis zum Bruch. Beide
Zustaende rechnet derselbe Loeser, nur mit verschiedenem Betongesetz.

Die Zugfestigkeit des Betons zaehlt nur bis zum Riss: der ungerissene
Zustand steht zum Vergleich darum nur bis `M_Riss` bzw. `N_Riss` da,
nicht darueber hinaus -- dort haette der Beton Zug ohne Grenze (Benutzer,
2026-10-12). Der gerissene Zustand steht zum Vergleich auf der ganzen Linie.


## DIE NAMEN AN DER LINIE

Ihr Ende heisst `M_Rd` bzw. `N_Rd` (`R_k` mit charakteristischen
Werten), wie der Widerstand der Tragsicherheit: bei derselben Rechenwahl ist
es dieselbe Zahl, bis auf die Schranke der Suche. Der Fliessbeginn heisst
`M_y` bzw. `N_y`, wie seine Kruemmung `chi_y`. Bis 2026-10-12 hiess er
`M_Rd` und das Ende `M_Rd,u` -- und wer im Bild nach dem Widerstand
suchte, fand den Fliessbeginn.

Den gerissenen Teil rechnet die Linie ueber die Verformung -- die Kruemmung
bzw. die Dehnung --, nicht ueber die Kraft. Nach dem Fliessen waechst die
Kraft kaum noch, die Verformung aber stark; ueber die Kraft gerechnet laegen
dort kaum Punkte, und die Suche nach einer Ebene zu einer Kraft nahe am
Widerstand ist die heikelste ueberhaupt.


## DAS ENDE

Die Linie endet bei der groessten Verformung, zu der es noch ein
Gleichgewicht gibt. Dort ist die erste Grenzdehnung erreicht: der Beton am
gedrueckten Rand bei `-eps_c2d`, der Stahl einer Lage bei `eps_ud`, der
ganz gedrueckte Querschnitt im Punkt C bei `-eps_c1d`. Dieselben Grenzen
wie im Dehnungsfaecher der genauen M-N-Linie
([[opencivil.nachweis.dehnungsfaecher]]). Bis 2026-10-09 endete die M-chi-
Linie stattdessen dort, wo die Suche des Loesers aufgab -- an der Platte des
Beispiels bei chi = 0.040 1/m statt 0.057 1/m, und `eps_ud` galt am
Betonrand statt am Stahl.

Gezeigt wird der Querschnitt, nicht das Bauteil: die Mitwirkung des Betons
zwischen den Rissen (Zugversteifung) steckt nicht darin. Mit welcher Regel
eine Linie des Bauteils zu rechnen waere, ist offen
(`notizbuch/Notizen/TODO.md`).

## Inhalt

### Analyseart

```python
class Analyseart(str, Enum)
```

Welche der sechs Fragen gestellt wird.

- `SCHNITTGROESSEN = 'schnittgroessen'`
- `DEHNUNGEN = 'dehnungen'`
- `MOMENT_KRUEMMUNG = 'moment_kruemmung'`
- `NORMALKRAFT_DEHNUNG = 'normalkraft_dehnung'`
- `MOMENT_EMODUL = 'moment_emodul'`
- `NORMALKRAFT_EMODUL = 'normalkraft_emodul'`

#### Analyseart.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Analyseart.kurz

```python
@property
def kurz(self) -> str
```

Fuer die Auswahl in der Zeile.

#### Analyseart.linie

```python
@property
def linie(self) -> Optional['Analyseart']
```

Die Linie, auf der diese Frage laeuft: M-chi oder N-eps -- der Modul
ist dieselbe Linie, umgerechnet. `None` fuer die beiden Bilder.

#### Analyseart.modul

```python
@property
def modul(self) -> bool
```

Ob gefragt ist, welchen E-Modul ein reiner Betonquerschnitt braeuchte.

### Faserpunkt

```python
@dataclass(frozen=True)
class Faserpunkt
```

Eine Stelle ueber die Hoehe, mit dem, was dort geschieht.

- `z: float` – Abstand von der **Oberkante**, in m. Dieselbe Achse, die der Loeser und der Lagenaufbau benutzen: dort ist `z` der Abstand von der gedrueckten Randfaser bei positivem Moment, und fuer eine Platte ist das die Oberkante. Die 1. Lage liegt damit bei `z = h - Randabstand` und die 4. bei `z = Randabstand`. Wer hier umdrehte, bekaeme ein Bild, das zum Nachweis nicht passt.
- `eps: float`
- `sigma: float` – in Pa, Zug positiv.

### Stahlpunkt

```python
@dataclass(frozen=True)
class Stahlpunkt(Faserpunkt)
```

Dasselbe fuer eine Bewehrungslage.

- `nummer: int`
- `a_s: float`
- `kraft: float` – `sigma * a_s` in N -- was die Lage traegt.

### Querschnittsbild

```python
@dataclass
class Querschnittsbild
```

Dehnungsebene, Spannungen und die daraus entstehenden Schnittgroessen.

- `eps_m: float`
- `chi: float`
- `N: float`
- `M: float`
- `beton: List[Faserpunkt] = field(default_factory=list)`
- `stahl: List[Stahlpunkt] = field(default_factory=list)`
- `konvergiert: bool = True`
- `hinweis: str = ''`

#### Querschnittsbild.nulllinie

```python
@property
def nulllinie(self) -> Optional[float]
```

Wo die Dehnung null wird, von der Oberkante aus.

`None`, wenn der ganze Querschnitt auf einer Seite liegt -- dann
gibt es keine Nulllinie, und eine hinzurechnen hiesse, eine Zahl zu
zeigen, die es nicht gibt.

### _bild

```python
def _bild(loeser: Querschnittsloeser, eps_m: float, chi: float) -> Querschnittsbild
```

Dehnungen und Spannungen zu einer gegebenen Ebene -- ohne jede Suche.

### aus_schnittgroessen

```python
def aus_schnittgroessen(loeser: Querschnittsloeser, *, N: float, M: float) -> Querschnittsbild
```

Die Dehnungsebene zu `N` und `M`, samt allem, was darauf steht.

Gesucht wird mit demselben Verfahren wie in den Nachweisen. Findet sich
keine Ebene, kommt das Bild leer zurueck und sagt warum -- geraten wird
nicht.

### aus_dehnungen

```python
def aus_dehnungen(loeser: Querschnittsloeser, *, eps_oben: float, eps_unten: float) -> Querschnittsbild
```

Der umgekehrte Weg: die Ebene ist gegeben, gesucht sind die Kraefte.

Hier gibt es nichts zu suchen -- aus den beiden Randdehnungen folgen
Mitteldehnung und Kruemmung unmittelbar, und das Faserintegral liefert
Normalkraft und Moment in einem Durchgang.

### beton_ungerissen

```python
def beton_ungerissen(*, E_c: float) -> Callable[[float], float]
```

Beton linear in beiden Richtungen -- der ungerissene Vergleichszustand.

Ohne Abminderung im Zug und ohne Abbruch bei `f_ct`. Das ist Absicht:
gebraucht wird die *Steifigkeit* des ungerissenen Querschnitts, und wo er
reisst, sagt das Rissmoment -- oberhalb davon gilt die Linie gerissen,
dieser Zustand steht dort nur noch zum Vergleich. Ein Gesetz, das bei
`f_ct` abfiele, waere ausserdem nicht mehr monoton, und die Bisektion
des Loesers braucht Monotonie.

### Loeserpaar

```python
@dataclass(frozen=True)
class Loeserpaar
```

Die beiden Querschnittsloeser einer Tragrichtung -- gerissen und nicht.

Sie unterscheiden sich in genau einem Stueck, dem Betongesetz. Alles
andere -- Hoehe, Breite, Lagen, Stahlgesetz, Grenzen -- ist dasselbe, und
das muss es sein: sonst verglichen die beiden Zustaende zwei verschiedene
Querschnitte. Dazu, was zum Riss und zum Fliessen gehoert, und womit
gerechnet wird.

- `gerissen: Querschnittsloeser`
- `ungerissen: Querschnittsloeser`
- `M_Riss: float` – Das Rissmoment ohne Normalkraft -- mit `k_t` fuer ein Drittel der Dicke.
- `k_t_zug: float = 1.0`
- `f_ct_eff_zug: float = 0.0` – Fuer die Rissnormalkraft: `k_t` fuer die ganze Dicke und `k_t·f_ctm`.
- `eps_y: float = math.inf` – Wo der Stahl zu fliessen beginnt: `f_s / E_s`.
- `wahl: Rechenwahl = Rechenwahl(art=Rechenart.PARABEL)` – Womit gerechnet wird -- Kriechzahl, Wertesatz, Rechenart.
- `grenznamen: Tuple[str, ...] = ()` – Je Grenze des gerissenen Loesers, was sie ist -- fuer «massgebend».
- `ids: Mapping[str, str] = field(default_factory=dict)` – Kurzname -> Wert-ID der Eingaben, fuer die Herleitung.
- `E_cm: float = 0.0` – Der Modul des Betons -- daran misst sich der aequivalente Modul.

#### Loeserpaar.rissmoment_bei

```python
def rissmoment_bei(self, N: float) -> float
```

Das Rissmoment bei der Normalkraft `N` (Zug positiv), in Nm.

Am Bruttoquerschnitt reisst der Rand, wenn `N/A + M/W = f_ct,eff`.
Mit `A = b·h` und `W = b·h²/6` -- denselben Werten, mit denen
[[opencivil.nachweis.sproedes_versagen#rissmoment|rissmoment]] das
Rissmoment ohne Normalkraft rechnet -- ist das
`M_Riss(N) = M_Riss(0) - N·h/6`. Druck hebt es, Zug senkt es.

Annahme, nicht nachgeschlagen (`notizbuch/Notizen/TODO.md`): der
Bruttoquerschnitt ohne Stahl, wie beim spröden Versagen. Der
ungerissene Zustand daneben rechnet mit Stahl und Kriechzahl und ist
darum steifer; beim Rissmoment steht sein Rand etwas unter
`f_ct,eff`.

`f_ct,eff` mit `k_t` fuer ein Drittel der Dicke, auch unter Zug:
Biegung bleibt bei `h/3`, nach Vorgabe. Die Rissnormalkraft nimmt die
ganze Dicke ([[opencivil.spannungsanalyse#Loeserpaar.rissnormalkraft_bei|rissnormalkraft_bei]]); beim selben N und M reissen
die beiden Linien darum nicht am selben Punkt.

#### Loeserpaar.rissnormalkraft_bei

```python
def rissnormalkraft_bei(self, M: float) -> float
```

Die Zugkraft, bei der der Querschnitt mit dem Moment `M` reisst, in N.

Am Bruttoquerschnitt reisst der Rand, wenn `N/A + |M|/W = f_ct,eff`,
also `N_Riss(M) = f_ct,eff·b·h - 6·|M|/h`. Das Vorzeichen des
Moments zaehlt nicht -- der Querschnitt ist oben wie unten derselbe.

`f_ct,eff` mit `k_t = 1/(1 + 0.5·t)` fuer die ganze Dicke,
`t = h`: unter Zug reisst der ganze Querschnitt, nicht ein Drittel
wie unter Biegung. Nach Vorgabe, nicht nachgeschlagen
(`notizbuch/Notizen/TODO.md`). Bis 2026-10-09 galt das `f_ct,eff`
des Rissmoments, mit `t = h/3` -- am Beispiel 829 statt 757 kN.

### loeserpaar

```python
def loeserpaar(querschnitt, richtung: Richtung, wert: Callable[[str], float], *, wahl: Rechenwahl=Rechenwahl(art=Rechenart.PARABEL)) -> Optional[Loeserpaar]
```

Das Loeserpaar einer Platte in einer Richtung -- `None` ohne Bewehrung.

`wert` liefert zu einer Wert-ID die Zahl in SI, aus einer Loesung.
`wahl` sagt, womit gerechnet wird: Kriechzahl, Wertesatz, Rechenart --
die Gesetze dazu baut [[opencivil.nachweis.rechenwahl#gesetze|gesetze]].

Stand frueher in der Schnittstelle zur Oberflaeche. Dort war sie ohne
Oberflaeche nicht erreichbar, und ein Test baute sie als eigene Kopie
nach -- er pruefte seine Kopie statt der echten.

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

### Linie

```python
@dataclass
class Linie
```

`M(chi)` bei festgehaltener Normalkraft oder `N(eps_m)` bei
festgehaltenem Moment -- welche, sagt [[opencivil.spannungsanalyse#Linie|art]].

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

`ebene` fuehrt von einer Verformung zur gerissenen Ebene ``(eps_m,
chi)` oder zu `None`, wo es kein Gleichgewicht gibt; `kraft`` liest
aus der Ebene die Kraft der Linie; `verformung_bei` sucht zu einer Kraft
die Verformung, mit einem der beiden Loeser.

- `ebene: Callable[[float], Optional[Tuple[float, float]]]`
- `kraft: Callable[[Tuple[float, float]], float]`
- `verformung_bei: Callable[[Querschnittsloeser, float], Optional[float]]`
- `obergrenze: float` – Eine Verformung, ueber der es sicher kein Gleichgewicht mehr gibt.

### _grenze

```python
def _grenze(gut: Callable[[float], bool], unten: float, oben: float) -> float
```

Wo `gut` endet, zwischen `unten` (gut) und `oben` -- durch Halbieren.

### _massgebend

```python
def _massgebend(paar: Loeserpaar, eps_m: float, chi: float) -> str
```

Welche Grenzdehnung die Ebene erreicht -- die mit dem kleinsten Abstand.

### _linie

```python
def _linie(paar: Loeserpaar, weg: _Weg, art: Analyseart, fest: float, riss: float) -> Linie
```

Die Linie von null bis zum Bruch: ungerissen bis `riss`, dort der
Sprung, darueber gerissen -- ueber die Verformung gerechnet, mit dem
Fliessbeginn als Punkt der Linie.

### moment_kruemmung

```python
def moment_kruemmung(paar: Loeserpaar, *, N: float) -> Linie
```

Die Momenten-Kruemmungs-Linie bei der Normalkraft `N` (Zug positiv):
ungerissen bis `M_Riss(N)`, dort der Sprung, darueber gerissen bis zum
Bruch.

### normalkraft_dehnung

```python
def normalkraft_dehnung(paar: Loeserpaar, *, M: float) -> Linie
```

Die Normalkraft-Dehnungs-Linie beim Moment `M`, auf Zug: ungerissen
bis `N_Riss(M)`, dort der Sprung, darueber gerissen bis zum Bruch.
Die Dehnung ist die auf halber Hoehe -- dort greift `N` an.

### Modulpunkt

```python
@dataclass(frozen=True)
class Modulpunkt
```

Ein Punkt der Linie des aequivalenten Moduls: die laufende Kraft und der
Modul, der dort gilt -- dazu beide Zustaende zum Vergleich, wie bei der
Linie, aus der er stammt.

- `kraft: float`
- `modul: Optional[float]` – In Pa; `None`, wo er nichts sagt.
- `gerissen: bool`
- `modul_I: Optional[float]`
- `modul_II: Optional[float]`

### Modullinie

```python
@dataclass
class Modullinie
```

Der aequivalente E-Modul ueber dem Moment oder ueber der Normalkraft.

Der Modul, den ein reiner Betonquerschnitt braeuchte -- ungerissen, ohne
Stahl, elastisch --, um sich unter der laufenden Kraft gleich stark zu
kruemmen bzw. zu dehnen wie der bewehrte Querschnitt:

```
E_eq = M / (I_c · (chi - chi_0))       I_c = b·h³/12
E_eq = N / (A_c · (eps_m - eps_0))     A_c = b·h
```

Gezaehlt wird ab dem Zustand ohne laufende Kraft -- `chi_0` bei M = 0
unter der festen Normalkraft, `eps_0` bei N = 0 unter dem festen
Moment --, nach Vorgabe (2026-10-11). Was die festgehaltene Kraft allein
verformt, kann ein gerader, ungerissener Betonquerschnitt nicht abbilden:
bei unsymmetrischer Bewehrung kruemmt schon eine Normalkraft, und ein
gerissener Querschnitt dehnt sich schon unter dem Moment allein. Ab null
gezaehlt, ergaebe das nahe null Ausreisser -- am Beispiel bei M = 30 kNm
und N = 16 kN 99 500 N/mm², fast das Dreifache von E_cm. Ist die feste
Kraft null, ist es genau `M = E·I·chi` bzw. `N = E·A·eps`.

Umgerechnet wird jeder Punkt der [[opencivil.spannungsanalyse#Linie|Linie]]; gerechnet wird nichts
Neues. So kann diese Linie nichts anderes zeigen als die M-chi- oder
N-eps-Linie daneben.

- `art: Analyseart`
- `linie: Linie` – Die M-chi- oder N-eps-Linie, aus der umgerechnet wird.
- `bezug: float` – `I_c` in m⁴ bzw. `A_c` in m² -- der reine Betonquerschnitt.
- `null: float` – Die Verformung ohne laufende Kraft: `chi_0` bzw. `eps_0`.
- `E_cm: float` – Zum Vergleich: `E_eq/E_cm` ist der Faktor, um den man E_cm abmindert.
- `punkte: List[Modulpunkt] = field(default_factory=list)`

#### Modullinie.modul

```python
def modul(self, kraft: float, verformung: float) -> Optional[float]
```

`Kraft / (Bezug · (Verformung − null))` -- `None`, wo das nichts sagt.

#### Modullinie.ungerissen

```python
@property
def ungerissen(self) -> Optional[float]
```

Der Modul des ungerissenen Teils -- dort ist der Querschnitt linear.

#### Modullinie.riss

```python
@property
def riss(self) -> Optional[float]
```

Der Modul gleich nach dem Riss, bei derselben Kraft.

#### Modullinie.fliessen

```python
@property
def fliessen(self) -> Optional[float]
```

#### Modullinie.ende

```python
@property
def ende(self) -> Optional[float]
```

Der Modul am Ende der Linie -- beim Bruch, oder ungerissen, wenn sie es bleibt.

### aequivalenter_modul

```python
def aequivalenter_modul(linie: Linie, *, b: float, h: float, E_cm: float) -> Modullinie
```

Die M-chi- oder N-eps-Linie als Linie des aequivalenten Moduls -- siehe
[[opencivil.spannungsanalyse#Modullinie|Modullinie]]. Beide Vergleichszustaende zaehlen ab ihrer eigenen
Verformung ohne laufende Kraft.

### _herleitung

```python
def _herleitung(p: Protokoll, fall, paar: Loeserpaar, linie: Linie, werte: Mapping[str, 'Wert'], raum: str, modul: Optional[Modullinie]=None) -> None
```

Wie die Linie entstand -- mit den Zahlen dieses Falls, und ohne sie in der
Formelsammlung, die daraus «Spannung-Dehnung-Analyse» bildet. Mit
`modul` dazu, wie aus ihr der aequivalente E-Modul wird.

### _herleitung_modul

```python
def _herleitung_modul(p: Protokoll, w: Zwischenwerte, modul: Modullinie, *, b: 'Wert', h: 'Wert') -> None
```

Der aequivalente Modul: der reine Betonquerschnitt, die Formel und der
Modul an den Ecken der Linie -- jede Zeile mit Kraft und Verformung, also
von Hand nachzurechnen.

### Analyse

```python
@dataclass
class Analyse
```

Ein Spannungsfall der Beschreibung -- und was die Auswertung ergab.

- `fall: Any` – Der [[opencivil.spannungsanalyse#Analyse|SpannungsfallEintrag]], wie er in der Beschreibung steht.
- `art: Analyseart`
- `richtung: Richtung`
- `h: float = 0.0` – Plattendicke in m -- fuer das Bild.
- `bild: Optional[Querschnittsbild] = None`
- `kurve: Optional[Union[Linie, 'Modullinie']] = None` – Die M-chi- oder N-eps-Linie -- oder der aequivalente Modul daraus.
- `paar: Optional[Loeserpaar] = None` – Womit gerechnet wurde -- Kriechzahl, Wertesatz, Betongesetz.
- `hinweis: str = ''` – Warum es nichts auszuwerten gab, falls es nichts gab.

#### Analyse.moeglich

```python
@property
def moeglich(self) -> bool
```

### auswerten

```python
def auswerten(fall, art: Analyseart, paar: Loeserpaar) -> Tuple[Optional[Querschnittsbild], Optional[Union[Linie, Modullinie]]]
```

Die eine der sechs Fragen stellen, die dieser Fall stellt -- in SI.

### analysen

```python
def analysen(aufbau: 'Aufbau', loesung: 'Loesung', protokoll: Optional[Protokoll]=None) -> Dict[str, List[Analyse]]
```

Die Auswertungen am Querschnitt, je Platte.

Kein Nachweis: hier steht kein Erfuellungsgrad und kein Urteil, sondern
eine Antwort auf die Frage, was im Querschnitt geschieht. Gerechnet wird
trotzdem mit demselben Faserintegral und denselben Werkstoffgesetzen wie
in den Nachweisen -- ein zweites Modell daneben waere eine zweite
Wahrheit ueber denselben Querschnitt.

Mit `protokoll` schreibt jede Linie dorthin, wie sie entstand -- daraus
sammelt die Formelsammlung ihr Thema.


## Konstanten

- `STUETZSTELLEN = 41` – Punkte ueber die Hoehe, mit denen Dehnung und Spannung gezeichnet werden. Die Betonspannung hat am Nulldurchgang einen Knick; 41 Punkte zeigen ihn, ohne dass die Kurve eckig wird.
- `KURVENPUNKTE = 40` – Punkte des gerissenen Teils einer Linie -- vor dem Fliessen ein Drittel, danach der Rest, denn dort waechst die Verformung am staerksten.
- `PUNKTE_UNGERISSEN = 10` – Punkte des ungerissenen Teils. Er ist beinahe gerade.
- `THEMA = 'Spannung-Dehnung-Analyse'` – Unter diesem Thema steht in der Formelsammlung, wie die Linien entstehen.
- `NULLKRAFT = 1e-06` – Unter diesem Anteil der groessten Kraft der Linie gilt eine Kraft als null -- der erste Punkt einer gerissen beginnenden Linie traegt null bis auf die Schranke des Loesers.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.core.wert]]
- [[opencivil.material.betonstahl]]
- [[opencivil.nachweis.dehnungsfaecher]]
- [[opencivil.nachweis.querschnittsloeser]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.nachweis.sproedes_versagen]]
- [[opencivil.projekt]]
- [[opencivil.querschnitt.platte]]
- [[opencivil.querschnitt.werkstoffgesetz]]

## Gebraucht von

- [[opencivil.bericht.formelsammlung]]
- [[opencivil.ergebnis]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.web.api]]
- [[opencivil.web.diagrammdaten]]

## Formeln aus diesem Modul

- [[Äquivalenter E-Modul über dem Moment]] · `_herleitung_modul`
- [[Äquivalenter E-Modul über der Normalkraft]] · `_herleitung_modul`
- [[Beiwert der Parabel, mit dem wirksamen Modul]] · `_herleitung`
- [[Beton ungerissen, in Druck und Zug]] · `_herleitung`
- [[Fläche eines Rechtecks]] · `_herleitung_modul`
- [[Flächenträgheitsmoment eines Rechtecks]] · `_herleitung_modul`
- [[Fliessdehnung]] · `_herleitung`
- [[Grenzdehnungen am Ende der Linie]] · `_herleitung`
- [[Grösste Dehnung auf halber Höhe]] · `_herleitung`
- [[Grösste Krümmung]] · `_herleitung`
- [[Parabel-Rechteck-Beziehung des Betons]] · `_herleitung`
- [[Rissmoment bei der Normalkraft]] · `_herleitung`
- [[Rissnormalkraft beim Moment]] · `_herleitung`
- [[Spannungsblock des Betons]] · `_herleitung`
- [[Wirksamer Elastizitätsmodul]] · `_herleitung`
