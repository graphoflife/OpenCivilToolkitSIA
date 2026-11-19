---
erzeugt: e5ef14139f23
art: modul
tags: [modul]
---
> [!abstract] opencivil/stabwerk/system.py
> das Stabwerk, eben und im Raum: Unbekannte, Zusammenbau, Loesen.
> Paket [[opencivil.stabwerk]] · [Quelltext](../../opencivil/stabwerk/system.py)

## VERANTWORTUNG

Aus einem System -- eben ([[opencivil.stabwerk.modell]]) oder im Raum
([[opencivil.stabwerk3d.modell]]) -- die Unbekannten, die
Steifigkeitsmatrix und je Lastfall und Kombination die rechte Seite -- und
nach dem Loesen Verschiebungen, Stabendkraefte und Lagerkraefte. Wie die
Schnittgroessen laengs der Staebe verlaufen, rechnet
[[opencivil.stabwerk.verlauf|verlauf]] aus dem, was hier herauskommt.


## EBEN UND IM RAUM

Gerechnet wird immer im Raum, mit den Staeben aus
[[opencivil.stabwerk3d.stab]]. Was die Ebene anders macht, sagt ihre
Art ([[opencivil.stabwerk.art|art]]): in welchen Richtungen sich ein Ort
verschiebt und um welche Achsen er sich dreht, ob ein Stab sich auch quer
zur Ebene biegt und Torsion traegt, wie seine Achsen liegen. Was aus der
Ebene hinausfuehrte, ist keine Unbekannte und kein Lager -- es gibt es
nicht. Die Ergebnisse stehen in den Achsen der Art: eben `(u_x, u_z, φ)`
und `(R_x, R_z, M)`, wie von Hand.


## ORTE UND TEILSTAEBE

Gerechnet wird an Orten, nicht an Knoten. Ein Ort ist ein Knoten der
Beschreibung -- oder ein Punkt im Innern eines Stabs, wo er geteilt ist:

* Liegt ein Knoten auf einem Stab, nicht an dessen Ende, ist er mit ihm
  verbunden (T-Stoss); der Stab wird dort geteilt. Linien, die sich ohne
  Knoten kreuzen, sind nicht verbunden -- dazu ein Hinweis.
* Ein gebetteter Stab wird in kurze Stuecke geteilt, nach der Regel des
  gebetteten Stabs ([[opencivil.stabwerk.stab#schritt|schritt]]), mit dem
  groessten β quer und laengs. Hoechstens [[opencivil.stabwerk.system#Konstanten|TEILE_HOECHSTENS]].

Zwischen zwei Orten liegt ein Teilstab -- ein Stab im Sinn von
[[opencivil.stabwerk3d.stab|stab]].


## UNBEKANNTE

Je Ort seine Verschiebungen und Drehungen, weniger was festgehalten ist --
als Richtungen: ein Lager haelt in den Achsen des Systems, ein festes
Linienlager laengs oder quer zu seinem Stab, also auch schief. Je Ort eine
orthonormale Basis aus den festen Richtungen und dem, was frei bleibt;
unbekannt sind nur die freien, moeglichst entlang der Achsen der Art.


## GELENKE -- IM RAUM NACH VORGABE, NICHT NACHGESCHLAGEN

Ein Gelenk am Stabende gibt dem Stab dort eigene Drehungen als Unbekannte,
mit der Steifigkeit `4EI/L` des Stabs; der Knoten dreht sich davon
unabhaengig. In der Ebene ist es eine. Im Raum loest das Gelenk alle drei
Momente, wie ein Kugelgelenk: Drehungen um y und z des Stabs, und um x, wenn
er Torsion traegt. Mit Gelenken an beiden Enden traegt er keine: er drehte
sich sonst frei um seine Achse. Ein Fachwerk aus lauter gelenkig
angeschlossenen Staeben rechnet so im Raum wie in der Ebene; ein Moment um
die Achse eines solchen Stabs hat keinen Halt und ist ein Fehler.


## DREHUNG OHNE STEIFIGKEIT

Ein Ort hat Drehsteifigkeit um die Achsen, die ein starr angeschlossener
Stab, eine Drehfeder oder eine Einspannung halten -- um die uebrigen nicht,
in der Ebene etwa, wenn er nur an Gelenken haengt. Diese Drehungen sind
gestrichen und null gesetzt, und die Ausgabe sagt es ([[opencivil.stabwerk.system#Konstanten|UNBESTIMMT]]).
Erkannt wird das an der Verbindung, nicht an einer Zahl. Greift dort ein
Moment an, ist das ein Fehler -- nichts koennte es aufnehmen.

Die Torsion haelt einen Knoten nur, wenn etwas das andere Ende des Stabs
haelt. Haelt nichts, dreht sich der Stab mit dem Knoten um seine Achse: Das
System ist beweglich, und die Meldung sagt, dass sich dabei nichts
verschiebt. Ein einfacher Balken im Raum auf zwei gelenkigen Lagern braucht
darum an einem Ende eine Gabel -- ein Lager, das die Drehung um seine Achse
festhaelt.


## FESTE LINIENLAGER

Liegt ein Stab quer in z fest auf, biegt er sich nicht in seiner
x-z-Ebene: seine Verschiebung in z ist an jedem Ort null, und wo er ohne
Gelenk anschliesst, auch die Drehung um seine y-Achse. Seine Lasten in
dieser Ebene gehen geradewegs ins Lager; er selbst hat dort keine Querkraft
und kein Moment. Quer in y und laengs ebenso; die Torsion traegt er weiter.
Das ist der Grenzfall einer unendlich steifen Bettung -- und genau.


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

Was die Rechnung zu sagen hat. `fehler`: etwas ist falsch -- rot, und
die Rechnung haelt an. `unfertig`: es fehlt nur etwas, etwa ein
geloeschtes Material -- grau, aber ohne es haelt die Rechnung auch an
(Benutzer, 2026-11-19). Sonst ist es ein Hinweis, und es wird gerechnet.

- `text: str`
- `elemente: Tuple[str, ...] = ()`
- `fehler: bool = True`
- `unfertig: bool = False`

#### Meldung.haelt_an

```python
@property
def haelt_an(self) -> bool
```

#### Meldung.als_dict

```python
def als_dict(self) -> Dict[str, Any]
```

Fuer die Oberflaeche: `fehler` steht rot, `unfertig` grau, und beide halten an.

### Ort

```python
@dataclass
class Ort
```

Ein Punkt des Systems mit Unbekannten -- ein Knoten oder ein Punkt in einem Stab.

- `name: str`
- `x: float`
- `y: float`
- `z: float`
- `knoten: Optional[str] = None` – Der Knoten der Beschreibung -- `None` im Innern eines Stabs.
- `stab: Optional[str] = None`
- `stelle: float = 0.0` – Bei einem inneren Ort: wo auf welchem Stab, in m ab seinem Anfang.
- `zwang: List[Vektor] = field(default_factory=list)` – Die Richtungen, in denen er nicht verschoben wird -- wie gesammelt.
- `drehzwang: List[Vektor] = field(default_factory=list)` – Die Achsen, um die er nicht gedreht wird -- wie gesammelt.
- `steif: List[Vektor] = field(default_factory=list)` – Die Achsen, um die ihn etwas steif haelt: Staebe und Drehfedern -- wie gesammelt.
- `fest: List[Vektor] = field(default_factory=list)`
- `frei: List[Vektor] = field(default_factory=list)` – Orthonormal: die festen und die freien Richtungen der Verschiebung.
- `dreh_fest: List[Vektor] = field(default_factory=list)`
- `dreh_frei: List[Vektor] = field(default_factory=list)`
- `offen: List[Vektor] = field(default_factory=list)` – Orthonormal: die Drehachsen -- fest, frei und ohne Steifigkeit, also gestrichen.
- `verschiebung: List[int] = field(default_factory=list)` – Je freie Richtung die Nummer ihrer Unbekannten.
- `drehung: List[int] = field(default_factory=list)` – Je freie Drehachse die Nummer ihrer Unbekannten.
- `feder: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])` – Federn in x, y und z des Systems, N/m.
- `drehfeder: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])` – Drehfedern um x, y und z des Systems, Nm/rad.

#### Ort.punkt

```python
@property
def punkt(self) -> Vektor
```

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
- `achsen: Tuple[Vektor, Vektor, Vektor]`
- `L_stab: float = 0.0` – Die Laenge des ganzen Stabs.
- `k_y: float = 0.0`
- `k_z: float = 0.0`
- `k_x: float = 0.0` – Die Bettung quer in y und z und laengs, N/m².
- `biegung_y: bool = True` – Ob er sich in seiner x-y-Ebene biegt -- nicht, wenn er quer in y fest aufliegt, und nicht in der Ebene.
- `biegung_z: bool = True` – Ob er sich in seiner x-z-Ebene biegt -- nicht, wenn er quer in z fest aufliegt.
- `laengs: bool = True` – Ob er sich dehnt -- nicht, wenn er laengs fest aufliegt.
- `torsion: bool = True` – Ob er Torsion traegt -- nicht mit Gelenken an beiden Enden, und nicht in der Ebene.
- `gelenk_a: bool = False`
- `gelenk_b: bool = False`
- `gelenkindizes: Dict[Tuple[str, int], int] = field(default_factory=dict)` – Je Ende (`a`, `b`) und Achse des Stabs (0, 1, 2) die Nummer seiner Drehung am Gelenk.
- `k: List[List[float]] = field(default_factory=list)`
- `abbildung: List[List[Tuple[int, float]]] = field(default_factory=list)` – Je lokale Unbekannte (u, v, w, θx, θy, θz am Anfang, dann am Ende): `[(Nummer, Beiwert)]`.

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

#### Teilstab.EI_y

```python
@property
def EI_y(self) -> float
```

#### Teilstab.EI_z

```python
@property
def EI_z(self) -> float
```

#### Teilstab.GI_T

```python
@property
def GI_T(self) -> float
```

#### Teilstab.gesperrt

```python
@property
def gesperrt(self) -> Tuple[int, ...]
```

Die lokalen Unbekannten der Teile, die er nicht traegt: wo ein festes
Linienlager alles nimmt, die Torsion zwischen zwei Gelenken -- und in
der Ebene, was aus ihr hinausfuehrte.

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
- `lasten: st3.Lasten`
- `f: List[float]` – Die arbeitsgleichen Knotenkraefte seiner Lasten.
- `d: List[float]` – Die Verschiebungen seiner Enden.
- `s: List[float]` – Die Kraefte auf seine Enden: `k · d - f`.

### Fall

```python
@dataclass
class Fall
```

Ein Lastfall oder eine Kombination, gerechnet. Verschiebungen und Kraefte
in den Achsen der Art: erst je Achse eine Verschiebung oder Kraft, dann
je Drehachse eine Drehung oder ein Moment.

- `name: str`
- `kombination: bool`
- `F: List[float]`
- `x: List[float]`
- `teile: List[Teilergebnis]`
- `verschiebungen: Dict[str, Werte]` – Je Ort -- auch die inneren --, eben `(u_x, u_z, φ)`, im Raum `(u_x, u_y, u_z, φ_x, φ_y, φ_z)`.
- `lagerkraefte: Dict[str, Werte]` – Je gehaltenen Ort `(R_x, R_z, M)` oder `(R_x, R_y, R_z, M_x, M_y, M_z)`, auf das Tragwerk wirkend.
- `linienlast: Dict[str, Werte]` – Je fest aufliegenden Stab, was seine Lasten geradewegs ins Lager geben -- Kraft und Moment um den Ursprung.
- `bettung: Dict[str, Werte]` – Je gebetteten Stab die Summe der Bettungskraefte auf das Tragwerk -- ebenso.
- `lastsumme: Werte`
- `gleichgewicht: Werte` – Was in den Summen der Kraefte und der Momente um den Ursprung uebrig bleibt -- null bis auf Rundung.

### Ergebnis

```python
@dataclass
class Ergebnis
```

- `art: Art`
- `meldungen: List[Meldung] = field(default_factory=list)`
- `orte: Dict[str, Ort] = field(default_factory=dict)`
- `teilstaebe: List[Teilstab] = field(default_factory=list)`
- `unbekannte: List[str] = field(default_factory=list)` – Je Unbekannte ein Name, fuer die Herleitung: `u_x(K1)`, `φ(K2)`, `θ_y(L3, Ende)`.
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

Die Knoten, deren Drehung um eine Achse gestrichen ist.

### _name

```python
def _name(zeichen: str, ort: str, richtung: Vektor, achsen: Sequence[Tuple[str, Vektor]]) -> str
```

`u_x(K1)` oder `φ(K1)` entlang einer Achse der Art, sonst mit der Richtung in ihren Achsen.

### _traegt_torsion

```python
def _traegt_torsion(stab_: Stab) -> bool
```

Ob ein Stab Torsion traegt: nicht mit Gelenken an beiden Enden -- siehe Dateikopf.

### rechnen

```python
def rechnen(system: Any, art: Art) -> Ergebnis
```

Ein System dieser Art, gerechnet -- oder, wo das nicht geht, die Meldungen dazu.

### _ende

```python
def _ende(t: Teilstab, ende: str) -> List[List[Tuple[int, float]]]
```

Wie u, v, w und θx, θy, θz eines Stabendes an den Unbekannten haengen.


## Konstanten

- `TEILE_HOECHSTENS = round(32 / st.TEILUNG)` – In hoechstens so viele Stuecke wird ein gebetteter Stab geteilt: so viele, wie die Regel des gebetteten Stabs bis β·L = 32 verlangt.
- `UNBESTIMMT = 'Verdrehung nicht bestimmbar, da keine Steifigkeit'` – Was an einem Knoten steht, dessen Drehung gestrichen ist.
- `SUMMEN = 'Bei Linienlagern und Bettung steht die Summe; ihr Moment um den Ursp…` – Was unter den Lagerkraeften steht, wenn Linienlager oder Bettung dabei sind.

## Braucht

- [[opencivil.stabwerk.art]]
- [[opencivil.stabwerk.matrix]]
- [[opencivil.stabwerk.modell]]
- [[opencivil.stabwerk.stab]]
- [[opencivil.stabwerk3d.modell]]
- [[opencivil.stabwerk3d.raum]]
- [[opencivil.stabwerk3d.stab]]

## Gebraucht von

- [[opencivil.decke.aufteilung]]
- [[opencivil.decke.lasten]]
- [[opencivil.decke.rechnung]]
- [[opencivil.decke.streifen]]
- [[opencivil.decke.werk]]
- [[opencivil.projekt.aufbau.balkensystem]]
- [[opencivil.projekt.aufbau.decke]]
- [[opencivil.projekt.aufbau.faelle]]
- [[opencivil.stabwerk.herleitung]]
- [[opencivil.stabwerk.rechnung]]
- [[opencivil.stabwerk3d.herleitung]]
- [[opencivil.web.balkendaten]]
- [[opencivil.web.deckendaten]]
