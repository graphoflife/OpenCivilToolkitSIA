---
erzeugt: 701a706a4db8
art: modul
tags: [modul]
---
> [!abstract] opencivil/fachwerkmodell/optimierung.py
> das leichteste Fachwerk im Gleichgewicht, als lineare Optimierung.
> Paket [[opencivil.fachwerkmodell]] · [Quelltext](../../opencivil/fachwerkmodell/optimierung.py)

## VERANTWORTUNG

Zu gegebenen Stäben die Kräfte, die die Lasten im Gleichgewicht zu den
Lagern tragen und dabei die kleinste Summe aus Kraft mal Länge haben – Zug
mit seinem Gewicht, Druck mit seinem ([[opencivil.fachwerkmodell.optimierung#optimieren|optimieren]]). Gelöst mit einem
primal-dualen Innere-Punkte-Verfahren nach Mehrotra, je Schritt mit dem
Gleichungslöser der Stabwerke ([[opencivil.stabwerk.matrix#Zerlegung|Zerlegung]])
in einem Profil, das die Folge nach Cuthill-McKee schmal hält.


## DIE AUFGABE


```
min  Σ l_i · (w_Z · q⁺_i + w_D · q⁻_i) + M · Σ (r⁺_k + r⁻_k)
mit  B · (q⁺ − q⁻) + r⁺ − r⁻ = f   und allen Unbekannten ≥ 0
```

Je Stab eine Spalte von B: an seinen zwei Knoten die Richtung von einem
zum andern, wo kein Lager hält ([[opencivil.fachwerkmodell.optimierung#Gleichgewicht|Gleichgewicht]]). `q⁺ − q⁻` ist
seine Kraft, Zug positiv. `r⁺ − r⁻` ist der Rest: was sich mit diesen
Stäben nicht ins Gleichgewicht bringen lässt. Er kostet `M` je Einheit,
mehr als jeder Weg durch die Stäbe, und ist null, wo ein Gleichgewicht
geht. Wo keins geht, bleibt er stehen und sagt, wo – statt dass das
Verfahren nicht zu Ende kommt. Zugleich hält er die Gleichungen lösbar, auch
an einem Knoten, an dem kein Stab mehr hängt.


## DIE VIRTUELLEN VERSCHIEBUNGEN

Die dualen Unbekannten `u`, je Zeile eine, sind ein Feld virtueller
Verschiebungen. Ein Stab `i` mit der Dehnung `b_iᵀ · u / l_i` über w_Z
oder unter −w_D machte das Fachwerk leichter: danach sucht die Suche
([[opencivil.fachwerkmodell.suche|suche]]) die Stäbe, die sie zufügt.


## OHNE ZUSATZ AUF DER DIAGONALE

Eine kleine Zahl auf der Diagonale, gegen eine singuläre Matrix, liess das
Verfahren an einer Wand mit 0.25 m Raster nach 80 Schritten mit einem Rest
von 10⁻⁵ stehen (2026-11-27): die Richtung passte nicht mehr genau zu den
Gleichungen. Der Rest `r` macht dasselbe richtig – er gehört zur
Aufgabe, und die Richtung bleibt genau.

## Inhalt

### Optimum

```python
@dataclass(frozen=True)
class Optimum
```

Was die Optimierung fand – in den Einheiten von `f` und der Kosten.

- `q: Tuple[float, ...]` – Je Stab seine Kraft, Zug positiv.
- `u: Tuple[float, ...]` – Je Zeile die virtuelle Verschiebung.
- `rest: Tuple[float, ...]` – Je Zeile, was sich nicht ins Gleichgewicht bringen liess – null, wo es ging.
- `ziel: float` – Σ l · (w_Z · q⁺ + w_D · q⁻), ohne den Rest.
- `schritte: int`
- `geloest: bool` – Ob die [[opencivil.fachwerkmodell.optimierung#Konstanten|GENAUIGKEIT]] erreicht ist.

### Gleichgewicht

```python
class Gleichgewicht
```

Die Gleichgewichtsbedingungen zu gegebenen Stäben: B, je Stab eine
Spalte, in einer Folge der Zeilen, die das Profil der Normalmatrix
schmal hält ([[opencivil.stabwerk.matrix#nummerierung|nummerierung]]).

#### Gleichgewicht.mal

```python
def mal(self, q: Sequence[float]) -> List[float]
```

`B · q`, in der Folge der Normalmatrix.

#### Gleichgewicht.mal_transponiert

```python
def mal_transponiert(self, u: Sequence[float]) -> List[float]
```

`Bᵀ · u`, `u` in der Folge der Normalmatrix.

#### Gleichgewicht.normalmatrix

```python
def normalmatrix(self, d: Sequence[float], d_rest: Sequence[float]) -> Profilmatrix
```

`B · diag(d) · Bᵀ + diag(d_rest)`.

### optimieren

```python
def optimieren(gl: Gleichgewicht, f: Sequence[float], kosten_zug: Sequence[float], kosten_druck: Sequence[float], strafe: float) -> Optimum
```

Die Kräfte der Stäbe mit dem kleinsten Ziel. `f` je Zeile die Last,
`kosten_zug` und `kosten_druck` je Stab `w_Z · l` und `w_D · l`,
`strafe` das `M` des Rests. Am besten ist `f` so bezogen, dass
seine grösste Zahl um 1 liegt.

### _weite

```python
def _weite(v: Sequence[float], dv: Sequence[float]) -> float
```

Wie weit ein Schritt längs `dv` gehen kann, bis eine Zahl von `v` null wird – höchstens 1.


## Konstanten

- `GENAUIGKEIT = 1e-08` – Wie genau gelöst wird: der Rest des Gleichgewichts, der dualen Bedingungen und der Abstand der beiden Zielwerte, je bezogen – nach Vorgabe.
- `HOECHSTENS = 100` – Wie viele Schritte das Verfahren höchstens macht – nach Vorgabe.
- `SCHRITTANTEIL = 0.995` – Welchen Teil des Wegs zum Rand ein Schritt geht – nach Vorgabe.
- `Spalte = Tuple[Tuple[int, float], ...]` – Eine Spalte von B: je Zeile, in der der Stab steht, ihr Wert.

## Braucht

- [[opencivil.stabwerk.matrix]]

## Gebraucht von

- [[opencivil.fachwerkmodell.grundstruktur]]
- [[opencivil.fachwerkmodell.suche]]
