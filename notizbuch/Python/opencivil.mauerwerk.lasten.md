---
erzeugt: d21a8d01d1ac
art: modul
tags: [modul]
---
> [!abstract] opencivil/mauerwerk/lasten.py
> wie die Lasten einer Wand zu ihren Pfeilern kommen.
> Paket [[opencivil.mauerwerk]] · [Quelltext](../../opencivil/mauerwerk/lasten.py)

## VERANTWORTUNG

Die lotrechten Lasten einer Wand – Linien- und Punktlasten mit ihrer
Ausmitte quer zur Wand, dazu ihr Eigengewicht – je Lastfall auf Pfeiler und
Stürze verteilt ([[opencivil.mauerwerk.lasten#abtragen|abtragen]]): je Pfeiler die Normalkraft an seinem Fuss,
die der Lasten allein und das Moment ihrer Ausmitten an seinem Kopf; je
Sturzauflager seine Kraft; und wie weit die Lasten in der Ebene der Wand
neben den Mitten der Pfeiler stehen, als ein Moment. Was in der Ebene der
Wand daraus wird und was die waagrechten Lasten dazugeben, rechnet
[[opencivil.mauerwerk.scheibe|scheibe]] in denselben Abtrag.
Eine Kombination summiert die Lastfälle mit ihren Beiwerten
([[opencivil.mauerwerk.lasten#kombinieren|kombinieren]]). Die Norm regelt das nicht; so rechnet das Werkzeug
(nach Vorgabe, nicht nachgeschlagen):

- Was über einem Pfeiler liegt, trägt er – auch sein eigenes Gewicht.
- Was über einer Öffnung liegt, trägt ihr Sturz: was über einem seiner
  Auflager liegt, ganz dieses; was über der Öffnung liegt, teilt er als
  einfacher Balken zwischen den Mitten seiner Auflager. Die Kraft eines
  Auflagers geht weiter nach unten, in den Pfeiler darunter oder auf den
  nächsten Sturz.
- Was unter einer Öffnung liegt, etwa eine Brüstung, geht neben den
  Pfeilern in den Fuss der Wand.
- Das Eigengewicht ist ρ · g · t_w je m² Wand, mit g = 10 m/s² wie überall
  im Werkzeug; ein Sturz wiegt wie Mauerwerk.
- Eine Last wirkt mit ihrer Ausmitte am Kopf der Pfeiler, die sie trägt,
  wo sie auch liegt; das Eigengewicht mittig. Die Ausmitte am Kopf ist
  darum die der Lasten allein, M / N_L: das Eigengewicht, das erst darunter
  dazukommt, verkleinert sie nicht.
- In der Ebene der Wand erreicht eine Last den Pfeiler, wo sie über ihm
  liegt, von einem Sturz in der Mitte seines Auflagers: ihr Hebel zur
  Mitte des Pfeilers, über alle Pfeiler summiert, ist das Moment M_v.

Die Lasten selbst beschreibt [[opencivil.mauerwerk.modell|modell]].


## EINHEITEN

SI: N, m und N·m; Druck positiv.

## Inhalt

### Abtrag

```python
@dataclass
class Abtrag
```

Was ein Fall den Pfeilern und Stürzen gibt: je Pfeiler die Normalkraft
am Fuss `N`, die der Lasten allein `N_L` und das Moment ihrer
Ausmitten `M`; je Sturzauflager `(Öffnung, Seite)` die Kraft `R`,
und was neben den Pfeilern in den Fuss geht (`unten`). In der Ebene
der Wand `M_v`, wie weit die Lasten neben den Mitten der Pfeiler
stehen, und je Pfeiler die Querkraft `V`, nach rechts positiv, was die
waagrechten Lasten zu seiner Normalkraft geben, `N_H` – schon in
`N` und `N_L` –, und das Moment an seinem Fuss `M_z`. Beide
Momente sind positiv, wenn sie die Resultierende nach rechts schieben.

- `N: Dict[str, float] = field(default_factory=dict)`
- `N_L: Dict[str, float] = field(default_factory=dict)`
- `M: Dict[str, float] = field(default_factory=dict)`
- `R: Dict[Tuple[str, str], float] = field(default_factory=dict)`
- `unten: float = 0.0`
- `M_v: float = 0.0`
- `V: Dict[str, float] = field(default_factory=dict)`
- `N_H: Dict[str, float] = field(default_factory=dict)`
- `M_z: Dict[str, float] = field(default_factory=dict)`

#### Abtrag.je_pfeiler

```python
def je_pfeiler(self) -> Tuple[Dict[str, float], ...]
```

Was je Pfeiler eine Zahl hat – die eine Liste, die [[opencivil.mauerwerk.lasten#kombinieren|kombinieren]] summiert.

### leer

```python
def leer(pfeiler: Sequence[Pfeiler], oeffnungen: Sequence[Oeffnung]) -> Abtrag
```

Ein Abtrag ohne Last: je Pfeiler und Auflager eine Null, damit jeder dasteht.

### kombinieren

```python
def kombinieren(name_faktoren: Mapping[str, float], je_fall: Mapping[str, Abtrag], pfeiler: Sequence[Pfeiler], oeffnungen: Sequence[Oeffnung]) -> Abtrag
```

Die Summe der Lastfälle mit ihren Beiwerten – `je_fall` nach dem Namen des Lastfalls.

### _Wand

```python
class _Wand
```

Die Wand, wie der Abtrag sie braucht: ihre Pfeiler und die Stürze über den Öffnungen.

#### _Wand.sturz_unter

```python
def sturz_unter(self, x0: float, x1: float, y: float) -> Optional[Tuple[Oeffnung, Rechteck]]
```

Der höchste Sturz unter `y`, der von `x0` bis `x1` ganz durchgeht, oder keiner.

#### _Wand.pfeiler_bei

```python
def pfeiler_bei(self, x0: float, x1: float) -> Optional[Pfeiler]
```

#### _Wand.stuecke

```python
def stuecke(self, last: Wandlast) -> List[Wandlast]
```

Eine Last, geteilt an den Grenzen – jedes Stück liegt ganz über einem Teil der Wand.

#### _Wand.mauerwerk

```python
def mauerwerk(self, je_m2: float) -> List[Wandlast]
```

Das Eigengewicht, in Stücken: je Streifen zwischen den Grenzen das
Mauerwerk zwischen Öffnungen und Sturzunterkanten, jedes als Last an
seiner Unterkante.

### abtragen

```python
def abtragen(flaeche: Rechteck, oeffnungen: Sequence[Oeffnung], pfeiler: Sequence[Pfeiler], lasten: Sequence[Wandlast], eigengewicht: float=0.0) -> Abtrag
```

Die Lasten eines Lastfalls auf Pfeiler und Stürze – `eigengewicht` in
N/m² der Wand, null ohne. Siehe Dateikopf.


## Konstanten

- `SEITEN = ('links', 'rechts')` – Die beiden Auflager eines Sturzes.

## Braucht

- [[opencivil.mauerwerk.modell]]

## Gebraucht von

- [[opencivil.mauerwerk.herleitung]]
- [[opencivil.mauerwerk.nachweise]]
- [[opencivil.mauerwerk.scheibe]]
- [[opencivil.mauerwerk.schub]]
- [[opencivil.mauerwerk.werk]]
- [[opencivil.projekt.aufbau.mauerwerk]]
