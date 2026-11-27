---
erzeugt: 24a66f3b45c9
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/qa_verbund_werte.py
> was Kennzahlen und Nachweise im Verbund teilen.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/qa_verbund_werte.py)

## VERANTWORTUNG

Die Kennzahlen ([[opencivil.nachweis.qa_verbund_kennzahlen]]) und die
Nachweise je Lastfall ([[opencivil.nachweis.qa_verbund]]) lesen dieselben
Festigkeiten und schreiben dieselben Tabellen; beides steht hier, je einmal:

* je Gruppe die Festigkeit gezogen und gedrueckt ([[opencivil.nachweis.qa_verbund_werte#Verbundwerte|Verbundwerte]]) --
  fuer die Verbundstuetze auch charakteristisch und den Elastizitaetsmodul;
* die Tabelle dieser Festigkeiten mit ihrem Ansatz ([[opencivil.nachweis.qa_verbund_werte#festigkeiten|festigkeiten]]);
* die Tabelle der Bleche mit ihren Klassen ([[opencivil.nachweis.qa_verbund_werte#klassen|klassen]]);
* `β` nach 5.1.2.2 mit `x_p` und `h` ([[opencivil.nachweis.qa_verbund_werte#beta|beta]]).


## DIE FESTIGKEITEN (SIA 264:2014, 4.1.3 und 5.1.2.1)

Baustahl `f_y/γ_a` gezogen und gedrueckt, je Dicke wie im Stahl
([[opencivil.nachweis.qa_stahl_werte#Stahlwerte|Stahlwerte]]); `γ_a` ist
`γ_M1` des Baustahls -- 4.1.5 nennt 1.05, wie SIA 263. Beton gedrueckt
`0.85 η_fc f_ck/γ_c` mit `η_fc = 1` und ohne `η_t`, also nicht `f_cd`
der SIA 262; gezogen nichts (4.3.2.1). Betonstahl `f_sd` seines Materials,
gedrueckt mit dem Wert fuer Druck.


## BEMESSUNG ODER CHARAKTERISTISCH

Wie beim Stahl je Material der Wertesatz, den die Tragsicherheit waehlt:
charakteristisch ohne `γ`, der Beton dann mit `0.85 f_ck`. Die
Widerstaende heissen in beiden Faellen `Rd` (nach Vorgabe, nicht
nachgeschlagen).

## Inhalt

### stoffbezuege

```python
def stoffbezuege(verbund: Verbundquerschnitt) -> List[Eingabebezug]
```

Die Kennwerte aller Materialien des Querschnitts, als Eingaben.

### Verbundwerte

```python
class Verbundwerte
```

Die Festigkeiten der Gruppen eines Verbundquerschnitts -- siehe
Dateikopf. `beton_faktor` rechnet die Druckfestigkeit des Betons um:
0.85, im gefuellten Rohr der Verbundstuetze 1.0.

#### Verbundwerte.wert

```python
def wert(self, g: int, kurz: str) -> Wert
```

Ein Kennwert des Materials der Gruppe `g`, unter seinem Namen -- ohne die Dicke.

#### Verbundwerte.zahl

```python
def zahl(self, g: int, kurz: str) -> float
```

Derselbe als Zahl: Spannungen in N/mm², Beiwerte rein.

#### Verbundwerte.E

```python
def E(self, g: int) -> float
```

Der Elastizitaetsmodul der Gruppe `g` in N/mm²: `E_a`, `E_cm` oder `E_s`.

#### Verbundwerte.gamma

```python
def gamma(self, g: int) -> float
```

Der Beiwert der Gruppe `g` -- eins mit charakteristischen Werten.

#### Verbundwerte.kennwert

```python
def kennwert(self, g: int) -> float
```

Die charakteristische Festigkeit: `f_y` in der Dicke der Gruppe, `f_ck`, `f_sk`.

#### Verbundwerte.festigkeiten

```python
@cached_property
def festigkeiten(self) -> List[Tuple[float, float]]
```

Je Gruppe `(zug, druck)` in N/mm² -- siehe Dateikopf.

#### Verbundwerte.druck_k

```python
@cached_property
def druck_k(self) -> List[float]
```

Je Gruppe gedrueckt mit γ = 1, in N/mm²: `f_y`, der Beton umgerechnet, `f_sk`.

#### Verbundwerte.zug

```python
@property
def zug(self) -> List[float]
```

#### Verbundwerte.druck

```python
@property
def druck(self) -> List[float]
```

#### Verbundwerte.eps

```python
@property
def eps(self) -> List[float]
```

Je Gruppe des Stahls `ε`.

#### Verbundwerte.hochfest

```python
@cached_property
def hochfest(self) -> bool
```

Ob ein Baustahl S420 oder S460 ist ([[opencivil.verbund.widerstand#Konstanten|HOCHFEST]]).

#### Verbundwerte.kurz

```python
def kurz(self) -> str
```

Die Festigkeiten in einem Satz, fuer die Nachweise: sie stehen in den Kennzahlen.

### festigkeiten

```python
def festigkeiten(p: Protokoll, werte: Verbundwerte) -> None
```

Die Festigkeiten je Gruppe als Tabelle, mit dem Ansatz fuer die Arten, die vorkommen.

### klassen

```python
def klassen(p: Protokoll, zustaende: Sequence[Blechzustand], freie: Sequence[Teil], titel: str) -> Tuple[int, str]
```

Ob jedes Blech in Klasse 1 oder 2 liegt, als Tabelle -- und die Klasse
des Querschnitts, die unguenstigste, mit dem Namen dessen, was sie
bestimmt (ohne Namen in Klasse 1). 3 heisst «über 2»; gedrueckte freie
Flaechen zaehlen so.

### klasse_text

```python
def klasse_text(klasse: int) -> str
```

Eine Klasse im Verbund: 1, 2 oder «über 2».

### beta

```python
def beta(p: Protokoll, werte: Zwischenwerte, b: vw.Beta) -> Optional[Wert]
```

`β` nach 5.1.2.2 an einer Nulllinie, mit `x_p` und `h` -- `None`,
wo es eins ist und nichts mindert. Ueber 0.4 rechnet der Fall nicht
([[opencivil.verbund.widerstand#Konstanten|UEBER_FIGUR_1]]) und kommt nicht
hierher.


## Konstanten

- `REFERENZ_FESTIGKEIT = 'SIA 264:2014, 4.1.3, (1); 4.1.5; 4.3.2.1; 5.1.2.1'`
- `BETON_FAKTOR = 0.85` – Der Umrechnungsfaktor der Betondruckfestigkeit im plastischen Widerstand (5.1.2.1).
- `_KENNWERTE = {Baustoffart.BAUSTAHL: KENNWERTE, Baustoffart.BETON: ('f_ck', 'gamma_…` – Was je Material gelesen wird, nach seiner Art.
- `MODUL = {Baustoffart.BAUSTAHL: 'E_a', Baustoffart.BETON: 'E_cm', Baustoffart.…` – Der Elastizitaetsmodul je Art.
- `_GAMMA = {Baustoffart.BAUSTAHL: 'gamma_M1', Baustoffart.BETON: 'gamma_c', Baus…` – Der Beiwert je Art -- beim Baustahl `γ_M1`, im Verbund `γ_a` genannt.
- `_ANSATZ = {Baustoffart.BAUSTAHL: ('f_{yd} = \\frac{f_y}{\\gamma_a}', 'f_{yd} = …` – Je Art der Teil des Ansatzes, mit und ohne Beiwert.
- `SPANNUNG = '\\ [\\mathrm{N}/\\mathrm{mm}^2]'`
- `MIT_BETA = 'Plastischer Biegewiderstand mit β'` – Wie die Formel mit `β` in der Formelsammlung heisst -- in den Kennzahlen und je Lastfall.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.material.basis]]
- [[opencivil.nachweis.qa_stahl_werte]]
- [[opencivil.querschnitt.gesetzwahl]]
- [[opencivil.stahlbau.querschnitt]]
- [[opencivil.stahlprofile.bleche]]
- [[opencivil.verbund.querschnitt]]
- [[opencivil.verbund.widerstand]]

## Gebraucht von

- [[opencivil.nachweis.qa_verbund]]
- [[opencivil.nachweis.qa_verbund_kennzahlen]]
- [[opencivil.nachweis.qa_verbund_stuetze]]

## Formeln aus diesem Modul

- [[Abminderungsbeiwert β nach Figur 1]] · `beta`
- [[Festigkeiten im Verbundquerschnitt]] · `festigkeiten`
