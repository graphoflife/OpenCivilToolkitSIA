---
erzeugt: db42614b5840
art: modul
tags: [modul]
---
> [!abstract] opencivil/decke/fem/system.py
> das Gleichungssystem der Platte.
> Paket [[opencivil.decke.fem]] · [Quelltext](../../opencivil/decke/fem/system.py)

## VERANTWORTUNG

Aus der Decke und ihrem Netz: was die Lager halten, die Nummern der
Unbekannten, die Steifigkeit aus den Dreiecken und den Trägern, einmal
zerlegt für alle Fälle ([[opencivil.stabwerk.matrix|matrix]]) – und welche
Teile der Decke sich frei bewegen könnten.


## LAGER

Ein Linienlager, das vertikal hält, hält auf jedem seiner Knoten `w` –
und damit auch die Neigung längs: `w` ist auf ihm überall null. Hält es
die Drehung, ist auch die Neigung quer zu ihm null; nur die Drehung allein
hält ein Rand an einer Symmetrieachse. Eine Stütze hält `w` ihres
Knotens, nicht seine Neigung: sie ist ein Punkt (Plan vom 2026-11-27).
Hält ein Knoten eine Neigung schief zu x und y, rechnet er in eigenen
Achsen, die erste längs dieser Richtung ([[opencivil.decke.fem.system#System|System.achsen]]); hält er
zwei, ist er ganz eingespannt.


## DIE NUMMERN

Die Knoten in der umgekehrten Cuthill-McKee-Folge
([[opencivil.stabwerk.matrix#nummerierung|nummerierung]]), je Knoten `w` und
die beiden Neigungen; was ein Lager hält, hat keine Nummer.


## BEWEGLICH

Hält ein Teil der Decke – Dreiecke, die über Knoten oder Träger
zusammenhängen – nicht genug, um nicht wegzukippen, fällt beim Zerlegen
ein Pivot weg. Der ganze Teil trägt dann nichts ([[opencivil.decke.fem.system#System|System.beweglich]]),
und der Rest rechnet weiter.

## Inhalt

### Halt

```python
@dataclass
class Halt
```

Was die Lager an einem Knoten halten: `w` und die Richtungen, in denen die Neigung null ist.

- `w: bool = False`
- `richtungen: List[Punkt] = field(default_factory=list)`

#### Halt.neigung

```python
def neigung(self, d: Punkt) -> None
```

### Balkenstueck

```python
@dataclass(frozen=True)
class Balkenstueck
```

Ein Stück eines Trägers zwischen zwei Knoten: von `u_p` bis `u_q` m ab seinem Anfang.

- `traeger: str`
- `p: int`
- `q: int`
- `u_p: float`
- `u_q: float`
- `K4: Matrix` – Die Steifigkeit über `(w_p, w'_p, w_q, w'_q)`, `w'` längs des Trägers.
- `richtung: Punkt`
- `EI: float`

### System

```python
class System
```

Die Platte als Gleichungssystem, zerlegt.

#### System.unbekannte

```python
def unbekannte(self, knoten: Sequence[int]) -> List[int]
```

Die Nummern der Unbekannten dieser Knoten, je drei – -1, wo ein Lager hält.

#### System.gedreht

```python
def gedreht(self, K: Matrix, knoten: Sequence[int]) -> Matrix
```

`K` über `(w, β_x, β_y)` der `knoten` – in den Achsen jedes Knotens ([[opencivil.decke.fem.system#System|achsen]]).

#### System.elemente

```python
def elemente(self) -> List[Tuple[Sequence[int], Matrix]]
```

Jedes Dreieck und jedes Balkenstück: seine Knoten und seine Steifigkeit über `(w, β_x, β_y)` je Knoten.

#### System._beweglich

```python
def _beweglich(self) -> List[Set[int]]
```

Die zusammenhängenden Teile, in denen ein Pivot wegfiel.

#### System.loesen

```python
def loesen(self, kraefte: Sequence[float]) -> List[Tuple[float, float, float]]
```

Je Knoten `(w, β_x, β_y)` in x und y, aus den Kräften nach unten in
N je Knoten – in einem beweglichen Teil null.

#### System.reste

```python
def reste(self, u: Sequence[Tuple[float, float, float]], kraefte: Sequence[float]) -> List[List[float]]
```

Je Knoten `K·u − f` in x und y: was die Lager auf die Platte
ausüben, nach unten positiv und als Moment zur Neigung – an einem
freien Knoten null bis auf Rundung.

### _halt

```python
def _halt(decke: Decke, netz: Netz) -> List[Halt]
```

Je Knoten, was die Linienlager und Stützen an ihm halten.

### _achsen

```python
def _achsen(h: Halt) -> Optional[Tuple[Punkt, Punkt]]
```

Die Achsen eines Knotens, der genau eine Neigung hält, schief zu x und y – sonst `None`.

### _balken

```python
def _balken(decke: Decke, netz: Netz) -> List[Balkenstueck]
```

Je Träger mit Höhe seine Stücke von Knoten zu Knoten
([[opencivil.decke.fem.element#steifigkeit_des_traegers|steifigkeit_des_traegers]]), mit E
und h der Platte neben dem Stück – auf der Fuge zweier Platten der
ersten. Ohne Höhe ist er kein Balken: er steckt in der Platte.


## Konstanten

- `PARALLEL = 1e-06` – Zwei Richtungen gelten als eine, wenn der Sinus ihres Winkels kleiner ist.

## Braucht

- [[opencivil.decke.fem.element]]
- [[opencivil.decke.fem.netz]]
- [[opencivil.decke.geometrie]]
- [[opencivil.decke.modell]]
- [[opencivil.stabwerk.matrix]]

## Gebraucht von

- [[opencivil.decke.fem.rechnung]]
