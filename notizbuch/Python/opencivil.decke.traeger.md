---
erzeugt: 47499118433d
art: modul
tags: [modul]
---
> [!abstract] opencivil/decke/traeger.py
> ein Streifen als Durchlaufträger.
> Paket [[opencivil.decke]] · [Quelltext](../../opencivil/decke/traeger.py)

## VERANTWORTUNG

Ein Streifen der Decke ist ein Balken über seine Lager. Hier wird er
gerechnet, in zwei Schritten:

1. **Elastisch**, mit den Lagern als Punkten: die Lagerkräfte eines statisch
   unbestimmten Streifens folgen aus der Biegelinie -- mit den Elementen des
   Stabwerks ([[opencivil.stabwerk.stab]]), Knoten an den Enden, den
   Lagern und wo die Steifigkeit wechselt. Zwischen den Knoten ist die
   Hermite-Biegelinie die genaue Lösung; die Lagerkräfte stimmen exakt.
2. **Statik**: mit diesen Lagerkräften laufen Querkraft und Moment vom
   Anfang des Streifens bis zu seinem Ende. Ein Flächenlager -- ein
   versteckter Unterzug, eine Stütze -- drückt dabei nicht in einem Punkt,
   sondern gleichmässig über seine Breite; so steht es in der Vorlesung
   («Flächenlager mit gleichmässiger Pressung», Stahlbeton II, 7.2 Platten,
   Folie 33), und so rechnet die Musterlösung des Kolloquiums 4 ihr
   Stützmoment von −10.9 auf −7.3 kNm/m herunter.


## VORZEICHEN

`s` läuft vom Anfang des Trägers, in m. Lasten wirken nach unten und
sind dann positiv, Lagerkräfte nach oben, Lagermomente im
Gegenuhrzeigersinn. `M > 0` zieht unten (Feldmoment), `V = dM/ds`:

```python
M(s) = Σ_links [F_k · (s − s_k) − C_k] − ∫_links p(σ) · (s − σ) dσ
```

Am Ende eines Trägers sind V und M null -- eine Probe, die
[[opencivil.decke.traeger#statik|statik]] macht.

## Inhalt

### Streckenlast

```python
@dataclass(frozen=True)
class Streckenlast
```

Eine Last je Länge, linear von `a` nach `b`, in N/m -- nach unten positiv.

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

Ein Lager am Träger, als Punkt: `vertikal` hält die Höhe, `eingespannt` die Drehung.

- `s: float`
- `vertikal: bool`
- `eingespannt: bool`

### stabil

```python
def stabil(halte: Sequence[Halt]) -> bool
```

Ob die Lager den Träger halten: zwei Höhenlager an verschiedenen
Stellen -- oder eines und eine Einspannung.

### Balken

```python
class Balken
```

Der elastische Durchlaufträger: Knoten, Elemente, die zerlegte
Steifigkeitsmatrix -- einmal gebaut, für jeden Fall nur noch gelöst.

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
Gegenuhrzeigersinn, die es auf den Träger ausübt -- elastisch, mit
den Lagern als Punkten.

### Stueck

```python
@dataclass(frozen=True)
class Stueck
```

Ein Stück des Trägers ohne Laststelle: Querkraft, Moment und Last als Polynome in `s`.

- `a: float`
- `b: float`
- `V: Polynom`
- `M: Polynom`
- `p: Polynom` – Die Last nach unten, samt Pressung der Flächenlager (negativ).

### statik

```python
def statik(L: float, lasten: Sequence[Teillast]) -> List[Stueck]
```

Querkraft und Moment längs des Trägers, von links: aus allen Kräften
auf ihn -- Lasten nach unten, Lagerkräfte als Einzellasten oder
Pressungen nach oben (negativ). Wirft, wenn am Ende etwas übrig bleibt:
dann stehen die Kräfte nicht im Gleichgewicht.

### wert

```python
def wert(stuecke: Sequence[Stueck], groesse: str, s: float, links: bool=False) -> float
```

`V` oder `M` an der Stelle `s` -- an einem Sprung rechts davon, mit `links` links davon.

### extreme

```python
def extreme(stuecke: Sequence[Stueck], groesse: str) -> Tuple[Tuple[float, float], Tuple[float, float]]
```

`((s, kleinster), (s, grösster))` von `V` oder `M` -- an Grenzen und wo die Ableitung null ist.


## Konstanten

- `GLEICH = 1e-09` – Was in m als dieselbe Stelle gilt.

## Braucht

- [[opencivil.stabwerk.matrix]]
- [[opencivil.stabwerk.stab]]
- [[opencivil.stabwerk.verlauf]]

## Gebraucht von

- [[opencivil.decke.feld]]
- [[opencivil.decke.lasten]]
- [[opencivil.decke.rechnung]]
- [[opencivil.decke.streifen]]
