---
erzeugt: 10412730438a
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
* je Beanspruchung -- Druck, Biegung zu einer Seite oder ein Lastfall -- den
  Zustand jedes Blechs, plastisch `α` und elastisch `ψ`, je an einer
  Nulllinie ([[opencivil.querschnitt.plastisch#Linie|Linie]]), und daraus seine Klasse
  ([[opencivil.stahlbau.klasse]]);
* den Querschnitt starr-plastisch, je Gruppe `±f`
  ([[opencivil.stahlbau.querschnitt#Stahlquerschnitt.starr|Stahlquerschnitt.starr]]) -- gerechnet wird in
  [[opencivil.querschnitt.plastisch]] --, die elastischen Werte und den
  wirksamen Querschnitt der Klasse 4.

Was ein Lastfall daraus macht, steht in [[opencivil.stahlbau.widerstand]].


## DIE TEILE

Ein Polygon zaehlt in seiner Gruppe mit +1 und in der seines Elternteils mit
-1 ([[opencivil.querschnitt.plastisch#stuecke|stuecke]]): so nimmt eine
Aussparung den Stahl darum weg, und ein Polygon aus anderem Stahl ersetzt ihn
dort. Ein Polygon aus anderem Werkstoff -- im Verbund der Beton -- ist fuer
den Stahl eine Aussparung. Mit einem Gewicht dazwischen faellt ein Teil eines
Blechs nur anteilig weg: so mindert die Querkraft den Steg
([[opencivil.stahlbau.querschnitt#Stahlquerschnitt.mit|Stahlquerschnitt.mit]]). Die Dicke eines Profils ist die seines dicksten
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

### normale

```python
def normale(seite: Zugseite) -> Tuple[float, float]
```

Die Richtung zur gezogenen Seite -- genau 0 oder ±1.

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
- `frei_plastisch: bool = False` – Ob der freie Rand plastisch der staerker gedrueckte ist -- fuer die Grenzen mit `α`.
- `tabelle: str = ''` – Wo die Grenzen stehen, wenn nicht in der Tabelle der Halterung -- beim kammerbetonierten Blech im Verbund ([[opencivil.verbund.querschnitt]]).

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

- `n: Tuple[float, float]`
- `v: float` – `n·S` -- wo die Nulllinie bei `N = 0` liegt, durch den Schwerpunkt `S`.
- `I: float`
- `A: float`
- `abstaende: Tuple[float, ...]` – Je Gruppe der weiteste Punkt ihres Stahls von der Nulllinie -- 0 ohne Stahl.
- `schwerpunkt: Punkt`

#### Elastisch.linie

```python
@property
def linie(self) -> Linie
```

Die Nulllinie bei `N = 0`, durch den Schwerpunkt.

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

#### Stahlquerschnitt.mit

```python
def mit(self, zusatz: Sequence[Stueck]) -> 'Stahlquerschnitt'
```

Derselbe Querschnitt mit weiteren Stuecken: ein Streifen mit negativem
Gewicht nimmt so viel Stahl weg -- ein Blech der Klasse 4 ganz, die
Querkraft anteilig. Teile und Bleche bleiben, wie gezeichnet.

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

#### Stahlquerschnitt.werte

```python
def werte(self) -> geo.Flaechenwerte
```

Flaeche, Schwerpunkt und Traegheitsmomente des Stahls -- alle Staehle haben dasselbe `E`.

#### Stahlquerschnitt.starr

```python
def starr(self, f: Sequence[float]) -> Starrplastisch
```

Der Querschnitt starr-plastisch: je Gruppe `f` gezogen und `-f` gedrueckt.

#### Stahlquerschnitt.plastisch

```python
def plastisch(self, n: Tuple[float, float], v: float) -> List[float]
```

Je Gruppe `∫|n·p - v| dA` in mm³ -- ihr Anteil am plastischen
Widerstandsmoment um die Nulllinie `v`.

#### Stahlquerschnitt.elastisch

```python
def elastisch(self, n: Tuple[float, float]) -> Elastisch
```

Der Querschnitt elastisch, quer zu `n` -- alle Staehle haben dasselbe `E`.

#### Stahlquerschnitt.zustaende

```python
def zustaende(self, pl: Linie, el: Optional[Linie], eps: Sequence[float]) -> List[Blechzustand]
```

Jedes Blech jedes Profils, plastisch an der Nulllinie `pl`,
elastisch an `el` -- mit `ε` je Gruppe. Ohne `el` gilt keine
Grenze der Klasse 3: so fragt der Verbund nur, ob ein Blech die
Klasse 1 oder 2 haelt ([[opencivil.verbund.querschnitt]]).

#### Stahlquerschnitt.freie_gedrueckt

```python
def freie_gedrueckt(self, pl: Linie, el: Optional[Linie]) -> List[Teil]
```

Die freien Flaechen, die plastisch oder elastisch gedrueckt sind -- siehe Dateikopf.

#### Stahlquerschnitt.wirksamer

```python
def wirksamer(self, zustaende: Sequence[Blechzustand], el: Linie, eps: Sequence[float], rest: Callable[[Blechzustand], float]=lambda zustand: 1.0) -> Optional[Tuple[List[Wirksam], 'Stahlquerschnitt']]
```

Der wirksame Querschnitt zu diesen Zustaenden (4.5.3): die
mitwirkenden Breiten der Bleche in Klasse 4 und der Querschnitt ohne
ihre Streifen -- `None` mit einem Rundrohr darunter (siehe
Dateikopf). `rest` sagt je Blech, wie viel von ihm noch zaehlt: hat
die Querkraft schon einen Teil genommen, nimmt sein Streifen nur den
Rest.

#### Stahlquerschnitt.wirksam

```python
def wirksam(self, zustand: Blechzustand, el: Linie, eps: float) -> Wirksam
```

Die mitwirkende Breite eines Blechs der Klasse 4 -- kein Rundrohr --,
ueber seine theoretische Breite `b`, mit `ψ` ueber dieselbe, an der
elastischen Nulllinie `el`. Siehe Dateikopf.

### _frei

```python
def _frei(blech: Blech, linie: Linie) -> bool
```

Ob der freie Rand eines einseitig gehaltenen Blechs an dieser Nulllinie der staerker gedrueckte ist.

### _rohr_innen

```python
def _rohr_innen(blech: Blech, linie: Linie) -> float
```

Wie weit der gedrueckteste Punkt eines Rundrohrs auf der gezogenen Seite liegt.

### _plastisch_gedrueckt

```python
def _plastisch_gedrueckt(blech: Blech, linie: Linie) -> Tuple[float, bool]
```

`α` an der plastischen Nulllinie und ob der freie Rand gedrueckt ist. Ein
Rundrohr ist gedrueckt, sobald ein Teil von ihm auf der gedrueckten Seite
liegt; seine Grenze haengt an nichts sonst.

### _elastisch_gedrueckt

```python
def _elastisch_gedrueckt(blech: Blech, linie: Linie) -> Tuple[Optional[float], bool]
```

`ψ` an der elastischen Nulllinie -- `None`, wo nichts gedrueckt ist -- und ob der freie Rand es ist.


## Konstanten

- `DICK_AB = 40.0` – Ab welcher Dicke die rechte Spalte von Tabelle 1 gilt, in mm.
- `TOLERANZ = 0.001` – Wie nah an einer Nulllinie ein Punkt auf ihr liegt, in mm.

## Braucht

- [[opencivil.material.basis]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.geometrie]]
- [[opencivil.querschnitt.plastisch]]
- [[opencivil.querschnitt.zugseite]]
- [[opencivil.stahlbau.klasse]]
- [[opencivil.stahlprofile.bleche]]

## Gebraucht von

- [[opencivil.nachweis.qa_stahl]]
- [[opencivil.nachweis.qa_stahl_kennzahlen]]
- [[opencivil.nachweis.qa_stahl_stabilitaet]]
- [[opencivil.nachweis.qa_stahl_werte]]
- [[opencivil.nachweis.qa_verbund_kennzahlen]]
- [[opencivil.nachweis.qa_verbund_werte]]
- [[opencivil.stahlbau.stabilitaet]]
- [[opencivil.stahlbau.widerstand]]
- [[opencivil.verbund.querschnitt]]
- [[opencivil.verbund.widerstand]]
