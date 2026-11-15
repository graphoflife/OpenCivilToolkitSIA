---
erzeugt: 7f82e48c398e
art: modul
tags: [modul]
---
> [!abstract] opencivil/stabwerk3d/verlauf.py
> Schnittgroessen und Biegelinien laengs eines Stabs im Raum.
> Paket [[opencivil.stabwerk3d]] · [Quelltext](../../opencivil/stabwerk3d/verlauf.py)

## VERANTWORTUNG

Wie [[opencivil.stabwerk.verlauf]], im Raum: aus dem, was
[[opencivil.stabwerk3d.system|system]] an den Enden jedes Teilstabs findet,
und aus seinen Lasten die Verlaeufe dazwischen -- je Teil des Stabs einmal
mit [[opencivil.stabwerk.verlauf#ebener_verlauf|ebener_verlauf]], dann
zusammengesetzt ([[opencivil.stabwerk3d.stab|stab]]). Die drei Teile
springen an denselben Stellen, weil jede Last in allen dreien steht.

VORZEICHEN -- M_z NACH VORGABE, NICHT NACHGESCHLAGEN:
In den Achsen des Stabs. `N > 0` ist Zug, `T > 0` dreht im Rechtssinn
um die nach aussen zeigende Normale des Schnitts. `M_y > 0` zieht an der
Faser auf der Seite +z, `M_z > 0` an der auf der Seite +y: beide Ebenen
wie die des 2D-Balkensystems, mit `V_z = dM_y/dx` und `V_y = dM_z/dx`,
wo kein verteiltes Moment liegt. Die Spannung im Querschnitt ist damit
`σ = N/A + M_y·z/I_y + M_z·y/I_z`; die Rechtsschraube gaebe `M_z` das
andere Vorzeichen.

Verschiebungen `u`, `v`, `w` in x, y und z des Stabs, Verdrehungen
`theta_x`, `theta_y`, `theta_z` im Rechtssinn um diese Achsen; dazu
`ux`, `uy`, `uz` in den Achsen des Systems und die Durchbiegungen
`f_y` und `f_z` gegen die Sehne zwischen den Stabenden.

## Inhalt

### Intervall

```python
@dataclass
class Intervall
```

Ein Stueck eines Stabs ohne Laststelle -- alles darauf Polynome in x ab dem Stabanfang.

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

### _zusammen

```python
def _zusammen(z: EbenesIntervall, y: EbenesIntervall, t: EbenesIntervall) -> Intervall
```

Die drei ebenen Teile eines Stuecks als eines -- mit der Zuordnung aus [[opencivil.stabwerk3d.stab|stab]].

### Stabverlauf

```python
@dataclass
class Stabverlauf
```

Ein Stab von Anfang bis Ende -- ueber alle seine Teilstaebe.

- `stab: str`
- `L: float`
- `anfang: Vektor`
- `achsen: Tuple[Vektor, Vektor, Vektor]`
- `intervalle: List[Intervall] = field(default_factory=list)`

#### Stabverlauf.bei

```python
def bei(self, x: float, links: bool=False) -> Dict[str, float]
```

Die Werte an der Stelle `x` -- an einer Sprungstelle rechts davon,
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

### verlaeufe

```python
def verlaeufe(fall) -> Dict[str, Stabverlauf]
```

Je Stab sein Verlauf in diesem Fall -- aus den Teilstaeben, der Reihe nach.


## Konstanten

- `SCHNITTGROESSEN = ('N', 'V_y', 'V_z', 'T', 'M_y', 'M_z')` – Die Schnittgroessen -- ihre Extremstellen kommen in die Proben.
- `POLYNOME = SCHNITTGROESSEN + ('u', 'v', 'w', 'theta_x', 'theta_y', 'theta_z')` – Was ein Intervall als Polynom traegt, ausser den Lasten.

## Braucht

- [[opencivil.stabwerk.verlauf]]
- [[opencivil.stabwerk3d.raum]]
- [[opencivil.stabwerk3d.stab]]
