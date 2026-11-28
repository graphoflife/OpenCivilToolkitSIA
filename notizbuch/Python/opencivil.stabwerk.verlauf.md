---
erzeugt: 552448dd3150
art: modul
tags: [modul]
---
> [!abstract] opencivil/stabwerk/verlauf.py
> Schnittgroessen und Biegelinien laengs eines Stabs, eben und im Raum.
> Paket [[opencivil.stabwerk]] · [Quelltext](../../opencivil/stabwerk/verlauf.py)

## VERANTWORTUNG

Aus dem, was [[opencivil.stabwerk.system|system]] an den Enden jedes Teilstabs
findet – Kraefte und Verschiebungen –, und aus seinen Lasten die Verlaeufe
dazwischen: Normalkraft, Querkraefte, Torsionsmoment, Biegemomente,
Verschiebungen und Verdrehungen. Dazu die groessten und kleinsten Werte und
wo sie liegen.


## EIN STAB AUS EBENEN TEILEN

Ein Stab besteht aus drei ebenen Teilen ([[opencivil.stabwerk3d.stab]]):
der Biegung in seiner x-z-Ebene samt Laengskraft, der Biegung in seiner
x-y-Ebene und der Torsion. Jeder Teil rechnet fuer sich
([[opencivil.stabwerk.verlauf#ebener_verlauf|ebener_verlauf]]), dann werden sie zusammengesetzt. Die drei Teile
springen an denselben Stellen, weil jede Last in allen dreien steht. In der
Ebene sind die beiden letzten null.


## VORZEICHEN EINES EBENEN TEILS

Wie man sie von Hand rechnet: `N > 0` ist Zug; `M > 0` zieht an der
gestrichelten Faser, der rechten Seite des Teils vom Anfang zum Ende
gesehen; `V = dM/dx + m` (`m` ein verteiltes Moment im
Gegenuhrzeigersinn). Ein Einfeldtraeger unter Last nach unten hat also ein
positives Feldmoment und links eine positive Querkraft.

Aus den Kraeften `s` auf die Enden (in den Achsen des Teils, y links,
Gegenuhrzeigersinn) folgt am Anfang:

```python
N(0) = -s_u      V(0) = s_v      M(0) = -s_θ
```

und mit den Lasten `p_x`, `p_y` und `m` laengs des Stabs:

```
dN/dx = -p_x     dV/dx = p_y     dM/dx = V - m
```

Eine Einzelkraft laesst N um `-P_x` und V um `+P_y` springen, ein
Einzelmoment M um `-M`.

VORZEICHEN DES STABS – M_z NACH VORGABE, NICHT NACHGESCHLAGEN:
In den Achsen des Stabs. `N > 0` ist Zug, `T > 0` dreht im Rechtssinn
um die nach aussen zeigende Normale des Schnitts. `M_y > 0` zieht an der
Faser auf der Seite +z, `M_z > 0` an der auf der Seite +y: beide Ebenen
wie die eines ebenen Teils, mit `V_z = dM_y/dx` und `V_y = dM_z/dx`, wo
kein verteiltes Moment liegt. Die Spannung im Querschnitt ist damit
`σ = N/A + M_y·z/I_y + M_z·y/I_z`; die Rechtsschraube gaebe `M_z` das
andere Vorzeichen. In der Ebene liegt z auf der gestrichelten Faser: `N`,
`V_z` und `M_y` sind `N`, `V` und `M` von Hand.

Verschiebungen `u`, `v`, `w` in x, y und z des Stabs, Verdrehungen
`theta_x`, `theta_y`, `theta_z` im Rechtssinn um diese Achsen; dazu
`ux`, `uy`, `uz` in den Achsen des Systems und die Durchbiegungen
`f_y` und `f_z` gegen die Sehne zwischen den Stabenden.


## STUECKWEISE POLYNOME

Zwischen zwei Laststellen sind die Lasten linear – also V quadratisch, M
kubisch, die Biegelinie vom fuenften Grad. Gerechnet wird darum genau, mit
Polynomen ([[opencivil.stabwerk.verlauf#Polynom|Polynom]]), nicht an Stuetzstellen. Ein gebetteter Teilstab
traegt dazu `-k · v(x)` mit der kubischen Biegelinie seiner Enden; dort ist
es die Naeherung, mit der auch gerechnet wurde. Quer darf `k` vom Anfang
zum Ende linear wachsen, wie in der Bettungsmatrix – so rechnet auch der
Pfahl ([[opencivil.pfahl.bettung]]) seine Schnittkraefte.

Die Biegelinie folgt aus `v'' = M/EI` und `u' = N/EA`, je Teilstab von
seinem Anfang aus – Verschiebung und Drehung dort sind die der Loesung, am
Ende trifft sie die des Endes (eine Probe in den Tests).


## EXTREMWERTE

Ein Moment ist dort am groessten, wo `dM/dx = V - m` null wird, oder an
einer Grenze: einem Stabende, einer Laststelle – dort auf beiden Seiten.
Gesucht wird an genau diesen Stellen, nicht im Raster der Bilder. Was sich
nur in der Rundung unterscheidet, gilt als gleich, und dann die vorderste
Stelle ([[opencivil.stabwerk.verlauf#vorderste_extreme|vorderste_extreme]]) – dieselbe Regel wie in der Decke. Ueber
alle Staebe eines Falls fasst [[opencivil.stabwerk.verlauf#grenzwerte|grenzwerte]] zusammen: den kleinsten,
den groessten und den massgebenden Wert, den mit dem groessten Betrag –
bei gleichem Betrag den positiven. Bericht und Bildschirm zeigen dieselben.
Die groesste Verschiebung ist ebenso genau: ihr Quadrat `u² + v² + w²`
ist ein Polynom ([[opencivil.stabwerk.verlauf#Stabverlauf.groesste_verschiebung|Stabverlauf.groesste_verschiebung]]).

## Inhalt

### Polynom

```python
class Polynom
```

`k[0] + k[1]·x + k[2]·x² + …` – mit Grad, so hoch es sein muss.

#### Polynom.durch

```python
@classmethod
def durch(cls, x0: float, y0: float, x1: float, y1: float) -> 'Polynom'
```

Die Gerade durch zwei Punkte – waagrecht, wo sie zusammenfallen.

#### Polynom.stammfunktion

```python
def stammfunktion(self, ab: float) -> 'Polynom'
```

`∫_ab^x p(ξ) dξ` – null bei `x = ab`.

#### Polynom.ableitung

```python
def ableitung(self) -> 'Polynom'
```

#### Polynom.nullstellen

```python
def nullstellen(self, a: float, b: float, stellen: int=48) -> List[float]
```

Wo es in `(a, b)` das Vorzeichen wechselt – abgetastet und halbiert.

### EbenesIntervall

```python
@dataclass
class EbenesIntervall
```

Ein Stueck eines ebenen Teils ohne Laststelle – alles darauf Polynome in x ab dem Stabanfang.

- `x0: float`
- `x1: float`
- `N: Polynom`
- `V: Polynom`
- `M: Polynom`
- `u: Polynom` – Laengs, in x des Stabs.
- `v: Polynom` – Quer, in y des Stabs – links positiv.
- `theta: Polynom`
- `p_y: Polynom = field(default_factory=lambda: NULL)` – Die Querlast samt Bettung – fuer das, was ins Linienlager geht.

### Intervall

```python
@dataclass
class Intervall
```

Ein Stueck eines Stabs ohne Laststelle – alles darauf Polynome in x ab dem Stabanfang.

- `x0: float`
- `x1: float`
- `N: Polynom`
- `V_y: Polynom`
- `V_z: Polynom`
- `T: Polynom`
- `M_y: Polynom`
- `M_z: Polynom`
- `u: Polynom`
- `v: Polynom`
- `w: Polynom`
- `theta_x: Polynom`
- `theta_y: Polynom`
- `theta_z: Polynom`
- `p_y: Polynom = field(default_factory=lambda: NULL)`
- `p_z: Polynom = field(default_factory=lambda: NULL)` – Die Querlast samt Bettung in y und z des Stabs.

### _rauschen

```python
def _rauschen(*werte: float) -> float
```

Was zwischen Werten dieser Groesse nur Rundung ist: ein Milliardstel, mindestens 1e-9 in SI-Basis.

### vorderste_extreme

```python
def vorderste_extreme(werte: Sequence[Tuple[Ort, float]]) -> Tuple[Tuple[Ort, float], Tuple[Ort, float]]
```

Aus `(Ort, Wert)`, in ihrer Folge: das erste Paar mit dem kleinsten und
das erste mit dem groessten Wert. Was sich nur in der Rundung
unterscheidet ([[opencivil.stabwerk.verlauf#_rauschen|_rauschen]]), gilt als gleich: sonst entschiede bei
gleichen Werten an zwei Orten das Rauschen – in einem symmetrischen
Traeger, an einem Stab, der sich nirgends biegt.

### massgebender

```python
def massgebender(werte: Sequence[Tuple[Ort, float]]) -> Tuple[Ort, float]
```

Aus `(Ort, Wert)`, in ihrer Folge: das erste Paar mit dem groessten
Betrag, bei gleichem Betrag das erste positive – gleich bis auf Rundung
wie in [[opencivil.stabwerk.verlauf#vorderste_extreme|vorderste_extreme]]. Bis 2026-11-20 war das ein Schluessel
fuer `max` (`nach_betrag`), und das Rauschen entschied zwischen
Werten, die nur in der Rundung abwichen.

### Extrem

```python
@dataclass(frozen=True)
class Extrem
```

Der kleinste und der groesste Wert einer Groesse, je mit Stelle: `(x, Wert)`.

- `kleinst: Tuple[float, float]`
- `groesst: Tuple[float, float]`

#### Extrem.massgebend

```python
@property
def massgebend(self) -> Tuple[float, float]
```

Der der beiden, der massgebend ist ([[opencivil.stabwerk.verlauf#massgebender|massgebender]]).

### extremwerte

```python
def extremwerte(teile: Sequence[Any], polynom: Callable[[Any], Polynom]) -> Extrem
```

Kleinster und groesster Wert eines Polynoms je Stueck `x0` bis `x1`,
bei gleichen Werten an der vordersten Stelle ([[opencivil.stabwerk.verlauf#vorderste_extreme|vorderste_extreme]])
– fuer die Staebe und die Durchlauftraeger der Decke. Bis 2026-11-20 hatte nur
die Decke diese Regel, und ein Stab, der sich nirgends biegt, nannte fuer
seine Durchbiegung 0.00 mm eine Stelle, die vom Rauschen abhing.

### _kandidaten

```python
def _kandidaten(teile: Sequence[Any], polynom: Callable[[Any], Polynom]) -> List[Tuple[float, float]]
```

`(x, Wert)` an den Grenzen jedes Stuecks und wo es flach ist – nach `x` geordnet.

### Grenzwert

```python
@dataclass(frozen=True)
class Grenzwert
```

Ein Wert ueber alle Staebe eines Falls: an welchem Stab, wo darauf und wie gross.

- `stab: str`
- `x: float`
- `wert: float`

### Grenzwerte

```python
@dataclass(frozen=True)
class Grenzwerte
```

Der kleinste, der groesste und der massgebende Wert einer Groesse ueber alle Staebe.

- `kleinst: Grenzwert`
- `groesst: Grenzwert`
- `massgebend: Grenzwert`

### grenzwerte

```python
def grenzwerte(extreme: Mapping[str, Extrem]) -> Grenzwerte
```

Aus den Extremwerten je Stab die ueber alle: der kleinste, der groesste
und der massgebende ([[opencivil.stabwerk.verlauf#Extrem.massgebend|Extrem.massgebend]]) – bei gleichem Wert,
auch bis auf Rundung, der des ersten Stabs.

### Stabverlauf

```python
@dataclass
class Stabverlauf
```

Ein Stab von Anfang bis Ende – ueber alle seine Teilstaebe.

- `stab: str`
- `L: float`
- `anfang: Vektor`
- `achsen: Tuple[Vektor, Vektor, Vektor]`
- `intervalle: List[Intervall] = field(default_factory=list)`

#### Stabverlauf.bei

```python
def bei(self, x: float, links: bool=False) -> Dict[str, float]
```

Die Werte an der Stelle `x` – an einer Sprungstelle rechts davon,
mit `links` links davon.

#### Stabverlauf.sehne

```python
def sehne(self, groesse: str) -> Polynom
```

Die Gerade zwischen den Werten von `v` oder `w` an den Stabenden.

#### Stabverlauf.proben

```python
def proben(self, je_stab: int=24) -> List[Dict[str, float]]
```

Werte zum Zeichnen: an beiden Seiten jeder Grenze und dazwischen so
dicht, dass ein Stab rund `je_stab` Stuecke hat.

#### Stabverlauf.extremstellen

```python
def extremstellen(self) -> List[float]
```

Wo eine Schnittgroesse im Innern eines Stuecks extrem ist.

#### Stabverlauf.extrem

```python
def extrem(self, groesse: str) -> Extrem
```

Kleinster und groesster Wert einer Groesse mit Stelle: einer
Schnittgroesse, einer Verschiebung oder Verdrehung oder von `f_y`
und `f_z`, der Durchbiegung gegen die Sehne.

#### Stabverlauf.groesste_verschiebung

```python
def groesste_verschiebung(self) -> Tuple[float, float]
```

Wo sich der Stab am weitesten verschiebt, und wie weit, in m – ``(x,
Betrag)`. Gesucht am Quadrat `u² + v² + w²``, einem Polynom;
verglichen am Betrag, damit die Rundung in m zaehlt und nicht in m².

### verlaeufe

```python
def verlaeufe(fall) -> Dict[str, Stabverlauf]
```

Je Stab sein Verlauf in diesem Fall – aus den Teilstaeben, der Reihe nach.

### ebener_verlauf

```python
def ebener_verlauf(*, L: float, x0: float, s: Sequence[float], d: Sequence[float], lasten: Sequence[st.Teillast], EA: float=0.0, EI: float=0.0, k_quer: Tuple[float, float]=(0.0, 0.0), k_laengs: float=0.0, laengs: bool=True, biegung: bool=True) -> List[EbenesIntervall]
```

Die Intervalle eines ebenen Teils der Laenge `L`, in x ab dem Anfang
seines Stabs (`x0`) – aus den Kraeften `s` und Verschiebungen `d`
seiner Enden und seinen Lasten. `EA` gilt nur, wenn er sich dehnt
(`laengs`), `EI` nur, wenn er sich biegt (`biegung`): sonst bleiben
`u` und `theta` die des Anfangs. Die Bettung quer `k_quer` am
Anfang und am Ende, dazwischen linear ([[opencivil.stabwerk.stab#bettung|bettung]]).

### _zusammen

```python
def _zusammen(z: EbenesIntervall, y: EbenesIntervall, t: EbenesIntervall) -> Intervall
```

Die drei ebenen Teile eines Stuecks als eines – mit der Zuordnung aus [[opencivil.stabwerk3d.stab|stab]].

### _hermite

```python
def _hermite(L: float, v1: float, t1: float, v2: float, t2: float) -> Polynom
```

Die kubische Biegelinie aus den Enden – die Form, mit der die Bettung
gerechnet wurde ([[opencivil.stabwerk.stab#formfunktionen|formfunktionen]]), nach
Potenzen von x geordnet.

### _verschoben

```python
def _verschoben(i: EbenesIntervall, um: float) -> EbenesIntervall
```

Dasselbe Intervall in x ab dem Anfang des ganzen Stabs.

### _schieben

```python
def _schieben(p: Polynom, um: float) -> Polynom
```

`q(x) = p(x - um)` – nach Horner, `(…(k_n·(x − um) + k_{n−1})·(x − um) + …)`.


## Konstanten

- `SCHNITTGROESSEN = ('N', 'V_y', 'V_z', 'T', 'M_y', 'M_z')` – Die Schnittgroessen eines Stabs – ihre Extremstellen kommen in die Proben.
- `POLYNOME = SCHNITTGROESSEN + ('u', 'v', 'w', 'theta_x', 'theta_y', 'theta_z')` – Was ein Intervall als Polynom traegt, ausser den Lasten.
- `IN_DER_EBENE = {'N': 'N', 'V': 'V_z', 'M': 'M_y', 'w': 'f_z', 'phi': 'theta_y'}` – In der Ebene heissen die Groessen eines Stabs wie von Hand – je Zeichen sein Feld im Verlauf: z liegt auf der gestrichelten Faser, y steht senkrecht auf der Ebene.
- `NULL = Polynom((0.0,))`
- `Ort = TypeVar('Ort')` – Wo ein Wert liegt: `x` laengs eines Stabs, ein Stab ueber alle, `s` laengs eines Durchlauftraegers der Decke, ein Punkt ihrer Platte.

## Braucht

- [[opencivil.stabwerk.stab]]
- [[opencivil.stabwerk3d.raum]]
- [[opencivil.stabwerk3d.stab]]

## Gebraucht von

- [[opencivil.decke.durchlauftraeger]]
- [[opencivil.decke.feld]]
- [[opencivil.decke.herleitung]]
- [[opencivil.decke.rechnung]]
- [[opencivil.decke.schnitt]]
- [[opencivil.pfahl.bettung]]
- [[opencivil.stabwerk.herleitung]]
- [[opencivil.stabwerk.rechnung]]
- [[opencivil.stabwerk.stellen]]
- [[opencivil.stabwerk3d.herleitung]]
- [[opencivil.web.balkendaten]]
