---
erzeugt: 80d7d795fd59
art: modul
tags: [modul]
---
> [!abstract] opencivil/pfahl/bettung.py
> der Pfahl als gebetteter Stab.
> Paket [[opencivil.pfahl]] · [Quelltext](../../opencivil/pfahl/bettung.py)

## VERANTWORTUNG

Löst den Pfahl als Stab auf Federn, längs und quer getrennt:

- längs ein Zug-Druck-Stab mit Federn am Mantel und, wo der Fuss trägt,
  einer am Fuss: die Setzung w(z) und die Normalkraft N(z) ([[opencivil.pfahl.bettung#laengs|laengs]]);
- quer ein Biegebalken auf einer Bettung: die Verschiebung y(z), die
  Verdrehung, das Moment M(z), die Querkraft V(z) und die Bettungskraft
  ([[opencivil.pfahl.bettung#quer|quer]]).

Die Federn je Meter Pfahl kommen als [[opencivil.pfahl.bettung#Strecke|Strecke]] von aussen; was sie
bedeuten, sagt [[opencivil.pfahl.steifigkeit|.steifigkeit]]. Hier wird nur gerechnet.


## DAS VERFAHREN

Finite Elemente mit Knoten an jeder Grenze einer Strecke, dazwischen gleich
lang und höchstens `schritt`: die Stäbe des Stabwerks, längs mit linearem,
quer mit kubischem Ansatz und konsistent verteilter Bettung
([[opencivil.stabwerk.stab#steifigkeit|opencivil.stabwerk.stab.steifigkeit]], [[opencivil.stabwerk.stab#bettung|bettung]]).
Quer darf die Bettung über eine Strecke linear wachsen -- so steht die
Abminderung am Terrain genau im Modell, ohne Stufen. Gelöst wird mit dem
Profillöser des Stabwerks ([[opencivil.stabwerk.matrix]]). N, M
und V folgen danach aus dem Gleichgewicht der Bettungskräfte, Element für
Element und für den Ansatz genau integriert -- nicht aus der Krümmung eines
Elements, die eine Ordnung ungenauer wäre. Am eingespannten Kopf ist das
Moment die Reaktion, die das Gleichgewicht am freien Fuss schliesst.


## VORZEICHEN

z zählt vom Pfahlkopf nach unten. Längs: w positiv nach unten, N positiv als
Druck. Quer: y in Richtung der Kopfkraft H; das Kopfmoment M_0 dreht wie eine
Kraft H, die über dem Kopf angreift (M_0 = H·e), und die Verdrehung θ wie
diese Kraft -- so verrichten H an y und M_0 an θ Arbeit. Es gilt V = dM/dz,
am Kopf V = H und M = M_0.


## EINHEITEN

SI-Basis.

## Inhalt

### Strecke

```python
@dataclass(frozen=True)
class Strecke
```

Ein Stück des Pfahls von `oben` bis `unten` (m unter dem Kopf).
`laengs` ist die Feder am Mantel je Meter Pfahl (Schubspannung mal
Umfang je Setzung), gleich über das Stück; `quer` die Bettung je Meter
Pfahl (k_s · D) oben und unten, dazwischen linear -- alle in N/m².

- `oben: float`
- `unten: float`
- `laengs: float`
- `quer: Tuple[float, float]`

#### Strecke.quer_bei

```python
def quer_bei(self, z: float) -> float
```

Die Bettung quer in der Tiefe `z` des Stücks.

### Laengs

```python
@dataclass(frozen=True)
class Laengs
```

Setzung und Normalkraft je Knoten, dazu die Kraft der Feder am Fuss.

- `z: List[float]`
- `w: List[float]`
- `N: List[float]`
- `fusskraft: float`

### Quer

```python
@dataclass(frozen=True)
class Quer
```

Verschiebung, Verdrehung, Moment, Querkraft und Bettungskraft je Knoten.

- `z: List[float]`
- `y: List[float]`
- `theta: List[float]`
- `M: List[float]`
- `V: List[float]`
- `q: List[float]` – Bettungskraft je Meter Pfahl, N/m: die Bettung mal y -- an der Grenze zweier Strecken mit der unteren.

### knoten

```python
def knoten(strecken: Sequence[Strecke], schritt: float=SCHRITT) -> List[float]
```

Die Knoten: jede Grenze einer Strecke, dazwischen gleich weit, höchstens `schritt`.

### laengs

```python
def laengs(strecken: Sequence[Strecke], EA: float, fussfeder: float, N_kopf: float, schritt: float=SCHRITT) -> Laengs
```

Der Stab längs unter der Kopfkraft `N_kopf` (Druck positiv), mit der
Feder `fussfeder` (N/m) am Fuss -- null, wo der Fuss nicht trägt.

### quer

```python
def quer(strecken: Sequence[Strecke], EI: float, H: float, M_0: float, *, eingespannt: bool, schritt: float=SCHRITT) -> Quer
```

Der Balken quer unter H und M_0 am Kopf, der Fuss frei. `eingespannt`:
der Kopf dreht sich nicht, M_0 zählt dann nicht -- das Moment am Kopf ist
die Reaktion.

### _element

```python
def _element(l: float, stellen: Sequence[int], *, EA: float=0.0, EI: float=0.0, laengs: float=0.0, quer: Tuple[float, float]=(0.0, 0.0)) -> List[List[float]]
```

Ein Element der Länge `l`: Steifigkeit und Bettung des Stabwerks, auf `stellen`.

### _schnittkraefte

```python
def _schnittkraefte(z: Sequence[float], k: Sequence[Tuple[float, float]], y: Sequence[float], phi: Sequence[float], H: float, M_0: float) -> Tuple[List[float], List[float]]
```

V und M von oben nach unten aus dem Gleichgewicht: je Element die
Bettungskraft und ihr Moment um das untere Ende, für den kubischen Ansatz
genau integriert.


## Konstanten

- `SCHRITT = 0.1` – So lang ist ein Element höchstens, in m.

## Braucht

- [[opencivil.stabwerk.matrix]]
- [[opencivil.stabwerk.stab]]

## Gebraucht von

- [[opencivil.pfahl.steifigkeit]]
