---
erzeugt: 9518a32d68d1
art: modul
tags: [modul]
---
> [!abstract] opencivil/stabwerk/stab.py
> der ebene Stab: Steifigkeit, Lasten, Bettung.
> Paket [[opencivil.stabwerk]] · [Quelltext](../../opencivil/stabwerk/stab.py)

## VERANTWORTUNG

Was ein einzelner Stab zum System beitraegt, in seinen eigenen Achsen: die
Steifigkeitsmatrix, die Lasten als arbeitsgleiche Knotenkraefte, die
Bettung, und die Drehung in die Achsen des Systems. Zusammengebaut wird in
[[opencivil.stabwerk.system|system]].


## DIE ACHSEN DES STABS

`x` laeuft vom Anfang zum Ende, `y` steht links davon -- `x` um 90° im
Gegenuhrzeigersinn gedreht --, Drehungen zaehlen im Gegenuhrzeigersinn. In
diesen Achsen ist die Steifigkeitsmatrix die des Lehrbuchs. Die gestrichelte
Faser liegt auf der anderen Seite, bei `-y`: dorthin zeigt `z` der
Baustatik, und dort zieht ein positives Moment
([[opencivil.stabwerk.verlauf|verlauf]]).

Je Ende drei Unbekannte, in dieser Folge:

```
u   laengs, in x
v   quer, in y
θ   Drehung, im Gegenuhrzeigersinn
```

Euler-Bernoulli: eben bleibende Querschnitte, ohne Schubverformung. Laengs
ist der Stab linear, quer kubisch (Hermite) -- fuer einen Stab ohne Bettung
ist das die genaue Loesung, und die Knotenverschiebungen stimmen exakt.


## ARBEITSGLEICHE LASTEN

Eine Last zwischen den Knoten geht als die Knotenkraefte ins System, die an
denselben Verschiebungen dieselbe Arbeit leisten: `f_i = ∫ N_i · p dx`.
Fuer diesen Stab sind das genau die Volleinspannkraefte mit umgekehrtem
Vorzeichen. Integriert wird nach Gauss-Legendre mit drei Punkten -- exakt
bis Grad fuenf, und eine lineare Last mal eine kubische Formfunktion hat
Grad vier. Ein verteiltes Moment `m` leistet Arbeit an der Drehung
`θ = v'`: `f_i = ∫ N_i' · m dx`.


## BETTUNG

Ein Stab auf einem nachgiebigen Linienlager (Winkler) bekommt zu seiner
Steifigkeit `k · ∫ Nᵀ N dx` -- die konsistente Bettungsmatrix. Mit
kubischen Formfunktionen ist das eine Naeherung; das System teilt einen
gebetteten Stab darum in kurze Stuecke ([[opencivil.stabwerk.system|system]]).

## Inhalt

### nullmatrix

```python
def nullmatrix(n: int, m: int=None) -> Matrix
```

### steifigkeit

```python
def steifigkeit(L: float, EA: float, EI: float) -> Matrix
```

Die Steifigkeitsmatrix 6 × 6 in den Achsen des Stabs.

### bettung

```python
def bettung(L: float, k_quer: float=0.0, k_laengs: float=0.0) -> Matrix
```

Die konsistente Bettungsmatrix 6 × 6: `k · ∫ Nᵀ N dx`, quer auf
`v` und `θ`, laengs auf `u`. `k` in N/m je m Stab, also N/m².

### summe

```python
def summe(*matrizen: Matrix) -> Matrix
```

### drehung

```python
def drehung(c: float, s: float) -> Matrix
```

`T` mit `d = T · d_glob`: je Ende `u = c·U + s·W`, `v = -s·U + c·W`, `θ = Θ`.

### mal

```python
def mal(A: Matrix, x: Sequence[float]) -> List[float]
```

### transponiert_mal

```python
def transponiert_mal(A: Matrix, x: Sequence[float]) -> List[float]
```

`Aᵀ · x`.

### formfunktionen

```python
def formfunktionen(x: float, L: float) -> Tuple[float, ...]
```

`(N1, N2, H1, H2, H3, H4)` an der Stelle `x`: laengs linear, quer
nach Hermite -- je eine Funktion zu `u1, u2` und `v1, θ1, v2, θ2`.

### ableitungen

```python
def ableitungen(x: float, L: float) -> Tuple[float, float, float, float]
```

`(H1', H2', H3', H4')` nach `x` -- die Drehung `θ = v'` je Einheitsverschiebung.

### Strecke

```python
@dataclass(frozen=True)
class Strecke
```

Eine Last auf `[a, b]`, linear von `a` nach `b`: Kraft je Laenge
laengs (`px`) und quer (`py`) und ein Moment je Laenge (`m`, im
Gegenuhrzeigersinn). In N/m und Nm/m; `a` und `b` in m ab dem
Anfang des Stabs (oder Teilstabs).

- `a: float`
- `b: float`
- `px_a: float = 0.0`
- `px_b: float = 0.0`
- `py_a: float = 0.0`
- `py_b: float = 0.0`
- `m_a: float = 0.0`
- `m_b: float = 0.0`

#### Strecke.bei

```python
def bei(self, x: float) -> Tuple[float, float, float]
```

`(px, py, m)` an der Stelle `x` innerhalb von `[a, b]`.

#### Strecke.ausschnitt

```python
def ausschnitt(self, von: float, bis: float) -> 'Strecke'
```

Der Teil auf `[von, bis]`, in den Achsen ab `von`.

### Punkt

```python
@dataclass(frozen=True)
class Punkt
```

Eine Last an der Stelle `a`: Kraefte `Px`, `Py` in N, Moment `M` in Nm.

- `a: float`
- `Px: float = 0.0`
- `Py: float = 0.0`
- `M: float = 0.0`

### aufteilen

```python
def aufteilen(lasten: Sequence[Teillast], von: float, bis: float, *, ende: bool) -> List[Teillast]
```

Die Lasten eines Stabs, die auf `[von, bis]` liegen -- in den Achsen
dieses Stuecks. Eine Einzellast genau auf der Grenze zweier Stuecke
gehoert dem ersten, dessen Ende sie ist; nur am letzten (`ende`)
zaehlt auch das Ende des Stabs.

### knotenlasten

```python
def knotenlasten(L: float, lasten: Sequence[Teillast]) -> List[float]
```

Die arbeitsgleichen Knotenkraefte `f` (6) in den Achsen des Stabs --
`f_i = ∫ N_i·p + N_i'·m` und die Einzellasten an ihren Stellen.


## Konstanten

- `GAUSS3 = ((-math.sqrt(0.6), 5.0 / 9.0), (0.0, 8.0 / 9.0), (math.sqrt(0.6), 5.0…` – Gauss-Legendre mit drei Punkten auf [-1, 1]: Stelle und Gewicht.
- `STEIFIGKEIT_LATEX = '\\mathbf{k} = \\begin{bmatrix} \\frac{EA}{L} & 0 & 0 & -\\frac{EA}{L…` – Die Steifigkeitsmatrix in Zeichen -- fuer die Herleitung.
- `DREHUNG_LATEX = '\\mathbf{d} = \\mathbf{T} \\cdot \\mathbf{d}_{glob} \\qquad \\mathbf…` – Die Drehung von den Achsen des Systems in die des Stabs.
- `BETTUNG_LATEX = '\\mathbf{k}_{b} = \\frac{k_{\\perp} \\cdot L}{420} \\begin{bmatrix} …` – Die Bettung in Zeichen -- quer und laengs.
- `LASTEN_LATEX = "f_i = \\int_0^L N_i(x) \\cdot p(x)\\,\\mathrm{d}x + \\int_0^L N_i'(x…` – Die arbeitsgleichen Knotenkraefte in Zeichen.

## Gebraucht von

- [[opencivil.stabwerk.system]]
- [[opencivil.stabwerk.verlauf]]
