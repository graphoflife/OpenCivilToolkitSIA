---
erzeugt: b96048b9831f
art: modul
tags: [modul]
---
> [!abstract] opencivil/spannungsanalyse/modul.py
> der aequivalente E-Modul.
> Paket [[opencivil.spannungsanalyse]] · [Quelltext](../../opencivil/spannungsanalyse/modul.py)

## VERANTWORTUNG

Die letzten zwei Fragen: eine Linie, umgerechnet in den Modul, den ein
reiner, ungerissener, elastischer Betonquerschnitt braeuchte, um sich gleich
stark zu kruemmen oder zu dehnen ([[opencivil.spannungsanalyse.modul#Modullinie|Modullinie]]).

## Inhalt

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

Umgerechnet wird jeder Punkt der [[opencivil.spannungsanalyse.linie#Linie|Linie]]; gerechnet wird nichts
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
def aequivalenter_modul(linie: Linie, *, I_c: float, A_c: float, E_cm: float) -> Modullinie
```

Die M-chi- oder N-eps-Linie als Linie des aequivalenten Moduls -- siehe
[[opencivil.spannungsanalyse.modul#Modullinie|Modullinie]]. Beide Vergleichszustaende zaehlen ab ihrer eigenen
Verformung ohne laufende Kraft. `I_c` und `A_c` sind der reine
Betonquerschnitt, an dem sich der Modul misst.


## Konstanten

- `NULLKRAFT = 1e-06` – Unter diesem Anteil der groessten Kraft der Linie gilt eine Kraft als null -- der erste Punkt einer gerissen beginnenden Linie traegt null bis auf die Schranke des Loesers.

## Braucht

- [[opencivil.spannungsanalyse.art]]
- [[opencivil.spannungsanalyse.linie]]

## Gebraucht von

- [[opencivil.spannungsanalyse]]
- [[opencivil.spannungsanalyse.analysen]]
- [[opencivil.spannungsanalyse.herleitung]]
