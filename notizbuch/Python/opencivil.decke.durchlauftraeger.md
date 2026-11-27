---
erzeugt: 2e94ce788a22
art: modul
tags: [modul]
---
> [!abstract] opencivil/decke/durchlauftraeger.py
> ein Streifen als Durchlaufträger.
> Paket [[opencivil.decke]] · [Quelltext](../../opencivil/decke/durchlauftraeger.py)

## VERANTWORTUNG

Ein Streifen der Decke ist ein Balken über seine Lager. Hier wird er
gerechnet, in zwei Schritten:

1. **Elastisch**, mit den Lagern als Punkten: die Lagerkräfte eines statisch
   unbestimmten Streifens folgen aus der Biegelinie – mit den Elementen des
   Stabwerks ([[opencivil.stabwerk.stab]]), Knoten an den Lagern und wo
   die Steifigkeit wechselt. Zwischen den Knoten ist die Hermite-Biegelinie
   die genaue Lösung; die Lagerkräfte stimmen exakt. Über das erste und das
   letzte Lager hinaus ragt der Streifen frei: dort ist er statisch
   bestimmt, und seine Last geht als Kraft und Moment an das Lager.
2. **Statik**: mit diesen Lagerkräften laufen Querkraft und Moment vom
   Anfang des Streifens bis zu seinem Ende, gerechnet wie in einem ebenen
   Stab des Stabwerks, starr ([[opencivil.decke.durchlauftraeger#statik|statik]]). Ein Flächenlager – ein
   Träger, eine Stütze – drückt dabei nicht in einem Punkt,
   sondern gleichmässig über seine Breite; so steht es in der Vorlesung
   («Flächenlager mit gleichmässiger Pressung», Stahlbeton II, 7.2 Platten,
   Folie 33), und so rechnet die Musterlösung des Kolloquiums 4 ihr
   Stützmoment von −10.9 auf −7.3 kNm/m herunter.


## VORZEICHEN

`s` läuft vom Anfang des Durchlaufträgers, in m. Lasten wirken nach unten und
sind dann positiv, Lagerkräfte nach oben, Lagermomente im
Gegenuhrzeigersinn. `M > 0` zieht unten (Feldmoment), `V = dM/ds`:

```python
M(s) = Σ_links [F_k · (s − s_k) − C_k] − ∫_links p(σ) · (s − σ) dσ
```

Am Ende eines Durchlaufträgers sind V und M null – eine Probe, die
[[opencivil.decke.durchlauftraeger#statik|statik]] macht.

## Inhalt

### Streckenlast

```python
@dataclass(frozen=True)
class Streckenlast
```

Eine Last je Länge, linear von `a` nach `b`, in N/m – nach unten positiv.

- `a: float`
- `b: float`
- `p_a: float`
- `p_b: float`

#### Streckenlast.bei

```python
def bei(self, s: float) -> float
```

#### Streckenlast.summe

```python
@property
def summe(self) -> float
```

#### Streckenlast.mal

```python
def mal(self, faktor: float) -> 'Streckenlast'
```

#### Streckenlast.verschoben

```python
def verschoben(self, um: float) -> 'Streckenlast'
```

### Einzellast

```python
@dataclass(frozen=True)
class Einzellast
```

Eine Kraft in N an der Stelle `a` (nach unten positiv) und ein Moment `C` in Nm (Gegenuhrzeigersinn).

- `a: float`
- `P: float = 0.0`
- `C: float = 0.0`

#### Einzellast.mal

```python
def mal(self, faktor: float) -> 'Einzellast'
```

#### Einzellast.verschoben

```python
def verschoben(self, um: float) -> 'Einzellast'
```

### Halt

```python
@dataclass(frozen=True)
class Halt
```

Ein Lager am Durchlaufträger, als Punkt: `vertikal` hält die Höhe, `eingespannt` die Drehung.

- `s: float`
- `vertikal: bool`
- `eingespannt: bool`

### stabil

```python
def stabil(halte: Sequence[Halt]) -> bool
```

Ob die Lager den Durchlaufträger halten: zwei Höhenlager an verschiedenen
Stellen – oder eines und eine Einspannung.

### Balken

```python
class Balken
```

Der elastische Durchlaufträger: Knoten, Elemente, die zerlegte
Steifigkeitsmatrix – einmal gebaut, für jeden Fall nur noch gelöst.

#### Balken.knoten_bei

```python
def knoten_bei(self, s: float) -> int
```

#### Balken._steifigkeit

```python
def _steifigkeit(self, i: int, EI: float) -> List[List[float]]
```

Der Biegeteil der Stabsteifigkeit: `v1, θ1, v2, θ2`.

#### Balken.lagerkraefte

```python
def lagerkraefte(self, lasten: Sequence[Teillast]) -> List[Tuple[float, float]]
```

Je Lager die Kraft nach oben `F` und das Moment `C` im
Gegenuhrzeigersinn, die es auf den Durchlaufträger ausübt – elastisch, mit
den Lagern als Punkten.

### _resultante

```python
def _resultante(lasten: Sequence[st.Teillast], x0: float) -> Tuple[float, float]
```

Kraft quer und Moment um `x0` – im Gegenuhrzeigersinn, in den Achsen
eines ebenen Stabs – der Lasten eines freien Endes.

### statik

```python
def statik(L: float, lasten: Sequence[Teillast]) -> List[EbenesIntervall]
```

Querkraft und Moment längs des Durchlaufträgers, von links: aus allen Kräften auf
ihn – Lasten nach unten, Lagerkräfte als Einzellasten oder Pressungen
nach oben (negativ). Gerechnet wie ein ebener Stab des Stabwerks, starr
([[opencivil.stabwerk.verlauf#ebener_verlauf|ebener_verlauf]] mit `EI = ∞`): die
Biegelinie braucht hier niemand. Bis 2026-11-20 integrierte die Decke
Querkraft und Moment ein zweites Mal selbst.

Was näher als [[opencivil.decke.durchlauftraeger#Konstanten|GLEICH]] beieinanderliegt, gilt als eine Stelle –
der Rand eines Lagers und die Grenze eines Streifens unterscheiden sich
oft nur in der Rundung. Wirft, wenn am Ende etwas übrig bleibt: dann
stehen die Kräfte nicht im Gleichgewicht.

### wert

```python
def wert(teile: Sequence[EbenesIntervall], groesse: str, s: float, links: bool=False) -> float
```

`V` oder `M` an der Stelle `s` – an einem Sprung rechts davon, mit `links` links davon.


## Konstanten

- `GLEICH = 1e-09` – Was in m als dieselbe Stelle gilt.
- `WECHSEL = 0.01` – Ein Wechsel der Steifigkeit näher als so viel an einem anderen Knoten gilt dort, in m. Als eigenes Element zwischen freien Knoten wäre ein so kurzes Stück fast starr: sein Pivot fiele unter die Schranke der Zerlegung ([[opencivil.stabwerk.matrix#Konstanten|SCHRANKE]]), und sie hielte den Knoten still fest wie ein Lager, das es nicht gibt – bei 1 mm zwischen zwei Wechseln schon. So schmal wirkt ein Wechsel auf die Lagerkräfte kaum; die 1 cm sind nach Vorgabe, nicht nachgeschlagen.

## Braucht

- [[opencivil.stabwerk.matrix]]
- [[opencivil.stabwerk.stab]]
- [[opencivil.stabwerk.verlauf]]

## Gebraucht von

- [[opencivil.decke.feld]]
- [[opencivil.decke.lasten]]
- [[opencivil.decke.rechnung]]
- [[opencivil.decke.streifen]]
