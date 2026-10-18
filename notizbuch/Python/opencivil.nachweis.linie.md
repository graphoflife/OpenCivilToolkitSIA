---
erzeugt: 32a20411fa34
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/linie.py
> Geometrie einer geschlossenen M-N-Linie.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/linie.py)

## VERANTWORTUNG

Punkt-in-Linie, Schnitte mit einer Geraden, kuerzester Abstand. Reine
Geometrie -- von Beton, Stahl und Norm weiss dieser Baustein nichts.


## WARUM EIGENSTAENDIG

Es gibt zwei Resistenzlinien: die punktweise aus Dehnungsebenen aufgebaute
([[opencivil.nachweis.dehnungsfaecher]]) und das Polygon aus der
Handrechnung ([[opencivil.nachweis.handrechnung]]). Beide werden auf genau
dieselbe Art ausgewertet. Laege die Geometrie bei einer der beiden, muesste die
andere sie entweder einbinden -- was einen Ring ergaebe -- oder nachbauen. Das
zweite waere der Anfang vom Auseinanderlaufen.


## DIE ACHSE IST EIN WERT

Ob ein Widerstand bei festgehaltener Normalkraft (waagrecht) oder bei
festgehaltenem Moment (senkrecht) gesucht wird, steckt in [[opencivil.nachweis.linie#Achse|Achse]].
Vorher stand dieselbe Unterscheidung vierfach da -- als Funktionspaar
`..._bei_N`/`..._bei_M`, als `positiv`-Schalter, als Zeichenkette `"M"`
und als Enum-Mitglied -- und wurde an sechs Stellen abgefragt. Jetzt gibt es
sie einmal, und die Funktionen hier kennen nur noch *eine* Achse und ihre
Gegenachse.


## VORZEICHEN

```
N > 0   Zug
M > 0   Zug an der Unterseite
```
Ein Punkt ist alles, was `N` und `M` hat; die Linie ist eine Folge solcher
Punkte, deren letzter mit dem ersten verbunden gedacht wird.

## Inhalt

### Punkt

```python
class Punkt(Protocol)
```

Alles, was eine Normalkraft und ein Moment hat.

- `N: float`
- `M: float`

### Stelle

```python
@dataclass(frozen=True)
class Stelle
```

Ein schlichter Punkt der M-N-Ebene -- etwa eine Einwirkung.

- `N: float`
- `M: float`

### Achse

```python
@dataclass(frozen=True)
class Achse
```

Eine der beiden Achsen der M-N-Ebene, samt allem, was sie unterscheidet.

`name` ist zugleich der Feldname eines [[opencivil.nachweis.linie#Punkt|Punkt]] -- damit kommt
[[opencivil.nachweis.linie#Achse.von|von]] ohne Fallunterscheidung aus.

- `name: str` – `"M"` oder `"N"`.
- `gegen_name: str`
- `einheit: Einheit`
- `beschriftung: str`
- `widerstand: str` – Ausgeschrieben, weil die Fugenform sich nicht anhaengen laesst: "Momentenwiderstand", nicht "Momentswiderstand".

#### Achse.von

```python
def von(self, punkt: Punkt) -> float
```

Der Wert dieses Punktes auf dieser Achse.

#### Achse.gegen

```python
@property
def gegen(self) -> 'Achse'
```

Die andere Achse -- die bei einem Schnitt festgehalten wird.

### innerhalb

```python
def innerhalb(N: float, M: float, linie: Sequence[Punkt]) -> bool
```

Punkt-in-Polygon nach dem Strahlverfahren.

### _schnittpunkte

```python
def _schnittpunkte(linie: Sequence[Punkt], achse: Achse, fest: float)
```

Alle Kanten, die die Gerade `achse.gegen = fest` schneiden, und jeder
Eckpunkt, der genau auf ihr liegt.

Liefert Tripel `(Wert auf achse, Punkt a, Punkt b)`; ein Eckpunkt auf
der Geraden kommt als `(Wert, a, a)`. Die einzige Stelle, an der ueber
die Linie gelaufen wird -- alles Weitere waehlt daraus aus.

Die Eckpunkte zaehlen fuer sich, weil die Linie die Gerade auch nur
beruehren kann, ohne sie zu kreuzen: eine Platte nur mit oberer Bewehrung
liegt ganz bei M \<= 0, und ihre Kante vom reinen Druck zu N = 0 liegt auf
M = 0. Bis 2026-10-18 fand die Suche dort nichts, und als Druckwiderstand
bei M_Ed = 0 stand 0 statt -5000 kN.

### schnitte

```python
def schnitte(linie: Sequence[Punkt], achse: Achse, fest: float) -> List[float]
```

Alle Werte auf `achse`, bei denen `achse.gegen = fest` die Linie trifft.

### kante

```python
def kante(linie: Sequence[Punkt], achse: Achse, fest: float, positiv: bool) -> Optional[Tuple[float, Punkt, Punkt]]
```

Der aeusserste Schnittpunkt -- mit den beiden Eckpunkten, zwischen denen er liegt.

Die Eckpunkte braucht die Mitschrift: dort soll stehen, *zwischen welchen
beiden* interpoliert wurde, nicht bloss das Ergebnis. Sonst waere die Zahl
wieder nicht von Hand nachvollziehbar -- und genau darum geht es hier.

### ohne_wiederholungen

```python
def ohne_wiederholungen(linie: Sequence, toleranz: float=1e-07) -> List
```

Entfernt aufeinanderfolgende Punkte, die auf dieselbe Stelle fallen.

Solange saemtliche Bewehrung fliesst und der Beton gerissen ist, aendert
eine Drehung der Dehnungsebene nichts an N und M -- am reinen Zug entstehen
so dutzende deckungsgleiche Punkte, und an der Nahtstelle der beiden Faecher
liegt der Punkt des reinen Drucks doppelt vor. Fuer die Geometrie sind das
entartete Segmente: Punkt-in-Polygon und Schnittsuche stolpern darueber, und
gezeichnet ergeben sie Nullflaechen.

### naechster_punkt

```python
def naechster_punkt(N: float, M: float, linie: Sequence[Punkt], N_ref: float, M_ref: float) -> Tuple[float, Tuple[float, float]]
```

Kuerzester Abstand zur Linie im normierten Diagramm.

Ohne Normierung waere der Abstand von der Wahl der Einheiten abhaengig --
kN und kNm lassen sich nicht sinnvoll gegeneinander aufrechnen.


## Konstanten

- `MOMENT = Achse('M', 'N', KNM, 'Moment', 'Momentenwiderstand')`
- `NORMALKRAFT = Achse('N', 'M', KN, 'Normalkraft', 'Normalkraftwiderstand')`
- `ACHSEN = {'M': MOMENT, 'N': NORMALKRAFT}` – Nachschlagewerk fuer [[opencivil.nachweis.linie#Achse.gegen|Achse.gegen]]. Nach den Konstanten gefuellt, weil eine eingefrorene Datenklasse sich nicht selbst referenzieren kann.

## Braucht

- [[opencivil.core.einheiten]]

## Gebraucht von

- [[opencivil.nachweis.biegung_normalkraft]]
- [[opencivil.nachweis.kennzahlen]]
- [[opencivil.nachweis.resistenzlinie]]
