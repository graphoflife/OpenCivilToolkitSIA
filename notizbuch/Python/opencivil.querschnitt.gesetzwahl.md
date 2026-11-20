---
erzeugt: 44d20ac10f42
art: modul
tags: [modul]
---
> [!abstract] opencivil/querschnitt/gesetzwahl.py
> womit ein Querschnitt rechnet.
> Paket [[opencivil.querschnitt]] · [Quelltext](../../opencivil/querschnitt/gesetzwahl.py)

## VERANTWORTUNG

Die Wahl der Werkstoffgesetze: der Wertesatz ([[opencivil.querschnitt.gesetzwahl#Werkstoffsatz|Werkstoffsatz]]) und die
Rechenart ([[opencivil.querschnitt.gesetzwahl#Rechenart|Rechenart]]), mit der Kriechzahl zusammen eine
[[opencivil.querschnitt.gesetzwahl#Rechenwahl|Rechenwahl]] -- und die eine Stelle, die daraus den Beton baut
([[opencivil.querschnitt.gesetzwahl#betongesetz|betongesetz]]), mit dem wirksamen Modul ([[opencivil.querschnitt.gesetzwahl#wirksamer_modul|wirksamer_modul]]).
Das gehoert dem Querschnitt: die Platte, der gezeichnete Querschnitt und die
Spannung-Dehnung-Analyse fragen hier, ohne dafuer einen Nachweis zu laden.
Was ein Nachweis-Kapitel davon anbietet, steht bei den Nachweisen
([[opencivil.nachweis.rechenwahl]]). Bis 2026-10-17 stand alles dort und
im Loeser, und der gezeichnete Querschnitt importierte darum aus den
Nachweisen.


## DIE RECHENARTEN

* **Handrechnung** -- im Loeser derselbe Querschnitt wie in der
  Resistenzlinie aus Handrechnung: der Spannungsblock, die Bewehrung nur auf
  Zug, je Seite zu einer Lage im Schwerpunkt zusammengefasst -- beide mit
  [[opencivil.nachweis.querschnittsloeser#je_seite|je_seite]] --, und der Beton
  auch dort gezaehlt, wo der Stahl liegt. Die gedrueckte Bewehrung zaehlt
  nicht -- in keiner anderen Rechenart fehlt sie.
* **0.85·x-Vereinfachung** -- derselbe Spannungsblock, ueber die Hoehe
  integriert, jede Faser mit ihrer mittleren Spannung. Die gedrueckte
  Bewehrung wirkt mit und verdraengt den Beton an ihrer Stelle.
* **Praezise ohne Vereinfachung** -- die Parabel-Rechteck-Beziehung, ihr
  Anstieg mit dem wirksamen Modul `E_cm/(1+phi)`, `k_sigma` nie unter 1.
* **elastisch** -- nur fuer die Stahlspannungen: der Beton linear mit
  `E_cm/(1+phi)`, hoechstens `f_c`. So rechneten sie bis 2026-10-09 fest.

Die Namen hat der Benutzer am 2026-10-12 gewaehlt; vorher hiessen sie
«Handrechnung Block 0.85·x», «Block 0.85·x genau» und «Parabel».

Die Kriechzahl wirkt nur bei praezise und elastisch: an den anderen Gesetzen
haengt kein Modul. Der Wertesatz bestimmt, wo die Plateaus liegen
([[opencivil.querschnitt.gesetzwahl#Werkstoffsatz|Werkstoffsatz]]), und wie ein Widerstand heisst -- `R_d` oder
`R_k`.


## JE MATERIAL

Den Wertesatz waehlt ein Kapitel je Material ([[opencivil.querschnitt.gesetzwahl#Wertesaetze|Wertesaetze]]), wie
die Tragsicherheit der Querschnittsanalyse es schon tat -- in jedem Modul
dieselbe Wahl (Benutzer, 2026-11-20). Bis dahin galt in der Platte, beim
Knicken, in den Stahlspannungen, den Analysen und beim E_eq eines Stabs ein
Satz fuer alle Materialien. Rechnen Beton und Stahl mit verschiedenen
Saetzen, ist ein Widerstand weder `R_d` noch `R_k`; er heisst dann
schlicht `R` (nach Vorgabe, nicht nachgeschlagen).

## Inhalt

### Werkstoffsatz

```python
class Werkstoffsatz(Wahl)
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

#### Werkstoffsatz.betonkennwerte

```python
@property
def betonkennwerte(self) -> Dict[str, str]
```

Je Rolle eines Betongesetzes
([[opencivil.querschnitt.werkstoffgesetz#Konstanten|Werte]]) der Kurzname
seines Kennwerts in diesem Satz -- `E_c` als `E_cm`, ohne Kriechen.

#### Werkstoffsatz.stahlkennwerte

```python
@property
def stahlkennwerte(self) -> Dict[str, str]
```

Dasselbe fuer ein Stahlgesetz.

### Rechenart

```python
class Rechenart(Wahl)
```

Wie der Querschnitt gerechnet wird -- siehe Dateikopf.

- `HANDRECHNUNG = 'handrechnung'`
- `BLOCK = 'block'`
- `PARABEL = 'parabel'`
- `ELASTISCH = 'elastisch'`

#### Rechenart.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Rechenart.kurz

```python
@property
def kurz(self) -> str
```

Fuer schmale Zeilen -- etwa die Auswahl auf der Karte einer Analyse.

#### Rechenart.latex

```python
@property
def latex(self) -> str
```

Der Name als Formeltext -- fuer die Zeile «Rechenwahl» der Herleitung.

#### Rechenart.mit_kriechzahl

```python
@property
def mit_kriechzahl(self) -> bool
```

Ob `phi` etwas aendert -- nur, wo ein Gesetz am Modul haengt.

#### Rechenart.mit_block

```python
@property
def mit_block(self) -> bool
```

Ob der Beton als Spannungsblock rechnet.

#### Rechenart.ohne_ebene

```python
@property
def ohne_ebene(self) -> str
```

Was statt der Probe dasteht, wenn die Suche ihre Ebene verfehlt
([[opencivil.nachweis.querschnittsloeser#Ebene|verfehlt]]) --
mit dem Spannungsblock bei viel Druck und wenig Moment. Mit der
Parabel gibt es die Ebene dort.

### Wertesaetze

```python
@dataclass(frozen=True)
class Wertesaetze
```

Je Baustoff sein Wertesatz ([[opencivil.querschnitt.gesetzwahl#Werkstoffsatz|Werkstoffsatz]]). `je_baustoff`
nennt die Baustoffe eines Bauteils mit ihrem Satz, nach Baustoff-ID
geordnet; ein anderer Baustoff rechnet mit `vorgabe` -- so auch jeder,
wo ein Kapitel einen Satz fuer alle festlegt ([[opencivil.querschnitt.gesetzwahl#Wertesaetze.alle|alle]]).
Unveraenderlich und vergleichbar: eine Wahl ist Schluessel von
Zwischenspeichern, und zwei gleiche Wahlen teilen sich eine Linie. Darum
wird ein Satz fuer alle immer zu [[opencivil.querschnitt.gesetzwahl#Wertesaetze.alle|alle]] ([[opencivil.querschnitt.gesetzwahl#Wertesaetze.je|je]]) -- sonst
rechneten die Kennzahlen, die mit Bemessungswerten fest waehlen, ihre
eigene Linie neben der gleichen der Tragsicherheit.

- `vorgabe: Werkstoffsatz = Werkstoffsatz.BEMESSUNG`
- `je_baustoff: Tuple[Tuple[str, Werkstoffsatz], ...] = ()`

#### Wertesaetze.alle

```python
@classmethod
def alle(cls, satz: Werkstoffsatz) -> 'Wertesaetze'
```

Jeder Baustoff mit demselben Satz.

#### Wertesaetze.je

```python
@classmethod
def je(cls, saetze: Mapping[str, Werkstoffsatz], vorgabe: Werkstoffsatz=Werkstoffsatz.BEMESSUNG) -> 'Wertesaetze'
```

Aus Baustoff-ID und Satz -- je Baustoff des Bauteils einer. Haben alle
denselben, ist es [[opencivil.querschnitt.gesetzwahl#Wertesaetze.alle|alle]] mit ihm.

#### Wertesaetze.von

```python
def von(self, stoff) -> Werkstoffsatz
```

Der Satz eines Baustoffs ([[opencivil.material.basis#Baustoff|id]]).

#### Wertesaetze.gewaehlt

```python
@property
def gewaehlt(self) -> FrozenSet[Werkstoffsatz]
```

Die Saetze, mit denen gerechnet wird.

#### Wertesaetze.einheitlich

```python
@property
def einheitlich(self) -> Optional[Werkstoffsatz]
```

Der Satz, wenn alle Baustoffe denselben haben -- sonst `None`.

#### Wertesaetze.index

```python
@property
def index(self) -> str
```

Wie ein Widerstand heisst: `Rd` mit Bemessungswerten, `Rk` mit
charakteristischen -- gemischt weder das eine noch das andere,
`R` (nach Vorgabe, nicht nachgeschlagen).

#### Wertesaetze.kuerzel

```python
@property
def kuerzel(self) -> str
```

Der Buchstabe am Index, `d` oder `k` -- gemischt keiner.

#### Wertesaetze.kurz

```python
@property
def kurz(self) -> str
```

Fuer Legenden: «Bemessung», «charakteristisch» -- oder «gemischt».

#### Wertesaetze.beschriftung

```python
@property
def beschriftung(self) -> str
```

Ueber einem Bild: «Bemessungswerte», «charakteristisch» -- oder «gemischte Werte».

### Rechenwahl

```python
@dataclass(frozen=True)
class Rechenwahl
```

Was ein Kapitel waehlt: Kriechzahl, Wertesatz je Baustoff, Rechenart.

- `kriechzahl: float = 0.0`
- `saetze: Wertesaetze = Wertesaetze()`
- `art: Rechenart = Rechenart.HANDRECHNUNG`
- `modul: str = 'E_cm'` – Der Kurzname des Elastizitaetsmoduls, an dem der Beton haengt: `E_cm`, bei der Verformung des Knickens `E_cd` (SIA 262:2025, 4.2.1.17). Keine Wahl des Benutzers -- das Kapitel setzt ihn.

#### Rechenwahl.satz

```python
def satz(self, stoff) -> Werkstoffsatz
```

Der Wertesatz eines Baustoffs ([[opencivil.querschnitt.gesetzwahl#Wertesaetze.von|Wertesaetze.von]]).

#### Rechenwahl.betonkennwerte

```python
def betonkennwerte(self, beton) -> Dict[str, str]
```

Die Kennwerte des Betongesetzes ([[opencivil.querschnitt.gesetzwahl#Werkstoffsatz.betonkennwerte|Werkstoffsatz.betonkennwerte]]) dieses Betons, mit dem Modul der Wahl.

#### Rechenwahl.index

```python
@property
def index(self) -> str
```

`Rd`, `Rk` oder gemischt `R` -- wie ein Widerstand dieser Wahl heisst ([[opencivil.querschnitt.gesetzwahl#Wertesaetze.index|Wertesaetze.index]]).

#### Rechenwahl.beschriftung

```python
@property
def beschriftung(self) -> str
```

Fuer Legenden: «Präzise ohne Vereinfachung, φ = 2, Bemessung» -- phi nur, wo es wirkt.

#### Rechenwahl.gleiche_linie

```python
def gleiche_linie(self, andere: 'Rechenwahl') -> bool
```

Ob `andere` dieselbe Resistenzlinie ergibt: dieselbe Rechenart und
dieselben Wertesaetze, dazu Kriechzahl und Modul, wo ein Gesetz am Modul
haengt ([[opencivil.querschnitt.gesetzwahl#Rechenart.mit_kriechzahl|Rechenart.mit_kriechzahl]]). Bis 2026-11-20 eine freie
Funktion der M-N-Interaktion, die den Modul nicht verglich: eine
Parabel mit `E_cd` haette die Linie einer mit `E_cm` bekommen.

### wirksamer_modul

```python
def wirksamer_modul(E_c: float, phi: float) -> float
```

`E_c,eff = E_c / (1 + phi)` -- das Kriechen weicht den Beton auf ([[opencivil.querschnitt.gesetzwahl#Konstanten|REFERENZ_KRIECHEN]]).

### betongesetz

```python
def betongesetz(wahl: Rechenwahl, *, f_c: float, E_c: float, eps_c1d: float, eps_c2d: float, ungerissen: bool=False) -> Gesetz
```

Der Beton einer Wahl -- im gerissenen Zustand je Rechenart, `ungerissen`
linear in Druck und Zug mit dem wirksamen Modul. Die eine Stelle fuer
beide: der Loeser der Platte, die genaue Resistenzlinie und der
gezeichnete Querschnitt bekommen ihren Beton hier. Bis 2026-10-17 gab die
Platte ihrem Loeser den ungerissenen Beton als eigenes Gesetz mit, und der
gezeichnete Querschnitt baute ihn hinter einem Schalter selbst. `E_c`
ist der Modul der Wahl ([[opencivil.querschnitt.gesetzwahl#Rechenwahl|Rechenwahl.modul]]), ohne Kriechen.


## Konstanten

- `REFERENZ_KRIECHEN = 'SIA 262:2025, 3.1.2.6.1, (12)'` – Die Kriechdehnung ist `phi` mal die elastische; zusammen `(1 + phi)` mal, und daraus folgt der wirksame Modul.

## Braucht

- [[opencivil.core.wahl]]
- [[opencivil.querschnitt.werkstoffgesetz]]

## Gebraucht von

- [[opencivil.nachweis.biegung_normalkraft]]
- [[opencivil.nachweis.handrechnung]]
- [[opencivil.nachweis.kennzahlen]]
- [[opencivil.nachweis.knicken]]
- [[opencivil.nachweis.mindestbewehrung]]
- [[opencivil.nachweis.qa_gebrauch]]
- [[opencivil.nachweis.qa_knicken]]
- [[opencivil.nachweis.querschnittsloeser]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.nachweis.resistenzlinie]]
- [[opencivil.nachweis.spannungsbegrenzung]]
- [[opencivil.pfahl.innen]]
- [[opencivil.pfahl.quer]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.beispiele]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.projekt.staebe]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.spannungsanalyse.bild]]
- [[opencivil.spannungsanalyse.herleitung]]
- [[opencivil.spannungsanalyse.linie]]
- [[opencivil.spannungsanalyse.modul]]
- [[opencivil.spannungsanalyse.platte]]
- [[opencivil.spannungsanalyse.schnitt]]
- [[opencivil.web.api]]
