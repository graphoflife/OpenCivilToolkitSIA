---
erzeugt: 0437fb2cbad9
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


## Braucht

- [[opencivil.core.wahl]]

## Gebraucht von

- [[opencivil.nachweis.qa_knicken]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.spannungsanalyse.schnitt]]
- [[opencivil.web.api]]
