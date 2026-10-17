---
erzeugt: 1579134af575
art: modul
tags: [modul]
---
> [!abstract] opencivil/querschnitt/schnittanalyse.py
> Spannung-Dehnung-Analyse am gezeichneten Querschnitt.
> Paket [[opencivil.querschnitt]] · [Quelltext](../../opencivil/querschnitt/schnittanalyse.py)

## VERANTWORTUNG

Die sechs Fragen der Spannung-Dehnung-Analyse an einen gezeichneten
Querschnitt: aus N und M, aus Randdehnungen, die M-χ- und die N-ε-Linie und
der aequivalente E-Modul darueber. Gerechnet wird mit denselben Funktionen
wie bei der Platte ([[opencivil.spannungsanalyse]]); hier steht, wie der
Querschnitt zu ihnen kommt -- das Loeserpaar je Zugseite -- und was seine
Herleitung anders schreibt.


## JE ZUGSEITE

Eine Analyse waehlt die Seite, die ein positives Moment zieht: unten, oben,
links oder rechts ([[opencivil.querschnitt.schnittanalyse#Zugseite|Zugseite]]). Die Nulllinie bleibt parallel zur
Achse, wie in der einachsigen Tragsicherheit. Das Moment um die andere
Achse, das ein unsymmetrischer Querschnitt dabei weckt, zaehlt nicht -- ein
L-Querschnitt drehte seine Nulllinie in Wirklichkeit. Die Platte rechnet
immer so.

`eps_m` ist die Dehnung im Schwerpunkt des Bruttoquerschnitts, und die
Momente beziehen sich auf ihn, wie in den Lastfaellen. «Oben» heisst der
Rand gegenueber der Zugseite, «unten» der auf ihr: bei Zug links ist oben
der rechte Rand.


## WOMIT GERECHNET WIRD

Je Analyse eine Rechenwahl wie bei der Platte -- Kriechzahl, Wertesatz,
Rechenart --, fuer jeden Werkstoff des Querschnitts dieselbe. Die
Werkstoffwahl der Tragsicherheit gilt hier nicht. Staebe in derselben Tiefe,
aus demselben Stahl, werden zu einer Lage: sie haben dieselbe Dehnung.
Zerlegt wird in so viele Streifen wie die Platte in Fasern ([[opencivil.nachweis.querschnittsloeser#Konstanten|FASERN]]),
dazu die Grenzen an jeder Ecke: eine Linie rechnet viele Ebenen, und mit den
200 Streifen der Tragsicherheit dauerte sie dreimal so lang -- fuer ein
M_Rd, das sich um zwei Zehntelpromille aendert.


## DER RISS

Am ungerissenen Bruttoquerschnitt, ohne Stahl, wie beim sproeden Versagen:

```python
M_Riss(N) = (f_ct,eff - N/A) · W          W = I / v_z
N_Riss(M) = (f_ct,eff,t - M·v/I) · A      v am Rand, den M zieht
```

`I` ist das Traegheitsmoment um die Achse der Biegung, `v_z` der
Abstand des gezogenen Rands vom Schwerpunkt. `f_ct,eff` mit `k_t` fuer
ein Drittel der Tiefe, unter Zug fuer die ganze -- die Regeln der Platte,
uebertragen; der Beton am gezogenen Rand gibt `f_ctm`. Nach Vorgabe,
nicht nachgeschlagen (`notizbuch/Notizen/TODO.md`). Bei der Platte ist
`W/A = h/6` -- dieselbe Formel.


## DER AEQUIVALENTE MODUL

Bezogen auf den Bruttoquerschnitt: `I` um die Achse der Biegung bzw.
`A`. Bei der Platte sind es `b·h³/12` und `b·h`.


## DER QUERSCHNITT NACH WAHL

Wie der gezeichnete Querschnitt mit den Gesetzen einer Rechenwahl entsteht
([[opencivil.querschnitt.schnittanalyse#querschnitt_nach_wahl|querschnitt_nach_wahl]]) und wie diese Gesetze in die Herleitung
kommen ([[opencivil.querschnitt.schnittanalyse#protokoll_gesetze_nach_wahl|protokoll_gesetze_nach_wahl]]), brauchen auch die
Gebrauchsnachweise und das Knicken -- es steht darum einmal hier.


## EINHEITEN

SI-Basis wie im ganzen Querschnittsmodul.

## Inhalt

### Zugseite

```python
class Zugseite(Wahl)
```

Die Seite, die ein positives Moment zieht -- und die Richtung, die dazu gehoert.

- `UNTEN = 'unten'`
- `OBEN = 'oben'`
- `LINKS = 'links'`
- `RECHTS = 'rechts'`

#### Zugseite.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Zugseite.psi

```python
@property
def psi(self) -> float
```

Die Zugrichtung als Winkel, wie [[opencivil.querschnitt.interaktion#Querschnitt|Querschnitt]] sie nimmt.

#### Zugseite.um_y

```python
@property
def um_y(self) -> bool
```

Ob die Biegung um die y-Achse geht -- Zug unten oder oben.

#### Zugseite.raender

```python
@property
def raender(self) -> Tuple[str, str]
```

Wie die beiden Raender heissen: der gedrueckte und der gezogene.

### _betonspannung

```python
def _betonspannung(r, gesetze: Mapping[int, Callable[[float], float]]) -> Callable[[float, float], float]
```

Die Spannung des Betons an einer Stelle, fuer das Bild: in jedem Streifen
der Beton mit der groessten Breite dort. Liegen zwei Betone in derselben
Tiefe, zeigt das Bild den, der dort ueberwiegt.

### _loeser

```python
def _loeser(q: Querschnitt, seite: Zugseite, herkunft: List[Stabgruppe], staehle: Mapping[int, Stahlgesetz], namen: Mapping[int, str]) -> Faserloeser
```

Der Querschnitt in einer Zugrichtung als [[opencivil.nachweis.querschnittsloeser#Faserloeser|Faserloeser]]. Staebe in
derselben Tiefe, aus demselben Stahl und im selben Beton werden eine Lage
-- sie haben dieselbe Dehnung, und das Bild zeigt sie als eine.

### Schnittpaar

```python
@dataclass(frozen=True)
class Schnittpaar
```

Die beiden Loeser eines gezeichneten Querschnitts in einer Zugrichtung --
gerissen und ungerissen, wie das [[opencivil.spannungsanalyse#Loeserpaar|Loeserpaar]]
der Platte. Dazu der Riss am Bruttoquerschnitt und was die Herleitung
braucht.

- `gerissen: Faserloeser`
- `ungerissen: Faserloeser`
- `seite: Zugseite`
- `wahl: Rechenwahl`
- `grenznamen: Tuple[str, ...]`
- `querschnitt: Querschnitt` – Der gerissene Querschnitt im Bruchzustand -- derselbe, aus dem `gerissen` stammt.
- `A: float` – Flaeche des Bruttoquerschnitts, m².
- `I: float` – Traegheitsmoment um die Achse der Biegung, m⁴.
- `v_oben: float`
- `v_unten: float` – Die Raender, vom Schwerpunkt in Zugrichtung gemessen: der gedrueckte (negativ) und der gezogene.
- `k_t: float`
- `f_ct_eff: float` – Fuer das Rissmoment: `k_t` fuer ein Drittel der Tiefe, `k_t·f_ctm`.
- `k_t_zug: float`
- `f_ct_eff_zug: float` – Fuer die Rissnormalkraft: `k_t` fuer die ganze Tiefe.
- `E_cm: float` – Der Modul des Betons am gezogenen Rand -- daran misst sich der aequivalente Modul.
- `staehle: Tuple[Baustoff, ...] = ()`
- `ids: Mapping[str, str] = field(default_factory=dict)` – Kurzname -> Wert-ID der Eingaben, fuer die Herleitung: der Beton am gezogenen Rand und A, I.
- `bezugsort = 'im Schwerpunkt'` – Wo die Mitteldehnung gilt -- dort greift N an.

#### Schnittpaar.W

```python
@property
def W(self) -> float
```

Das Widerstandsmoment zum gezogenen Rand, m³.

#### Schnittpaar.M_Riss

```python
@property
def M_Riss(self) -> float
```

Das Rissmoment ohne Normalkraft.

#### Schnittpaar.rissmoment_bei

```python
def rissmoment_bei(self, N: float) -> float
```

`M_Riss(N) = (f_ct,eff - N/A)·W` -- Druck hebt es, Zug senkt es.

#### Schnittpaar.rissnormalkraft_bei

```python
def rissnormalkraft_bei(self, M: float) -> float
```

`N_Riss(M) = (f_ct,eff,t - M·v/I)·A` -- `v` am Rand, den `M` zieht:
der gezogene bei positivem Moment, der gedrueckte bei negativem.

#### Schnittpaar.I_c

```python
@property
def I_c(self) -> float
```

#### Schnittpaar.A_c

```python
@property
def A_c(self) -> float
```

#### Schnittpaar.tiefe

```python
def tiefe(self, w: Zwischenwerte, ein: Callable[[str], 'Wert']) -> 'Wert'
```

Die Ausdehnung des Betons in Zugrichtung -- aus der Zeichnung, kein Wert des Rechenwerks.

#### Schnittpaar.herleitung_riss

```python
def herleitung_riss(self, p: Protokoll, w: Zwischenwerte, linie: Linie, ein: Callable[[str], 'Wert'], h: 'Wert') -> None
```

Der Riss am Bruttoquerschnitt: Widerstandsmoment, Zugfestigkeit, Risskraft.

#### Schnittpaar.herleitung_dehnung_am_ende

```python
def herleitung_dehnung_am_ende(self, p: Protokoll, w: Zwischenwerte, bruch: Grenzzustand, oben: 'Wert', unten: 'Wert') -> None
```

Die Dehnung im Schwerpunkt am Ende -- dort greift N an.

#### Schnittpaar.herleitung_bezug

```python
def herleitung_bezug(self, p: Protokoll, w: Zwischenwerte, momente: bool, ein: Callable[[str], 'Wert'], h: 'Wert') -> 'Wert'
```

Der reine Betonquerschnitt des aequivalenten Moduls: der Bruttoquerschnitt.

### querschnitt_nach_wahl

```python
def querschnitt_nach_wahl(analyse: Querschnittsanalyse, wert: Callable[[str], float], wahl: Rechenwahl, *, ungerissen: bool=False) -> Tuple[Querschnitt, List[Stabgruppe], Dict[int, Stahlgesetz]]
```

Der gezeichnete Querschnitt mit den Gesetzen einer Rechenwahl -- dazu je
Bewehrung ihr Element und je Stahl sein Gesetz, nach dem Index des
Werkstoffs. `wert` liefert zu einer Wert-ID die Zahl in SI. Zerlegt in
so viele Streifen, wie die Platte Fasern hat ([[opencivil.nachweis.querschnittsloeser#Konstanten|FASERN]]).

### protokoll_gesetze_nach_wahl

```python
def protokoll_gesetze_nach_wahl(p: Protokoll, e: Eingaben, analyse: Querschnittsanalyse, wahl: Rechenwahl, basis: str, *, titel: str) -> None
```

Die Werkstoffgesetze einer Wahl, je Material des Querschnitts -- die von
[[opencivil.querschnitt.schnittanalyse#querschnitt_nach_wahl|querschnitt_nach_wahl]]; jedes schreibt sich selbst, mit seinen
Werten, wie bei der Platte
([[opencivil.nachweis.rechenwahl#protokoll_gesetze|protokoll_gesetze]]). Vor jedem
Beton sein wirksamer Modul, wo ein Gesetz an ihm haengt.

### schnittpaar

```python
def schnittpaar(analyse: Querschnittsanalyse, seite: Zugseite, wert: Callable[[str], float], wahl: Rechenwahl) -> Optional[Schnittpaar]
```

Das Loeserpaar eines gezeichneten Querschnitts in einer Zugrichtung --
`None` ohne Bewehrung. `wert` liefert zu einer Wert-ID die Zahl in SI,
aus einer Loesung.

### analysen

```python
def analysen(aufbau: 'Aufbau', loesung: 'Loesung', protokoll: Protokoll) -> Dict[str, List[Analyse]]
```

Die Auswertungen je gezeichnetem Querschnitt -- wie
[[opencivil.spannungsanalyse#analysen|opencivil.spannungsanalyse.analysen]] je Platte, und von dort
gerufen. Mit `protokoll` schreibt jede Linie ihre Herleitung.


## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.core.wahl]]
- [[opencivil.core.wert]]
- [[opencivil.material.basis]]
- [[opencivil.nachweis.querschnittsloeser]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.nachweis.sproedes_versagen]]
- [[opencivil.projekt]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.fasern]]
- [[opencivil.querschnitt.interaktion]]
- [[opencivil.querschnitt.werkstoffgesetz]]
- [[opencivil.spannungsanalyse]]

## Gebraucht von

- [[opencivil.nachweis.qa_gebrauch]]
- [[opencivil.nachweis.qa_knicken]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.spannungsanalyse]]
- [[opencivil.web.api]]

## Formeln aus diesem Modul

- [[Grösste Dehnung im Schwerpunkt]] · `Schnittpaar.herleitung_dehnung_am_ende`
- [[Rissmoment bei der Normalkraft]] · `Schnittpaar.herleitung_riss`
- [[Rissnormalkraft beim Moment]] · `Schnittpaar.herleitung_riss`
- [[Widerstandsmoment zum gezogenen Rand]] · `Schnittpaar.herleitung_riss`
