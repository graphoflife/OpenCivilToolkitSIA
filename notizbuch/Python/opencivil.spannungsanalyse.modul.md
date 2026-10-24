---
erzeugt: f90ea76dc663
art: modul
tags: [modul]
---
> [!abstract] opencivil/spannungsanalyse/modul.py
> der aequivalente E-Modul.
> Paket [[opencivil.spannungsanalyse]] · [Quelltext](../../opencivil/spannungsanalyse/modul.py)

## VERANTWORTUNG

Die letzten zwei Fragen: eine Linie, umgerechnet in den Modul, den ein
reiner, ungerissener, elastischer Betonquerschnitt braeuchte, um sich gleich
stark zu kruemmen oder zu dehnen ([[opencivil.spannungsanalyse.modul#Modullinie|Modullinie]]). Und derselbe Modul
an einer Stelle der Linie, fuer die Staebe eines Balkensystems
([[opencivil.spannungsanalyse.modul#modul_bei|modul_bei]], [[opencivil.spannungsanalyse.modul#Modulfrage|Modulfrage]]): dort geht er in die Rechnung ein,
darum rechnet ihn das Rechenwerk, nicht die Auswertung danach.

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

### Modulstelle

```python
@dataclass(frozen=True)
class Modulstelle
```

Der aequivalente Modul bei N und M -- und woraus er folgt, fuer die Herleitung.

- `N: float`
- `M: float` – Das Moment, bei dem gerechnet wurde, zur Zugseite -- bei M = 0 das halbe Rissmoment.
- `riss: float` – `M_Riss(N)`.
- `gerissen: bool`
- `chi_0: float` – Die Kruemmung ohne Moment -- ab ihr wird gezaehlt.
- `chi: float`
- `I_c: float`
- `modul: float` – In Pa.

### modul_bei

```python
def modul_bei(paar: Paar, *, N: float, M: float) -> Tuple[Optional[Modulstelle], str]
```

Der aequivalente E-Modul bei der Normalkraft `N` (Zug positiv) und dem
Moment `M >= 0` zur Zugseite des Paars, in SI -- an derselben Stelle der
M-E_eq-Linie ([[opencivil.spannungsanalyse.modul#aequivalenter_modul|aequivalenter_modul]] ueber
[[opencivil.spannungsanalyse.linie#moment_kruemmung|moment_kruemmung]]): ungerissen
bis `M_Riss(N)`, darueber gerissen, gezaehlt ab der Kruemmung ohne
Moment. Bei `M = 0` der Wert, mit dem die Linie beginnt -- ungerissen
ist der Querschnitt linear, das halbe Rissmoment gibt ihn genau.

Ohne Gleichgewicht `None`, dazu der Satz, warum -- klein beginnend, er
steht hinter einem Doppelpunkt.

### Modulbefund

```python
@dataclass(frozen=True)
class Modulbefund
```

Was die Suche nach E_eq fand: die Stelle -- oder warum es keine gibt.

- `stelle: Optional[Modulstelle]`
- `grund: str = ''`

### Modulfrage

```python
@dataclass(frozen=True)
class Modulfrage
```

Das E_eq eines gezeichneten Querschnitts bei `N` in kN (Zug positiv)
und `M` in kNm (positiv mit Zug unten), fuer die Staebe eines
Balkensystems mit ihm (Benutzer, 2026-10-23) -- gerechnet mit `wahl`
wie eine Spannung-Dehnung-Analyse.

- `analyse: Any` – Die [[opencivil.querschnitt.analyse#Querschnittsanalyse|Querschnittsanalyse]].
- `N: float`
- `M: float`
- `wahl: Rechenwahl`

#### Modulfrage.einbauen

```python
def einbauen(self, definieren: Callable[..., WertDef], *, wo: str, index: str, name: str, abschnitt: Abschnitt) -> Tuple[List[Berechnung], str, str]
```

Die Berechnungen dazu, im Namensraum des Systems: N und M als
Vorgaben, die Suche ([[opencivil.spannungsanalyse.modul#ModulProzedur|ModulProzedur]]) und E aus ihrem Befund
([[opencivil.spannungsanalyse.modul#ModulAusBefund|ModulAusBefund]]). ``definieren(kurzname, symbol, einheit,
beschreibung, stellen)`` legt einen Wert des Systems an. Zurueck die
Berechnungen, die Wert-ID von E -- sie fehlt, wo die Suche keinen
Modul fand -- und die ID der Suche.

### ModulProzedur

```python
class ModulProzedur(Prozedur)
```

Sucht das E_eq einer [[opencivil.spannungsanalyse.modul#Modulfrage|Modulfrage]]: mit dem Paar der
Spannung-Dehnung-Analyse in der Zugrichtung des Moments
([[opencivil.spannungsanalyse.schnitt#schnittpaar|schnittpaar]]), an der Stelle
der M-E_eq-Linie ([[opencivil.spannungsanalyse.modul#modul_bei|modul_bei]]). Ohne Ausgabe -- ihr Befund ist der
[[opencivil.spannungsanalyse.modul#Modulbefund|Modulbefund]], und die Herleitung sagt, was sie fand. So haelt
ein Moment ueber dem Widerstand nur das System auf, nicht das Projekt.

#### ModulProzedur.rechne

```python
def rechne(self, e: Eingaben, p: Protokoll) -> Ausfuehrung
```

### ModulAusBefund

```python
class ModulAusBefund(Prozedur)
```

E aus dem Befund der Suche -- nur, wo sie einen Modul fand. Sonst ist sie
nicht anwendbar: E fehlt, mit ihm EA und EI, und das System sagt warum.

#### ModulAusBefund.anwendbar

```python
def anwendbar(self, e: Eingaben) -> Tuple[bool, str]
```

#### ModulAusBefund.rechne

```python
def rechne(self, e: Eingaben, p: Protokoll) -> dict
```


## Konstanten

- `NULLKRAFT = 1e-06` – Unter diesem Anteil der groessten Kraft der Linie gilt eine Kraft als null -- der erste Punkt einer gerissen beginnenden Linie traegt null bis auf die Schranke des Loesers.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.material.basis]]
- [[opencivil.querschnitt.gesetzwahl]]
- [[opencivil.querschnitt.zugseite]]
- [[opencivil.spannungsanalyse.art]]
- [[opencivil.spannungsanalyse.linie]]
- [[opencivil.spannungsanalyse.schnitt]]

## Gebraucht von

- [[opencivil.projekt.aufbau.balkensystem]]
- [[opencivil.spannungsanalyse]]
- [[opencivil.spannungsanalyse.analysen]]
- [[opencivil.spannungsanalyse.herleitung]]

## Formeln aus diesem Modul

- [[Äquivalenter E-Modul eines Stabs]] · `ModulProzedur._schreiben`
