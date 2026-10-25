---
erzeugt: 333938bd2bb4
art: modul
tags: [modul]
---
> [!abstract] opencivil/querschnitt/zugseite.py
> welche Seite ein Moment zieht.
> Paket [[opencivil.querschnitt]] · [Quelltext](../../opencivil/querschnitt/zugseite.py)

## VERANTWORTUNG

Die Zugseite eines gezeichneten Querschnitts: unten, oben, links oder
rechts -- dazu die Zugrichtung als Winkel, die Achse, um die gebogen wird,
und wie die beiden Raender heissen. Eine Wahl fuer sich, in einem eigenen
Modul: die Beschreibung des Projekts, die Nachweise und die Analysen fragen
sie, und keiner von ihnen soll dafuer die Spannung-Dehnung-Analyse laden.
Bis 2026-10-17 stand sie in der Schnittanalyse des gezeichneten Querschnitts.


## EINE SEITE, EINE FORM

Auch die Platte fragt sie: ihre Seiten sind [[opencivil.querschnitt.zugseite#Konstanten|UM_Y]], unten und oben, und
wie eine Seite in Zeichen und Kennungen heisst, sagt sie selbst
([[opencivil.querschnitt.zugseite#Zugseite.zeichen|Zugseite.zeichen]], [[opencivil.querschnitt.zugseite#Zugseite.marke|Zugseite.marke]]). Bis 2026-10-18 stand
dieselbe Seite in sechs Formen da: als Tupel der Richtungen des gezeichneten
Querschnitts, als Text der Verformung, als `pos`/`neg`, als `+`/`-`
und in drei Winkelausdruecken.

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

#### Zugseite.moment

```python
@property
def moment(self) -> Tuple[float, float]
```

Ein Moment von eins, das diese Seite zieht, als `(M_y, M_z)`: M_y > 0
zieht unten, M_z > 0 links -- wie
[[opencivil.querschnitt.interaktion#Querschnitt.neigung_fuer|neigung_fuer]].

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

#### Zugseite.gegen

```python
@property
def gegen(self) -> 'Zugseite'
```

Die Gegenseite -- die gedrueckte.

#### Zugseite.positiv

```python
@property
def positiv(self) -> bool
```

Ob ein positives Moment sie zieht: M_y > 0 zieht unten, M_z > 0 links.

#### Zugseite.zeichen

```python
@property
def zeichen(self) -> str
```

Ihr Vorzeichen, wie es an Symbolen steht: M_Rd^+ fuer Zug unten.

#### Zugseite.marke

```python
@property
def marke(self) -> str
```

Ihr Vorzeichen in Kennungen: `M_Rd_N0_pos` fuer Zug unten.

#### Zugseite.pfeil

```python
@property
def pfeil(self) -> str
```

Wohin sie zeigt, als Pfeil: ↓ fuer Zug unten. So steht sie im Schalter
der Oberflaeche, der auch in einer schmalen Spalte Platz finden muss
(Benutzer, 2026-10-23: keine Auswahllisten).

#### Zugseite.aus_moment

```python
@classmethod
def aus_moment(cls, M_y: float) -> 'Zugseite'
```

Die Seite, die ein Moment um y zieht -- bei M_y = 0 die untere, wie
die waagrechte Nulllinie einer einachsigen Rechnung es braucht.


## Konstanten

- `UM_Y = (Zugseite.UNTEN, Zugseite.OBEN)` – Die Seiten, die ein Moment um y zieht: die einer Platte, und die eines gezeichneten Querschnitts, der einachsig gerechnet wird.

## Braucht

- [[opencivil.core.wahl]]

## Gebraucht von

- [[opencivil.nachweis.gebrauchsebene]]
- [[opencivil.nachweis.handrechnung]]
- [[opencivil.nachweis.kennzahlen]]
- [[opencivil.nachweis.qa_kennzahlen]]
- [[opencivil.nachweis.qa_knicken]]
- [[opencivil.nachweis.querkraft]]
- [[opencivil.nachweis.querkraft_buegel]]
- [[opencivil.nachweis.querkraft_ohne_buegel]]
- [[opencivil.nachweis.richtungsnachweise]]
- [[opencivil.nachweis.schiefe_biegung]]
- [[opencivil.nachweis.verformung]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.platte]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.platte]]
- [[opencivil.spannungsanalyse.modul]]
- [[opencivil.spannungsanalyse.schnitt]]
- [[opencivil.web.api]]
