---
erzeugt: a63fee94e1bd
art: modul
tags: [modul]
---
> [!abstract] opencivil/spannungsanalyse/rissfrei.py
> das Paar eines Querschnitts, der nicht reisst.
> Paket [[opencivil.spannungsanalyse]] · [Quelltext](../../opencivil/spannungsanalyse/rissfrei.py)

## VERANTWORTUNG

Wie ein gezeichneter Querschnitt aus Baustahl oder Holz zu den sechs Fragen
kommt ([[opencivil.spannungsanalyse.rissfrei#RissfreiesPaar|RissfreiesPaar]], ein
[[opencivil.spannungsanalyse.linie#Paar|Paar]], seit 2026-11-26). Ohne Beton
reisst er nicht: er hat einen Zustand, seine beiden Loeser sind derselbe, und
jede Linie laeuft ganz ueber die Verformung, von der festgehaltenen Kraft
allein bis zum Ende. Fliessen beginnt, wo eine Faser ihren elastischen
Bereich verlaesst -- Baustahl auf Zug und Druck, Holz auf Druck, wenn es dort
elastisch-plastisch rechnet
([[opencivil.querschnitt.werkstoffgesetz#Gesetz.fliessbereich|fliessbereich]]). Seine
Ebenen findet er wie der Stahlbeton
([[opencivil.spannungsanalyse.schnitt#AmSchnitt|AmSchnitt]]).


## DER AEQUIVALENTE MODUL

Bezogen auf den Querschnitt selbst, mit dem Modul seines Materials: `E_a`
beim Baustahl, `E_0,mean` beim Holz. Solange keine Faser fliesst, ist
`E_eq` genau dieser Modul -- kippt die Nulllinie, mit `I - I_yz²/I_quer`
([[opencivil.nachweis.rissgroessen#Bruttoquerschnitt.traegheit|traegheit]]).


## NACH VORGABE, NICHT NACHGESCHLAGEN

Ist der Querschnitt aus mehreren Materialien derselben Art -- zwei Hoelzer,
zwei Baustaehle --, misst sich der Modul an dem mit der groessten Flaeche.


## EINHEITEN

SI-Basis wie im ganzen Querschnittsmodul.

## Inhalt

### RissfreiesPaar

```python
@dataclass(frozen=True)
class RissfreiesPaar(AmSchnitt)
```

Das Paar eines Querschnitts ohne Beton in einer Zugrichtung: ein Loeser
fuer beide Zustaende, dazu seine Zerlegung fuer die kippende Nulllinie,
seine Traegheitsmomente fuer den Modul und was die Herleitung braucht.

- `gerissen: Faserloeser` – Der eine Zustand -- «gerissen» heisst er nur, weil jedes Paar so fragt.
- `seite: Zugseite`
- `wahl: Rechenwahl`
- `zerlegung: Zerlegung` – Derselbe Zustand in jeder Richtung -- fuer die kippende Nulllinie.
- `brutto: Bruttoquerschnitt` – Die Traegheitsmomente des Querschnitts mit der Wahl der Biegung -- ohne Ecken: er reisst nicht.
- `A: float` – Flaeche des Querschnitts, m².
- `stoffe: Tuple[Baustoff, ...]` – Die Materialien der Flaechen, jedes einmal -- zuerst das mit der groessten Flaeche.
- `gesetze: Tuple[Gesetz, ...]` – Je Material sein Gesetz, wie die Wahl es will.
- `E: float` – Der Modul des ersten Materials, Pa -- Massstab des aequivalenten Moduls.
- `ids: Mapping[str, str] = field(default_factory=dict)` – Kurzname -> Wert-ID der Eingaben, fuer die Herleitung: A und I.
- `OHNE_FLIESSEN = 'Bis zum Bruch fliesst keine Faser: der Querschnitt bleibt linear, bi…`
- `mit_kriechzahl = False` – Ohne Beton kriecht nichts.
- `vorgespannt = False` – Spannglieder liegen nur im Beton.

#### RissfreiesPaar.ungerissen

```python
@property
def ungerissen(self) -> Faserloeser
```

Derselbe Loeser: ohne Beton gibt es keinen zweiten Zustand.

#### RissfreiesPaar.ebenen

```python
def ebenen(self) -> Zustaende
```

Eine Ebenensuche fuer beide Zustaende ([[opencivil.spannungsanalyse.schnitt#AmSchnitt.zustand|zustand]]).

#### RissfreiesPaar.rissmoment_bei

```python
def rissmoment_bei(self, N: float) -> None
```

Kein Riss.

#### RissfreiesPaar.rissnormalkraft_bei

```python
def rissnormalkraft_bei(self, M: float) -> None
```

Kein Riss.

#### RissfreiesPaar.flaeche

```python
@property
def flaeche(self) -> str
```

Woraus die Flaeche ist: «Baustahl» oder «Holz».

#### RissfreiesPaar.rechenart

```python
@property
def rechenart(self) -> str
```

Wie das Holz rechnet, in Worten -- beim Baustahl gibt es nichts zu waehlen.

#### RissfreiesPaar.beschriftung

```python
@property
def beschriftung(self) -> str
```

Die Wahl in Worten: wie das Holz rechnet, dazu der Wertesatz.

#### RissfreiesPaar.modulbezug

```python
@property
def modulbezug(self) -> Modulbezug
```

Der Querschnitt selbst, mit dem Modul seines ersten Materials.

#### RissfreiesPaar.herleitung_gesetze

```python
def herleitung_gesetze(self, p: Protokoll, w: Zwischenwerte, linie: 'Linie', ein: Callable[[str], 'Wert'], werte: Mapping[str, 'Wert']) -> Tuple['Wert', 'Wert', 'Wert']
```

Was vor dem Ende der Linie steht: dass nichts reisst, das Gesetz jedes
Materials, wo es zu fliessen beginnt und wo die Linie endet. Zurueck
die Tiefe und `A`, `I` des Querschnitts.

#### RissfreiesPaar.herleitung_traegheit

```python
def herleitung_traegheit(self, p: Protokoll, w: Zwischenwerte, I: 'Wert') -> 'Wert'
```

Der Bezug ueber dem Moment: der Querschnitt selbst -- gekippt mit `I - I_yz²/I_quer`.

#### RissfreiesPaar.herleitung_flaeche

```python
def herleitung_flaeche(self, p: Protokoll, w: Zwischenwerte, A: 'Wert') -> 'Wert'
```

Der Bezug ueber der Normalkraft: der Querschnitt selbst.

### rissfreies_paar

```python
def rissfreies_paar(analyse: Querschnittsanalyse, seite: Zugseite, wert: Callable[[str], float], wahl: Rechenwahl) -> RissfreiesPaar
```

Das Paar eines gezeichneten Querschnitts ohne Beton in einer Zugrichtung.
`wert` liefert zu einer Wert-ID die Zahl in SI, aus einer Loesung.


## Konstanten

- `_MODUL = {Baustoffart.BAUSTAHL: 'E_a', Baustoffart.HOLZ: 'E_0_mean'}` – Je Art der Kennwert, an dessen Modul sich `E_eq` misst.

## Braucht

- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.material.basis]]
- [[opencivil.material.betonstahl]]
- [[opencivil.nachweis.querschnittsloeser]]
- [[opencivil.nachweis.rissgroessen]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.gesetzwahl]]
- [[opencivil.querschnitt.werkstoffgesetz]]
- [[opencivil.querschnitt.zugseite]]
- [[opencivil.spannungsanalyse.linie]]
- [[opencivil.spannungsanalyse.schnitt]]

## Gebraucht von

- [[opencivil.spannungsanalyse.analysen]]
