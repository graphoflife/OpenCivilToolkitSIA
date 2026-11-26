---
erzeugt: 47fba6e3de2b
art: modul
tags: [modul]
---
> [!abstract] opencivil/stahlbau/querschnitt.py
> ein gezeichneter Querschnitt aus Baustahl.
> Paket [[opencivil.stahlbau]] · [Quelltext](../../opencivil/stahlbau/querschnitt.py)

## VERANTWORTUNG

Was die Kennzahlen eines Stahlquerschnitts
([[opencivil.nachweis.qa_stahl_kennzahlen]]) aus der Zeichnung brauchen,
ohne Rechenwerk und ohne Herleitung, in mm und N/mm²:

* die Teile, nach Baustahl und Dicke in Gruppen -- je Gruppe eine
  Fliessgrenze ([[opencivil.stahlbau.querschnitt#Gruppe|Gruppe]]);
* je Beanspruchung -- Druck oder Biegung zu einer Seite -- den Zustand jedes
  Blechs, plastisch `α` und elastisch `ψ`, und daraus seine Klasse
  ([[opencivil.stahlbau.klasse]]);
* die plastische Nulllinie und das plastische Moment, die elastischen Werte
  und den wirksamen Querschnitt der Klasse 4.


## DIE TEILE

Ein Polygon zaehlt in seiner Gruppe mit +1 und in der seines Elternteils mit
-1: so nimmt eine Aussparung den Stahl darum weg, und ein Polygon aus anderem
Stahl ersetzt ihn dort. Die Dicke eines Profils ist die seines dicksten
Blechs, die einer frei gezeichneten Flaeche ihre kleinste Breite -- die ihrer
konvexen Huelle. Nach Vorgabe, nicht nachgeschlagen: das ganze Profil
rechnet so mit der Fliessgrenze seines dicksten Blechs, und eine freie
Flaeche nie mit einer zu grossen. Ueber 40 mm gelten die Werte der rechten
Spalte von Tabelle 1, auch ueber 100 mm, wo die Tabelle endet.


## HAUPTACHSEN

y und z gelten als Hauptachsen, wie im Balkensystem
([[opencivil.stabwerk.stabquerschnitt#Konstanten|KOPPLUNG]]): die Nulllinie einer
Biegung um y liegt waagrecht, plastisch wie elastisch.


## FREIE FLAECHEN

Wie ein frei gezeichnetes Blech gehalten ist, weiss das Werkzeug nicht. Wo
eines gedrueckt ist, rechnet der Querschnitt darum hoechstens elastisch, in
Klasse 3, ohne sein Beulen zu pruefen (Plan vom 2026-11-25, Punkt 7).


## DIE WIRKSAME BREITE

(4.5.3), IN EINEM SCHRITT
Je Blech der Klasse 4 faellt ein Streifen weg, so dick wie das Blech, aus
der gedrueckten Zone `b_c` seiner theoretischen Breite, wie Tabelle 10 ihn
legt: beim beidseitig gestuetzten in der Mitte, sodass je `b_eff/2` an
den Enden der Zone bleiben; beim einseitig gestuetzten am freien Ende,
sodass `b_eff` am gehaltenen bleibt -- Tabelle 10 zeigt das nur fuer
gleichmaessigen Druck (nach Vorgabe, nicht nachgeschlagen). `ψ` kommt aus
den Spannungen des Bruttoquerschnitts; dass die Nulllinie des wirksamen
sich verschiebt, aendert die Streifen nicht mehr (nach Vorgabe, nicht
nachgeschlagen). Ein Rundrohr hat keine mitwirkende Breite: in Klasse 4
rechnet das Werkzeug es nicht.

## Inhalt

### Gruppe

```python
@dataclass(frozen=True)
class Gruppe
```

Ein Baustahl in einer Dicke: alle Teile, die mit derselben Fliessgrenze rechnen.

- `stoff: Baustoff`
- `dick: bool`

#### Gruppe.name

```python
@property
def name(self) -> str
```

#### Gruppe.kennwert

```python
def kennwert(self, kurz: str) -> str
```

Der Kennwert in dieser Dicke: `f_y` oder `f_y_dick`.

### Teil

```python
@dataclass(frozen=True)
class Teil
```

Ein Polygon aus Baustahl, mit seiner Dicke -- ein Profil mit seinen Blechen.

- `flaeche: Flaechenteil`
- `gruppe: int`
- `dicke: float`
- `netto: float` – Seine Flaeche in mm², ohne was in ihm liegt.
- `bleche: Tuple[Blech, ...]`

#### Teil.name

```python
@property
def name(self) -> str
```

### Stueck

```python
@dataclass(frozen=True)
class Stueck
```

Ein Polygon mit Vorzeichen in einer Gruppe -- siehe Dateikopf.

- `gruppe: int`
- `vorzeichen: float`
- `punkte: Tuple[Punkt, ...]`

### Blechzustand

```python
@dataclass(frozen=True)
class Blechzustand
```

Wie ein Blech unter einer Beanspruchung gedrueckt ist und in welche Klasse
es damit faellt -- gemessen ueber `c`: `alpha` der plastisch
gedrueckte Anteil, `psi` das Verhaeltnis der elastischen Spannungen
(`None`: elastisch nicht gedrueckt), `frei` ob der freie Rand der
staerker gedrueckte ist.

- `teil: Teil`
- `blech: Blech`
- `alpha: float`
- `psi: Optional[float]`
- `frei: bool`
- `grenzen: kl.Grenzen`
- `klasse: int`

#### Blechzustand.name

```python
@property
def name(self) -> str
```

#### Blechzustand.schlankheit

```python
@property
def schlankheit(self) -> float
```

### Wirksam

```python
@dataclass(frozen=True)
class Wirksam
```

Die mitwirkende Breite eines Blechs der Klasse 4 -- in mm, ueber seine theoretische Breite.

- `zustand: Blechzustand`
- `psi: float`
- `k: float`
- `lambda_p: float`
- `rho: float`
- `b_c: float`
- `streifen: Optional[Tuple[Punkt, ...]]` – Was wegfaellt -- `None`, wo das ganze Blech mitwirkt.

#### Wirksam.b_eff

```python
@property
def b_eff(self) -> float
```

### Elastisch

```python
@dataclass(frozen=True)
class Elastisch
```

Ein Querschnitt elastisch, quer zu einer Richtung `n`: in mm und mm⁴.

- `v: float` – `n·S` -- wo die Nulllinie bei `N = 0` liegt, durch den Schwerpunkt `S`.
- `I: float`
- `A: float`
- `abstaende: Tuple[float, ...]` – Je Gruppe der weiteste Punkt ihres Stahls von der Nulllinie -- 0 ohne Stahl.
- `schwerpunkt: Punkt`

#### Elastisch.moment

```python
def moment(self, f: Sequence[float]) -> Tuple[float, int]
```

Das Moment, bei dem die erste Faser die Spannung ihrer Gruppe erreicht,
in N·mm, und die Gruppe, in der sie liegt: `min f_g I/z_g`.

### kleinste_breite

```python
def kleinste_breite(punkte: Sequence[Punkt]) -> float
```

Die kleinste Breite eines Polygons -- die seiner konvexen Huelle, quer zu einer ihrer Kanten.

### _huelle

```python
def _huelle(punkte: Sequence[Punkt]) -> List[Punkt]
```

Die konvexe Huelle, linksherum (Andrew).

### _null

```python
def _null(d: float) -> float
```

Eine Entfernung von der Nulllinie -- null, wo sie auf ihr liegt.

### anteil

```python
def anteil(d_1: float, d_2: float) -> float
```

Der gedrueckte Anteil einer Strecke, deren Enden `d` von der Nulllinie liegen -- gedrueckt, wo `d < 0`.

### verhaeltnis

```python
def verhaeltnis(d_1: float, d_2: float) -> Optional[float]
```

`ψ` ueber eine Strecke: die Spannung am anderen Ende durch die am staerker gedrueckten -- `None` ohne Druck.

### Stahlquerschnitt

```python
class Stahlquerschnitt
```

Die Polygone einer Querschnittsanalyse aus Baustahl -- siehe Dateikopf.

#### Stahlquerschnitt.profile

```python
@property
def profile(self) -> List[Teil]
```

#### Stahlquerschnitt.freie

```python
@property
def freie(self) -> List[Teil]
```

Die frei gezeichneten Flaechen aus Baustahl -- siehe Dateikopf.

#### Stahlquerschnitt.flaechen

```python
def flaechen(self) -> List[float]
```

Je Gruppe ihre Flaeche in mm².

#### Stahlquerschnitt.nulllinie

```python
def nulllinie(self, n: Tuple[float, float], f: Sequence[float]) -> float
```

Die plastische Nulllinie `n·p = v` bei `N = 0`: so viel Kraft
gezogen wie gedrueckt, je Gruppe mit `f`. Halbiert, bis sie auf
1e-9 mm genau liegt.

#### Stahlquerschnitt.plastisch

```python
def plastisch(self, n: Tuple[float, float], v: float) -> List[float]
```

Je Gruppe `∫|n·p - v| dA` in mm³ -- ihr Anteil am plastischen
Widerstandsmoment um die Nulllinie `v`.

#### Stahlquerschnitt.elastisch

```python
def elastisch(self, n: Tuple[float, float], abzug: Sequence[Tuple[int, Tuple[Punkt, ...]]]=()) -> Elastisch
```

Der Querschnitt elastisch, ohne die Streifen in `abzug` (je Gruppe
und Umriss) -- alle Staehle haben dasselbe `E`.

#### Stahlquerschnitt.zustaende

```python
def zustaende(self, n: Normale, eps: Sequence[float], v_pl: float=0.0, v_el: float=0.0) -> List[Blechzustand]
```

Jedes Blech jedes Profils unter Druck (`n` `None`) oder unter
Biegung mit den Nulllinien `v_pl` und `v_el` -- mit `ε` je Gruppe.

#### Stahlquerschnitt.freie_gedrueckt

```python
def freie_gedrueckt(self, n: Normale, v_pl: float=0.0, v_el: float=0.0) -> List[Teil]
```

Die freien Flaechen, die plastisch oder elastisch gedrueckt sind -- siehe Dateikopf.

#### Stahlquerschnitt.wirksam

```python
def wirksam(self, zustand: Blechzustand, n: Normale, eps: float, v_el: float=0.0) -> Wirksam
```

Die mitwirkende Breite eines Blechs der Klasse 4 -- kein Rundrohr --,
ueber seine theoretische Breite `b`, mit `ψ` ueber dieselbe. Siehe
Dateikopf.


## Konstanten

- `DICK_AB = 40.0` – Ab welcher Dicke die rechte Spalte von Tabelle 1 gilt, in mm.
- `TOLERANZ = 0.001` – Wie nah an einer Nulllinie ein Punkt auf ihr liegt, in mm.
- `Normale = Optional[Tuple[float, float]]` – Eine Richtung, zur gezogenen Seite hin -- `None` bei gleichmaessigem Druck.

## Braucht

- [[opencivil.material.basis]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.geometrie]]
- [[opencivil.stahlbau.klasse]]
- [[opencivil.stahlprofile.bleche]]

## Gebraucht von

- [[opencivil.nachweis.qa_stahl_kennzahlen]]
