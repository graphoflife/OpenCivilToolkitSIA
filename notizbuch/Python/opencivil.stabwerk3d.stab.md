---
erzeugt: 73436e317823
art: modul
tags: [modul]
---
> [!abstract] opencivil/stabwerk3d/stab.py
> der raeumliche Stab: drei ebene in einem.
> Paket [[opencivil.stabwerk3d]] · [Quelltext](../../opencivil/stabwerk3d/stab.py)

## VERANTWORTUNG

Was ein Stab im Raum zum System beitraegt, in seinen eigenen Achsen: die
Achsen selbst, die Steifigkeitsmatrix 12 × 12, die Bettung und die Lasten --
in seinen Achsen, als arbeitsgleiche Knotenkraefte und als Resultierende.
Zusammengebaut wird in [[opencivil.stabwerk.system|system]].


## DIE ACHSEN DES STABS

`x` laeuft vom Anfang zum Ende. `z` steht senkrecht dazu in der
lotrechten Ebene durch den Stab und zeigt nach unten: dort liegt die
gestrichelte Faser, wie in der Ebene. `y = z × x` ergaenzt zum
Rechtssystem. Bei einem lotrechten Stab gibt es keine lotrechte Ebene durch
ihn; dort ist `y` die Achse `-y` des Systems.

In einem Rahmen in der x-z-Ebene liegt `z` darum auf der gestrichelten
Faser des 2D-Balkensystems -- bei jedem Stab, der nach rechts oder lotrecht
laeuft: `y` ist dort `-y` des Systems, und `N`, `V_z` und `M_y`
sind `N`, `V` und `M` der Ebene. Laeuft ein Stab nach links, liegt
die gestrichelte Faser der Ebene oben, `z` bleibt unten: `V_z` und
`M_y` haben dort das andere Vorzeichen. Der Drehwinkel `β`
dreht `y` und `z` im Rechtssinn um `x`. Bei `β = 0` steht der Steg
eines Profils, das sich um `y` biegt, in der lotrechten Ebene des Stabs.

Lotrecht heisst: weniger als [[opencivil.stabwerk3d.raum#Konstanten|TOLERANZ]]
daneben -- so genau rundet das Zeichenfenster.


## IN DER EBENE

Liegt das ganze System in der x-z-Ebene und bleibt darin
([[opencivil.stabwerk.art#Konstanten|EBENE]]), ist `y` jedes Stabs `-y`
des Systems, wie sonst nur bei einem lotrechten ([[opencivil.stabwerk3d.stab#achsen_eben|achsen_eben]]).
`z = x × y` steht dann rechts des Stabs, vom Anfang zum Ende gesehen, auf
der gestrichelten Faser des 2D-Balkensystems -- auch wenn er nach links
laeuft. So sind `N`, `V_z` und `M_y` in jedem Stab `N`, `V` und
`M` der Ebene, und eine Drehung um `y` des Stabs ist eine im
Gegenuhrzeigersinn.


## DREI EBENE STAEBE

Ein gerader Stab mit den Hauptachsen y und z, ohne Schubverformung und mit
Torsion nach St. Venant, zerfaellt in drei Teile, die nichts voneinander
wissen: die Biegung in der x-z-Ebene samt Laengskraft, die Biegung in der
x-y-Ebene und die Torsion -- sie verhaelt sich wie die Laengskraft, mit
`G·I_T` statt `E·A`. Jeder Teil ist ein ebener Stab
([[opencivil.stabwerk.stab]]), dessen y-Achse links liegt und dessen
Moment an der rechten, gestrichelten Faser zieht. Steifigkeit,
arbeitsgleiche Lasten, Bettung, Teilen und Verlauf kommen darum von dort,
ueber die Zuordnung [[opencivil.stabwerk3d.stab#Konstanten|EBENE_Z]], [[opencivil.stabwerk3d.stab#Konstanten|EBENE_Y]], [[opencivil.stabwerk3d.stab#Konstanten|TORSION]]:

```
Ebene z:   x und -z     u, -w, θ_y     M_y zieht an +z
Ebene y:   x und -y     -v, -θ_z      M_z zieht an +y
Torsion:   θ_x wie u, das Torsionsmoment wie N
```

Je Ende sechs Unbekannte, in dieser Folge:

```
u   v   w      laengs, in y, in z
θx  θy  θz     Drehungen um x, y und z im Rechtssinn
```

Ein U-Profil hat seinen Schubmittelpunkt neben dem Schwerpunkt; hier
liegen beide auf der Achse, und Woelbkrafttorsion gibt es nicht (nach
Vorgabe, nicht nachgeschlagen).

## Inhalt

### achsen

```python
def achsen(a, b, drehung: float=0.0) -> Tuple[float, Tuple[Vektor, Vektor, Vektor]]
```

Laenge und Achsen `(x, y, z)` eines Stabs von `a` nach `b` --
Einheitsvektoren im System, siehe Dateikopf.

### achsen_eben

```python
def achsen_eben(a, b) -> Tuple[float, Tuple[Vektor, Vektor, Vektor]]
```

Laenge und Achsen eines Stabs in der x-z-Ebene: `y` ist `-y` des
Systems, `z = x × y` liegt rechts des Stabs -- siehe Dateikopf.

### _lotrecht

```python
def _lotrecht(d: Sequence[float]) -> bool
```

Ob ein Stab in Richtung `d` lotrecht steht -- waagrecht weniger lang als die Toleranz.

### drehung_umgekehrt

```python
def drehung_umgekehrt(d: Sequence[float], drehung: float, halbe_drehung: float=math.pi) -> float
```

Der Drehwinkel eines Stabs in Richtung `d`, wenn er umgekehrt laeuft
-- so, dass der Querschnitt bleibt, wie er steht: `z` bleibt, `y`
kehrt um wie `x`. Liegt der Stab nicht lotrecht, bleibt `z` bei
`β = 0` dasselbe, und es ist `-β`; lotrecht kehrt es um, und es ist
`π - β`. Zwischen `-π` und `π` -- in Grad mit ``halbe_drehung =
180``, ohne den Umweg ueber rad und seine Rundung.

### steifigkeit

```python
def steifigkeit(L: float, EA: float, EI_y: float, EI_z: float, GI_T: float) -> Matrix
```

Die Steifigkeitsmatrix 12 × 12 in den Achsen des Stabs.

### bettung

```python
def bettung(L: float, k_y: float=0.0, k_z: float=0.0, k_x: float=0.0) -> Matrix
```

Die konsistente Bettungsmatrix 12 × 12 -- quer in y und z, laengs in x; in N/m².

### Lasten

```python
@dataclass
class Lasten
```

Die Lasten eines Stabs in seinen Achsen, je Teil eine ebene Liste. Jede
Last steht in allen dreien -- wo sie nichts tut, mit null --, damit die
drei Verlaeufe an denselben Stellen springen.

- `z: List[st.Teillast] = field(default_factory=list)`
- `y: List[st.Teillast] = field(default_factory=list)`
- `t: List[st.Teillast] = field(default_factory=list)`

#### Lasten.dazu

```python
def dazu(self, andere: 'Lasten') -> None
```

#### Lasten.mit_torsion

```python
@property
def mit_torsion(self) -> bool
```

Ob eine davon den Stab um seine Achse dreht.

### strecke

```python
def strecke(a: float, b: float, p_a: Vektor=(0.0, 0.0, 0.0), p_b: Vektor=(0.0, 0.0, 0.0), m_a: Vektor=(0.0, 0.0, 0.0), m_b: Vektor=(0.0, 0.0, 0.0)) -> Lasten
```

Eine Last auf `[a, b]`, linear: Kraft je Laenge `p` und Moment je
Laenge `m`, je in x, y und z des Stabs, in N/m und Nm/m.

### punkt

```python
def punkt(a: float, P: Vektor=(0.0, 0.0, 0.0), M: Vektor=(0.0, 0.0, 0.0)) -> Lasten
```

Eine Last an der Stelle `a`: Kraft `P` in N und Moment `M` in Nm, in den Achsen des Stabs.

### aufteilen

```python
def aufteilen(lasten: Lasten, von: float, bis: float, *, ende: bool) -> Lasten
```

Die Lasten, die auf `[von, bis]` liegen -- wie in der Ebene ([[opencivil.stabwerk.stab#aufteilen|opencivil.stabwerk.stab.aufteilen]]).

### knotenlasten

```python
def knotenlasten(L: float, lasten: Lasten) -> List[float]
```

Die arbeitsgleichen Knotenkraefte (12) in den Achsen des Stabs.

### eben

```python
def eben(werte: Sequence[float], ebene) -> List[float]
```

Die sechs ebenen Werte einer Ebene aus den zwoelf raeumlichen -- Verschiebungen wie Kraefte.

### eben_matrix

```python
def eben_matrix(k: Matrix, ebene) -> Matrix
```

Die ebene Matrix 6 × 6 einer Ebene aus der raeumlichen 12 × 12 -- umgekehrt wie beim Einsetzen.

### lastbereich

```python
def lastbereich(last, L: float) -> Union[Tuple[float, float], str]
```

Wo eine Last auf einem Stab der Laenge `L` liegt, `(von, bis)` in m
-- oder ein Satz, warum nicht: eine Stelle ausserhalb des Stabs. Eine
Einzellast steht bei `von`.

### lokal

```python
def lokal(last: Stablast, L: float, achsen: Sequence[Vektor]) -> Union[Lasten, str]
```

Eine Last des Modells in den Achsen ihres Stabs -- oder ein Satz, warum
nicht: eine Stelle ausserhalb des Stabs.

### resultierende

```python
def resultierende(lasten: Lasten, anfang: Vektor, achsen: Sequence[Vektor], *, laengs: bool=True, quer_y: bool=True, quer_z: bool=True, torsion: bool=True) -> List[float]
```

Kraft und Moment um den Ursprung `(F, M)` der Lasten eines Stabs, der
bei `anfang` beginnt -- nur die gewaehlten Anteile. Die ebenen Lasten
tragen ihre Werte in den Achsen ihrer Ebene, siehe Dateikopf.


## Konstanten

- `EBENE_Z = ((0, 0, 1.0), (1, 2, -1.0), (2, 4, 1.0), (3, 6, 1.0), (4, 8, -1.0), (…` – Wie die ebenen Unbekannten (u, v, θ am Anfang, dann am Ende) einer Ebene auf die raeumlichen fallen: (eben, raeumlich, Vorzeichen).
- `EBENE_Y = ((1, 1, -1.0), (2, 5, -1.0), (4, 7, -1.0), (5, 11, -1.0))`
- `TORSION = ((0, 3, 1.0), (3, 9, 1.0))`
- `ZERLEGUNG_LATEX = '\\mathbf{k} = \\mathbf{k}_{z}(EA, EI_y) \\oplus \\mathbf{k}_{y}(EI_z…` – Die Zuordnung in Zeichen -- fuer die Herleitung.
- `DREHUNG_LATEX = '\\mathbf{d} = \\mathbf{T} \\cdot \\mathbf{d}_{glob} \\qquad \\mathbf…` – Die Drehung von den Achsen des Systems in die des Stabs.

## Braucht

- [[opencivil.stabwerk.modell]]
- [[opencivil.stabwerk.stab]]
- [[opencivil.stabwerk3d.modell]]
- [[opencivil.stabwerk3d.raum]]

## Gebraucht von

- [[opencivil.projekt.balkensystem3d]]
- [[opencivil.stabwerk.art]]
- [[opencivil.stabwerk.herleitung]]
- [[opencivil.stabwerk.system]]
- [[opencivil.stabwerk.verlauf]]
- [[opencivil.stabwerk3d.herleitung]]
