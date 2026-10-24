---
erzeugt: 240e7275baec
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
  Zug, je Seite zu einer Lage im Schwerpunkt zusammengefasst, und der Beton
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

### Rechenwahl

```python
@dataclass(frozen=True)
class Rechenwahl
```

Was ein Kapitel waehlt: Kriechzahl, Wertesatz, Rechenart.

- `kriechzahl: float = 0.0`
- `satz: Werkstoffsatz = Werkstoffsatz.BEMESSUNG`
- `art: Rechenart = Rechenart.HANDRECHNUNG`

#### Rechenwahl.index

```python
@property
def index(self) -> str
```

`Rd` oder `Rk` -- wie ein Widerstand dieser Wahl heisst.

#### Rechenwahl.beschriftung

```python
@property
def beschriftung(self) -> str
```

Fuer Legenden: «Präzise ohne Vereinfachung, φ = 2, Bemessung» -- phi nur, wo es wirkt.

### wirksamer_modul

```python
def wirksamer_modul(E_cm: float, phi: float) -> float
```

`E_c,eff = E_cm / (1 + phi)` -- das Kriechen weicht den Beton auf.

### betongesetz

```python
def betongesetz(wahl: Rechenwahl, *, f_c: float, E_cm: float, eps_c1d: float, eps_c2d: float, ungerissen: bool=False) -> Gesetz
```

Der Beton einer Wahl -- im gerissenen Zustand je Rechenart, `ungerissen`
linear in Druck und Zug mit dem wirksamen Modul. Die eine Stelle fuer
beide: der Loeser der Platte, die genaue Resistenzlinie und der
gezeichnete Querschnitt bekommen ihren Beton hier. Bis 2026-10-17 gab die
Platte ihrem Loeser den ungerissenen Beton als eigenes Gesetz mit, und der
gezeichnete Querschnitt baute ihn hinter einem Schalter selbst.


## Braucht

- [[opencivil.core.wahl]]
- [[opencivil.querschnitt.werkstoffgesetz]]

## Gebraucht von

- [[opencivil.nachweis.biegung_normalkraft]]
- [[opencivil.nachweis.handrechnung]]
- [[opencivil.nachweis.kennzahlen]]
- [[opencivil.nachweis.knicken]]
- [[opencivil.nachweis.qa_gebrauch]]
- [[opencivil.nachweis.qa_knicken]]
- [[opencivil.nachweis.querschnittsloeser]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.nachweis.resistenzlinie]]
- [[opencivil.nachweis.spannungsbegrenzung]]
- [[opencivil.projekt.balkensystem]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.projekt]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.spannungsanalyse.bild]]
- [[opencivil.spannungsanalyse.herleitung]]
- [[opencivil.spannungsanalyse.linie]]
- [[opencivil.spannungsanalyse.modul]]
- [[opencivil.spannungsanalyse.platte]]
- [[opencivil.spannungsanalyse.schnitt]]
- [[opencivil.web.api]]
