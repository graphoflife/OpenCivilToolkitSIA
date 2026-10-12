---
erzeugt: 75f8644149e6
art: modul
tags: [modul]
---
> [!abstract] opencivil/stabwerk/system.py
> das ganze Stabwerk: Unbekannte, Zusammenbau, Loesen.
> Paket [[opencivil.stabwerk]] · [Quelltext](../../opencivil/stabwerk/system.py)

## VERANTWORTUNG

Aus dem [[opencivil.stabwerk.modell#System|System]] die Unbekannten, die
Steifigkeitsmatrix und je Lastfall und Kombination die rechte Seite -- und
nach dem Loesen Verschiebungen, Stabendkraefte und Lagerkraefte. Wie die
Schnittgroessen laengs der Staebe verlaufen, rechnet
[[opencivil.stabwerk.verlauf|verlauf]] aus dem, was hier herauskommt.


## ORTE UND TEILSTAEBE

Gerechnet wird an Orten, nicht an Knoten. Ein Ort ist ein Knoten der
Beschreibung -- oder ein Punkt im Innern eines Stabs, wo er geteilt ist:

* Liegt ein Knoten auf einem Stab, nicht an dessen Ende, ist er mit ihm
  verbunden (T-Stoss); der Stab wird dort geteilt. Linien, die sich ohne
  Knoten kreuzen, sind nicht verbunden -- dazu ein Hinweis.
* Ein gebetteter Stab wird in kurze Stuecke geteilt, so dass jedes hoechstens
  `1/(2β)` lang ist, `β = (k/(4EI))^(1/4)`: dann weicht die kubische
  Naeherung um weniger als ein Promille ab. Hoechstens [[opencivil.stabwerk.system#Konstanten|TEILE_HOECHSTENS]].

Zwischen zwei Orten liegt ein Teilstab -- ein Stab im Sinn von
[[opencivil.stabwerk.stab|stab]].


## UNBEKANNTE

Je Ort zwei Verschiebungen und eine Drehung, weniger was festgehalten ist.
Feste Richtungen kommen von Lagern -- in x und z -- und von festen
Linienlagern, quer oder laengs zur Linie, also auch schief. Je Ort wird darum
eine orthonormale Basis gebildet: die festen Richtungen, und was frei bleibt;
unbekannt sind nur die freien.

Ein Gelenk am Stabende gibt dem Stab dort seine eigene Drehung -- eine
Unbekannte mehr, mit der Steifigkeit `4EI/L` des Stabs. Der Knoten dreht
sich davon unabhaengig.


## DREHUNG OHNE STEIFIGKEIT

Haengt ein Knoten nur an Gelenken, ohne Drehfeder und ohne Einspannung, hat
seine Drehung keine Steifigkeit: ihre Zeile in K waere null. Sie wird
gestrichen und null gesetzt, und die Ausgabe sagt «Verdrehung nicht
bestimmbar, da keine Steifigkeit» ([[opencivil.stabwerk.system#Konstanten|UNBESTIMMT]]). Erkannt wird das an
der Verbindung, nicht an einer Zahl: welche Stabenden ohne Gelenk dort
haengen. Greift an einem solchen Knoten ein Moment an, ist das ein Fehler --
nichts koennte es aufnehmen.


## FESTE LINIENLAGER

Liegt ein Stab quer fest auf, biegt er sich nicht: seine Querverschiebung
ist an jedem Ort null, und wo er ohne Gelenk anschliesst, auch die Drehung.
Seine Querlasten gehen geradewegs ins Lager; er selbst hat keine Querkraft
und kein Moment. Laengs fest dasselbe fuer die Normalkraft. Das ist der
Grenzfall einer unendlich steifen Bettung -- und genau.


## MELDUNGEN

Was nicht zu rechnen ist, wird gemeldet, nicht geworfen: ein bewegliches
System, ein Stab ohne Laenge, eine Last hinter dem Stabende. Das Balkensystem
zeigt die Meldungen an den Elementen; der Rest des Projekts rechnet weiter.

## Inhalt

### Meldung

```python
@dataclass(frozen=True)
class Meldung
```

Was die Rechnung zu sagen hat -- `fehler` haelt sie auf, ein Hinweis nicht.

- `text: str`
- `elemente: Tuple[str, ...] = ()`
- `fehler: bool = True`

### Ort

```python
@dataclass
class Ort
```

Ein Punkt des Systems mit Unbekannten -- ein Knoten oder ein Punkt in einem Stab.

- `name: str`
- `x: float`
- `z: float`
- `knoten: Optional[str] = None` – Der Knoten der Beschreibung -- `None` im Innern eines Stabs.
- `stab: Optional[str] = None`
- `stelle: float = 0.0` – Bei einem inneren Ort: wo auf welchem Stab, in m ab seinem Anfang.
- `zwang: List[Tuple[float, float]] = field(default_factory=list)` – Die Richtungen, in denen er festgehalten ist -- wie gesammelt.
- `fest: List[Tuple[float, float]] = field(default_factory=list)`
- `frei: List[Tuple[float, float]] = field(default_factory=list)` – Orthonormal: die festen und die freien Richtungen.
- `verschiebung: List[int] = field(default_factory=list)` – Je freie Richtung die Nummer ihrer Unbekannten.
- `drehung: str = 'frei'` – `frei`, `fest` oder `unbestimmt`.
- `drehindex: Optional[int] = None`
- `feder_x: float = 0.0`
- `feder_z: float = 0.0`
- `feder_phi: float = 0.0`
- `dreh_fest: bool = False`

#### Ort.gehalten

```python
@property
def gehalten(self) -> bool
```

Ob hier eine Lagerkraft entsteht: etwas Festes oder eine Feder.

### Teilstab

```python
@dataclass
class Teilstab
```

Ein Stueck eines Stabs zwischen zwei Orten.

- `stab: Stab`
- `nummer: int`
- `x0: float`
- `x1: float`
- `a: Ort`
- `b: Ort`
- `c: float`
- `s: float`
- `L_stab: float = 0.0` – Die Laenge des ganzen Stabs.
- `k_quer: float = 0.0`
- `k_laengs: float = 0.0`
- `biegung: bool = True` – Ob er sich biegt -- nicht, wenn er quer fest aufliegt.
- `laengs: bool = True` – Ob er sich dehnt -- nicht, wenn er laengs fest aufliegt.
- `gelenk_a: bool = False`
- `gelenk_b: bool = False`
- `gelenkindex_a: Optional[int] = None`
- `gelenkindex_b: Optional[int] = None`
- `k: List[List[float]] = field(default_factory=list)`
- `abbildung: List[List[Tuple[int, float]]] = field(default_factory=list)` – Je lokale Unbekannte (u, v, θ am Anfang, dann am Ende): `[(Nummer, Beiwert)]`.

#### Teilstab.L

```python
@property
def L(self) -> float
```

#### Teilstab.EA

```python
@property
def EA(self) -> float
```

#### Teilstab.EI

```python
@property
def EI(self) -> float
```

#### Teilstab.lokal

```python
def lokal(self, x: Sequence[float]) -> List[float]
```

Die Verschiebungen seiner Enden, in seinen Achsen, aus der Loesung `x`.

#### Teilstab.bettungsmatrix

```python
def bettungsmatrix(self) -> List[List[float]]
```

### Teilergebnis

```python
@dataclass
class Teilergebnis
```

Was ein Teilstab in einem Fall tut -- in seinen Achsen.

- `teil: Teilstab`
- `lasten: List[st.Teillast]`
- `f: List[float]` – Die arbeitsgleichen Knotenkraefte seiner Lasten.
- `d: List[float]` – Die Verschiebungen seiner Enden.
- `s: List[float]` – Die Kraefte auf seine Enden: `k · d - f`.

### Fall

```python
@dataclass
class Fall
```

Ein Lastfall oder eine Kombination, gerechnet.

- `name: str`
- `kombination: bool`
- `lasten: List`
- `F: List[float]`
- `x: List[float]`
- `teile: List[Teilergebnis]`
- `verschiebungen: Dict[str, Tuple[float, float, float]]` – Je Ort `(u_x, u_z, φ)` -- auch die inneren.
- `lagerkraefte: Dict[str, Tuple[float, float, float]]` – Je gehaltenen Ort `(R_x, R_z, M)`, auf das Tragwerk wirkend.
- `linienlast: Dict[str, Tuple[float, float, float]]` – Je fest aufliegenden Stab, was seine Lasten geradewegs ins Lager geben -- als Summe `(F_x, F_z, M)`.
- `bettung: Dict[str, Tuple[float, float, float]]` – Je gebetteten Stab die Summe der Bettungskraefte auf das Tragwerk.
- `lastsumme: Tuple[float, float, float]`
- `gleichgewicht: Tuple[float, float, float]` – Was in `ΣF_x`, `ΣF_z` und `ΣM` um den Ursprung uebrig bleibt -- null bis auf Rundung.

### Ergebnis

```python
@dataclass
class Ergebnis
```

- `meldungen: List[Meldung] = field(default_factory=list)`
- `orte: Dict[str, Ort] = field(default_factory=dict)`
- `teilstaebe: List[Teilstab] = field(default_factory=list)`
- `unbekannte: List[str] = field(default_factory=list)` – Je Unbekannte ein Name, fuer die Herleitung: `u_x(K1)`, `φ(K2)`, `φ(L3, Ende)`.
- `K: Optional[Profilmatrix] = None`
- `faelle: List[Fall] = field(default_factory=list)`
- `beweglich: List[str] = field(default_factory=list)` – Was sich ohne Widerstand bewegt, wenn das System beweglich ist.

#### Ergebnis.gueltig

```python
@property
def gueltig(self) -> bool
```

#### Ergebnis.fall

```python
def fall(self, name: str) -> Fall
```

#### Ergebnis.unbestimmt

```python
def unbestimmt(self) -> List[str]
```

Die Knoten, deren Drehung gestrichen ist.

### _stelle_auf

```python
def _stelle_auf(stab_a, stab_b, p) -> Optional[float]
```

Wo `p` auf der Strecke a-b liegt (m ab a) -- `None`, wenn daneben oder an einem Ende.

### _kreuzen

```python
def _kreuzen(p1, p2, q1, q2) -> bool
```

Ob sich zwei Strecken im Innern beider kreuzen.

### _basis

```python
def _basis(vektoren: Sequence[Tuple[float, float]]) -> Tuple[List[Tuple[float, float]], List[Tuple[float, float]]]
```

Die festen Richtungen orthonormal -- und was frei bleibt, ebenso.

### rechnen

```python
def rechnen(system: System) -> Ergebnis
```

Das System, gerechnet -- oder, wo das nicht geht, die Meldungen dazu.

### _ende

```python
def _ende(ort: Ort, c: float, s: float, gelenk: bool, gelenkindex: Optional[int], biegung: bool) -> List[List[Tuple[int, float]]]
```

Wie u, v und θ eines Stabendes an den Unbekannten haengen.

### _lokal

```python
def _lokal(last: Stablast, L: float, c: float, s: float)
```

Eine Last des Modells in den Achsen ihres Stabs -- oder ein Satz, warum
nicht: eine Stelle ausserhalb des Stabs.

### _resultierende

```python
def _resultierende(teil, a, c: float, s: float, *, quer: bool=True, laengs: bool=True, moment: bool=True) -> Tuple[float, float, float]
```

Kraft `(F_x, F_z)` und Moment um den Ursprung einer Last in den Achsen
eines Stabs, der bei `a` beginnt -- nur die gewaehlten Anteile.

### _summe_der_lasten

```python
def _summe_der_lasten(rechnung: _Rechnung, fall: Lastfall) -> List[float]
```

Alle Lasten des Falls als Kraft auf das Tragwerk und Moment um den Ursprung.


## Konstanten

- `TOLERANZ = 1e-06` – Wie nahe ein Knoten an einem Stab liegen muss, um mit ihm verbunden zu sein -- in m. Das Zeichenfenster rundet auf ein Millionstel.
- `TEILE_HOECHSTENS = 64` – In hoechstens so viele Stuecke wird ein gebetteter Stab geteilt.
- `UNBESTIMMT = 'Verdrehung nicht bestimmbar, da keine Steifigkeit'` – Was an einem Knoten steht, dessen Drehung gestrichen ist.

## Braucht

- [[opencivil.stabwerk.matrix]]
- [[opencivil.stabwerk.modell]]
- [[opencivil.stabwerk.stab]]

## Gebraucht von

- [[opencivil.projekt.balkensystem]]
- [[opencivil.stabwerk.herleitung]]
- [[opencivil.stabwerk.rechnung]]
- [[opencivil.web.balkendaten]]
