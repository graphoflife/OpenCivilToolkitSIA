---
erzeugt: caf3a696abcd
art: modul
tags: [modul]
---
> [!abstract] opencivil/querschnitt/schubwaende.py
> Querkraft und Torsion auf Schubwaende verteilt.
> Paket [[opencivil.querschnitt]] · [Quelltext](../../opencivil/querschnitt/schubwaende.py)

## VERANTWORTUNG

Eine Schubwand ist eine Linie im Querschnitt mit einer Dicke `b_w` und
Buegeln. Sie traegt eine Kraft entlang ihrer Achse; ihre Laenge ist der
Hebelarm `z` des Fachwerks. Hier wird `(V_y, V_z, T)` auf die Waende
verteilt, der Widerstand jeder Wand bestimmt und -- auf Wunsch -- die
Laengszugkraft, die das Druckfeld der Waende im Querschnitt weckt.


## DIE VERTEILUNG, ELASTISCH

Jede Wand wirkt wie eine Feder entlang ihrer Achse, ihre Steifigkeit ist
`k = b_w · l`: dicker und laenger heisst steifer. `G` kuerzt sich, solange
alle Waende aus demselben Beton sind.

1. **Querkraft.** Der Querschnitt verschiebt sich um `u`, jede Wand wehrt
   sich mit `V_i = k_i · (e_i · u)`. Aus `Σ V_i · e_i = (V_y, V_z)` folgt
   `u` -- zwei Gleichungen, `K = Σ k_i · e_i · e_iᵀ`. Zwei gleiche Stege
   eines Kastens tragen so je die Haelfte.
2. **Versatz.** Die Wandkraefte aus 1 haben ein Moment `ΔT` um den
   Schwerpunkt -- die Querkraft greift im Schwerpunkt an, ihre Wirkungslinie
   in den Waenden liegt anderswo. Den Rest `T - ΔT` tragen die Zellen.
3. **Zellen nach Bredt.** Wo Waende eine geschlossene Flaeche umranden, laeuft
   ein Schubfluss rundum. Je Zelle ein unbekannter Fluss `q_k`, dazu die
   Verdrillung `θ` (mit `G` multipliziert):

```
    T - ΔT = Σ 2 · A_k · q_k                     Gleichgewicht
    ∮_k q_netto · ds / b_w = 2 · A_k · θ          je Zelle: alle drehen gleich

In einer Wand zwischen zwei Zellen fliesst die Differenz der beiden.
Zwei gleiche Kaesten mit gemeinsamer Mittelwand: dort fliesst nichts, und
aussen ``T / (2 · A_gesamt)``. Ein einzelner Kasten: ``T / (2 · A_k)``.
```
4. **Ohne Zelle** traegt die Torsion ueber dieselben Federn, nun mit Drehung:
   `V_i = k_i · (e_i · u + r_i · θ)` mit dem Hebelarm `r_i` der Wand um den
   Schwerpunkt, aus `(V_y, V_z, T)` drei Gleichungen. Querkraft und
   Torsion laufen dann gemeinsam durch dieses System.

In jedem Fall gilt: die Wandkraefte ergeben `V_y` und `V_z`, und ihr
Moment um den Schwerpunkt ist `T`.


## WIDERSTAND

Je Wand das Fachwerk aus [[opencivil.querschnitt.fachwerk#fachwerk|opencivil.querschnitt.fachwerk.fachwerk]], je
Laenge der Wand -- SIA 262:2025, Gl. (45) und (47), durch den Hebelarm geteilt:

```
v_Rd,s = A_sw/s · f_yd · cot α          v_Rd,c = b_w · k_c · f_cd · sin α · cos α
```

α ganzgradig zwischen den Grenzen, massgebend das groesste `min`. Eine Wand,
die zwischen zwei Zellen in Stuecke zerfaellt, traegt je Stueck einen anderen
Fluss; nachgewiesen wird das staerkste Stueck.


## VORZEICHEN

y nach rechts, z nach oben; `V_y`, `V_z` in Achsrichtung; `T` im
Gegenuhrzeigersinn. Der Fluss einer Wand zaehlt in ihrer Richtung, vom
Anfangs- zum Endpunkt. Einheiten in SI-Basis.


## WAS DIE NORM SAGT

- Eine einzelne Zelle traegt die Torsion mit dem Schubfluss `T / (2 · A_k)`
  rundum (SIA 262:2025, 4.3.5.2, Gl. (55)). `A_k` ist die Flaeche, die die
  Laengsbewehrung umschliesst (Figur 20): die Wandachsen gehoeren darum durch
  die Eckstaebe. Querkraft und Torsion zusammen: 4.3.5.5.
- Die Laengszugkraft `|q| · l · cot α` je Stueck, halb in jedem Gurt, ihre
  Resultierende also in der Wandmitte: 4.3.3.4.11, Gl. (51), mit lotrechten
  Buegeln; fuer die Torsion 4.3.5.4.
- Das Federmodell, die Verteilung auf mehrere Zellen mit gleicher
  Verdrillung und die Torsion ohne Zelle ueber Federn mit Drehung sind nach
  Vorgabe eingebaut, in SIA 262:2025 nicht gefunden
  (`notizbuch/Notizen/TODO.md`). Die Norm legt auch einem Vollquerschnitt
  einen Hohlquerschnitt zugrunde (4.3.5.1) -- wer ihn rechnet, zeichnet ihn
  als Zelle.

## Inhalt

### WandFehler

```python
class WandFehler(ValueError)
```

Eine Last, die die Waende nicht aufnehmen koennen -- mit dem Grund.

### Wand

```python
@dataclass(frozen=True)
class Wand
```

Eine Schubwand: Achse, Dicke, Buegel und die Festigkeiten dazu.

- `name: str`
- `von: Punkt`
- `bis: Punkt`
- `b_w: float` – Dicke in m.
- `a_sw_s: float` – Buegelquerschnitt je Laenge in Laengsrichtung, `n · π⌀²/4 / s`, in m²/m.
- `f_yd: float` – Fliessgrenze der Buegel in Pa, im Wertesatz der Rechenwahl.
- `f_cd: float` – Druckfestigkeit des Betons der Wand in Pa.
- `k_c: float`

#### Wand.laenge

```python
@property
def laenge(self) -> float
```

#### Wand.richtung

```python
@property
def richtung(self) -> Punkt
```

#### Wand.mitte

```python
@property
def mitte(self) -> Punkt
```

#### Wand.steifigkeit

```python
@property
def steifigkeit(self) -> float
```

### Stueck

```python
@dataclass(frozen=True)
class Stueck
```

Ein Stueck einer Wand zwischen zwei Knoten des Graphen.

- `wand: int`
- `von: Punkt`
- `bis: Punkt`

#### Stueck.laenge

```python
@property
def laenge(self) -> float
```

#### Stueck.mitte

```python
@property
def mitte(self) -> Punkt
```

### Zelle

```python
@dataclass(frozen=True)
class Zelle
```

Eine geschlossene Flaeche, umrandet von Wandstuecken.

- `flaeche: float` – `A_k`, umschlossen von den Wandachsen -- die Norm meint die Laengsbewehrung.
- `rand: Tuple[Tuple[int, int], ...]` – Je Randstueck: (Index, +1 wenn die Zelle es in seiner Richtung umlaeuft).

### Zellenmodell

```python
@dataclass(frozen=True)
class Zellenmodell
```

Die Waende als Graph: ihre Stuecke und die Zellen, die sie bilden.

- `stuecke: Tuple[Stueck, ...]`
- `zellen: Tuple[Zelle, ...]`

### _auf_strecke

```python
def _auf_strecke(p: Punkt, a: Punkt, b: Punkt) -> Optional[float]
```

Wo `p` auf der Strecke `a`–`b` liegt (0..1), oder nichts.

### _kreuzung

```python
def _kreuzung(a1: Punkt, a2: Punkt, b1: Punkt, b2: Punkt) -> Optional[Tuple[float, float]]
```

Wo sich zwei Strecken im Innern beider kreuzen -- als Anteile auf beiden.

### zellen

```python
def zellen(waende: Sequence[Wand]) -> Zellenmodell
```

Die Wandachsen als ebener Graph, und die Zellen darin.

Knoten sind die Wandenden, die Stellen, an denen eine Wand auf einer
anderen endet, und Kreuzungen. Dazwischen liegen die Stuecke. Ein Stueck,
das zu keinem Kreis gehoert -- eine freie Wand, eine Bruecke zwischen zwei
Kaesten --, gehoert zu keiner Zelle. Die Zellen sind die beschraenkten
Flaechen des Graphen; gefunden, indem jeder Rand so umlaufen wird, dass die
Flaeche links liegt.

### _loese

```python
def _loese(matrix: List[List[float]], rechts: List[float]) -> List[float]
```

Gauss mit Spaltenpivot; regularisiert nur, wo es noetig ist.

Eine Wandanordnung, die eine Richtung gar nicht steift -- nur parallele
Waende --, gibt eine singulaere Matrix. Dann macht ein Hauch auf der
Diagonale daraus die Loesung kleinster Laenge; ob sie die Last wirklich
traegt, prueft der Aufrufer an der Probe. Sonst bleibt die Matrix, wie
sie ist -- der Hauch verschoebe auch eine eindeutige Loesung.

### _gauss

```python
def _gauss(matrix: List[List[float]], rechts: List[float], *, singulaer_erlaubt: bool=False) -> Optional[List[float]]
```

Gauss mit Spaltenpivot. `None`, wenn ein Pivot verschwindet.

### Verteilung

```python
@dataclass(frozen=True)
class Verteilung
```

Wie `(V_y, V_z, T)` auf die Waende faellt.

- `aus_querkraft: Tuple[float, ...]` – Je Wand die Kraft entlang ihrer Achse aus der Verschiebung, in N.
- `fluss: Tuple[float, ...]` – Je Stueck der Schubfluss entlang seiner Wand, in N/m -- alles zusammen.
- `versatz: float` – `ΔT`: das Moment der Querkraftanteile um den Schwerpunkt, in Nm.
- `zellenfluss: Tuple[float, ...]` – Je Zelle ihr Umlauf-Schubfluss `q_k`, in N/m.
- `mit_drehung: bool` – Ob die Torsion ueber die Federn lief (keine Zelle).

### _hebel

```python
def _hebel(w: Wand, bezug: Punkt) -> float
```

Moment einer Einheitskraft entlang der Wand um den Bezugspunkt.

### verteilen

```python
def verteilen(waende: Sequence[Wand], modell: Zellenmodell, *, V_y: float, V_z: float, T: float, bezug: Punkt) -> Verteilung
```

`(V_y, V_z, T)` auf die Waende, nach dem Modell im Kopf dieser Datei.

Wirft [[opencivil.querschnitt.schubwaende#WandFehler|WandFehler]], wenn die Waende eine Komponente nicht tragen
koennen -- etwa V_y bei lauter senkrechten Waenden, oder Torsion bei einer
einzigen Wand.

### _verschieben

```python
def _verschieben(waende: Sequence[Wand], V_y: float, V_z: float) -> List[float]
```

Die Querkraft ueber eine reine Verschiebung: `K·u = V`.

### _verschieben_und_drehen

```python
def _verschieben_und_drehen(waende: Sequence[Wand], V_y: float, V_z: float, T: float, bezug: Punkt) -> List[float]
```

Querkraft und Torsion ueber Verschiebung und Drehung: drei Gleichungen.

### _bredt

```python
def _bredt(waende: Sequence[Wand], modell: Zellenmodell, T: float) -> List[float]
```

Die Umlauf-Schubfluesse der Zellen: Gleichgewicht und gleiche Verdrillung.
Eine Zelle allein ergibt `T / (2 · A_k)` ([[opencivil.querschnitt.schubwaende#Konstanten|REFERENZ_ZELLE]]); die
gleiche Verdrillung mehrerer ist Vorgabe.

Unbekannt sind `q_0 … q_(n-1)` und `θ`. Je Zelle:

```
Σ_Rand (l/b_w) · (q_k - q_Nachbar) - 2·A_k·θ = 0
```

und dazu `Σ 2·A_k·q_k = T`.

### Wandwiderstand

```python
@dataclass(frozen=True)
class Wandwiderstand
```

Was eine Wand je Laenge aufnimmt, bei der guenstigsten Neigung.

- `alpha: int`
- `v_Rd_s: float` – Buegel, in N/m Wandlaenge.
- `v_Rd_c: float` – Druckdiagonale, in N/m Wandlaenge.

#### Wandwiderstand.v_Rd

```python
@property
def v_Rd(self) -> float
```

### widerstand

```python
def widerstand(w: Wand, *, alpha_min: int, alpha_max: int, zugkraft: bool) -> Wandwiderstand
```

Der Widerstand einer Wand je Laenge: das Fachwerk mit dem Hebelarm eins,
ganzgradig ueber α, massgebend das groesste `min(v_Rd,s; v_Rd,c)`
([[opencivil.querschnitt.schubwaende#Konstanten|REFERENZ_WAND]]). Bei Normalzug gelten die gehobenen Grenzen der
Platte ([[opencivil.querschnitt.platte#druckfeldgrenzen|druckfeldgrenzen]]).

### Laengszug

```python
@dataclass(frozen=True)
class Laengszug
```

Die Zugkraft, die das Druckfeld der Waende in Laengsrichtung braucht.

- `N: float`
- `M_y: float`
- `M_z: float`

### laengszug

```python
def laengszug(modell: Zellenmodell, verteilung: Verteilung, neigungen: Sequence[int], bezug: Punkt) -> Laengszug
```

`ΔN = Σ |q|·l·cot α` ueber alle Wandstuecke, je Stueck in seiner Mitte
([[opencivil.querschnitt.schubwaende#Konstanten|REFERENZ_LAENGSZUG]]).

Das Druckfeld einer Wand mit dem Fluss q braucht je Laenge den Zug
`q · cot α`, gleichmaessig ueber die Wand verteilt; seine Resultierende
liegt in der Mitte -- dasselbe wie `V · cot α / 2` in jedem Gurt. Liegen
die Mitten nicht im Schwerpunkt, gibt das auch Momente:

```
ΔM_y = -Σ ΔN_i · (z_i - z_S)        ΔM_z = -Σ ΔN_i · (y_i - y_S)
```

`neigungen` ist je Wand das α, das ihr Nachweis waehlt.


## Konstanten

- `REFERENZ_WAND = 'SIA 262:2025, 4.3.3.4.3, (45); 4.3.3.4.6, (47)'` – Wo der Widerstand einer Wand steht: Buegel und Druckdiagonale.
- `REFERENZ_ZELLE = 'SIA 262:2025, 4.3.5.2, (55), Figur 20'` – Wo die Torsion einer Zelle steht.
- `REFERENZ_TORSION = 'SIA 262:2025, 4.3.5.2, (55); 4.3.5.5; 4.3.3.4.3, (45); 4.3.3.4.6, (4…` – Querkraft und Torsion zusammen: die Zelle, kombiniert nach 4.3.5.5, und je Wand das Fachwerk.
- `REFERENZ_LAENGSZUG = 'SIA 262:2025, 4.3.3.4.11, (51); 4.3.5.4'` – Wo die Laengszugkraft aus dem Druckfeld steht.
- `KNOTEN_TOLERANZ = 1e-06` – Wann zwei Punkte im Graphen der Wandachsen derselbe Knoten sind, in Metern. Gezeichnet wird auf Millimeter; ein Tausendstel davon fasst alles Rundungsrauschen und trennt alles, was jemand absichtlich auseinanderlegt.

## Braucht

- [[opencivil.querschnitt.fachwerk]]
- [[opencivil.querschnitt.platte]]

## Gebraucht von

- [[opencivil.nachweis.qa_kennzahlen]]
- [[opencivil.nachweis.schubwandnachweis]]
- [[opencivil.querschnitt.analyse]]
