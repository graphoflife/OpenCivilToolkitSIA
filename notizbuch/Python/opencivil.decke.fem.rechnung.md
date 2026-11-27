---
erzeugt: b0294d7f6175
art: modul
tags: [modul]
---
> [!abstract] opencivil/decke/fem/rechnung.py
> die FEM der Decke, Fall für Fall.
> Paket [[opencivil.decke.fem]] · [Quelltext](../../opencivil/decke/fem/rechnung.py)

## VERANTWORTUNG

Die Decke einmal vernetzt ([[opencivil.decke.fem.netz|netz]]) und ihr System
einmal zerlegt ([[opencivil.decke.fem.system|system]]); dann je Lastfall die
Lasten auf den Knoten ([[opencivil.decke.fem.belastung|belastung]]) und je
Kombination ihre Summe mit den Beiwerten – die Platte ist linear. Je Fall:

1. die Verschiebungen `(w, β_x, β_y)` je Knoten;
2. die Momente jedes Dreiecks an seinen Ecken, an den Knoten geglättet
   ([[opencivil.decke.fem.glaetten|glaetten]]);
3. die Querkräfte aus dem Gefälle der geglätteten Momente, je Dreieck
   `v_x = ∂m_x/∂x + ∂m_xy/∂y` und `v_y = ∂m_xy/∂x + ∂m_y/∂y`, ebenso
   geglättet;
4. was die Lager tragen, aus `K·u − f` an ihren Knoten;
5. Moment und Querkraft jedes Balkenstücks eines Trägers.

Am Ende die Probe wie in der Streifenmethode: alle Lagerkräfte zusammen
sind die Last, ohne was neben den Platten liegt oder auf einem Teil, der
sich frei bewegen könnte.


## LÄNGS EINES LINIENLAGERS

Zu jedem Knoten gehört das Stück des Lagers bis zur Mitte der Kanten
daneben, und was er trägt, verteilt sich gleichmässig darüber: `r = F/l`.
Hält das Lager die Drehung, ist `m` ebenso das Moment, das der Knoten
hält, je Meter – mit dem Vorzeichen der Platte wie in der Streifenmethode:
dem der Seite, die stärker zieht ([[opencivil.decke.rechnung#gehalten|gehalten]]).
Liegen mehrere Lager an einem Knoten, teilen sie ihn nach der Länge ihrer
Stücke; steht eine Stütze darauf, trägt sie ihn allein.

## Inhalt

### Femwerte

```python
@dataclass(frozen=True)
class Femwerte(Schnittkraefte)
```

An einer Ecke: die Schnittkräfte wie in der Streifenmethode und die Durchbiegung `w` in m, nach unten.

- `w: float = 0.0`

#### Femwerte.groesse

```python
def groesse(self, name: str) -> float
```

Die Grösse `name` aus [[opencivil.decke.fem.rechnung#Konstanten|GROESSEN]].

### Balkenwerte

```python
@dataclass(frozen=True)
class Balkenwerte
```

Ein Stück eines Trägers als Balken, von `u_p` bis `u_q` m ab seinem
Anfang: die Momente an seinen Enden in Nm, positiv mit Zug unten, und
die Querkraft `V = dM/du` in N dazwischen.

- `u_p: float`
- `u_q: float`
- `M_p: float`
- `M_q: float`
- `V: float`

### Femfall

```python
@dataclass
class Femfall(Fall)
```

Ein Lastfall oder eine Kombination nach der FEM.

- `name: str`
- `summe: float` – Die ganze Last, in N.
- `daneben: float` – Was davon neben den Platten liegt.
- `nicht_getragen: float = 0.0` – Was auf Teilen liegt, die sich frei bewegen könnten.
- `verschiebungen: List[Tuple[float, float, float]] = field(default_factory=list)` – Je Knoten `(w, β_x, β_y)` in m und rad.
- `sektoren: List[Femwerte] = field(default_factory=list)` – Je Sektor der Glättung ([[opencivil.decke.fem.glaetten#Glaettung|Glaettung]]) seine Werte.
- `ecken: List[Tuple[Femwerte, ...]] = field(default_factory=list)` – Je Dreieck die Werte an seinen drei Ecken – dazwischen linear.
- `stuetzen: Dict[str, float] = field(default_factory=dict)` – Je Stütze die Kraft nach unten auf sie, in N.
- `linienlager: Dict[str, Tuple[float, List[Stufe]]] = field(default_factory=dict)` – Je Linienlager die Kraft nach unten auf es, in N, und ihr Verlauf längs.
- `traeger: Dict[str, List[Balkenwerte]] = field(default_factory=dict)` – Je Träger mit Höhe seine Stücke als Balken, nach ihrer Stelle.
- `meldungen: List[Meldung] = field(default_factory=list)`

#### Femfall.stuetzenkraft

```python
def stuetzenkraft(self, name: str) -> float
```

#### Femfall.wandkraft

```python
def wandkraft(self, name: str) -> float
```

#### Femfall.lagerstufen

```python
def lagerstufen(self, lager: Linienlager) -> List[Stufe]
```

### Femergebnis

```python
@dataclass
class Femergebnis(Faelle)
```

Die Decke nach der FEM: ihre Fälle und Meldungen, dazu Netz, System,
Glättung und Raster – `None`, wenn eine Meldung die Rechnung aufhielt.

- `decke: Decke`
- `faelle: List[Femfall]`
- `meldungen: List[Meldung]`
- `netz: Optional[Netz] = None`
- `system: Optional[System] = None`
- `glaettung: Optional[Glaettung] = None`
- `raster: Optional[Raster] = None`

### rechnen

```python
def rechnen(decke: Decke) -> Femergebnis
```

Die Decke nach der FEM, je Lastfall und Kombination – oder, was dem im Weg steht.

### _weite_fuer

```python
def _weite_fuer(decke: Decke) -> float
```

Die kleinste Netzweite auf 5 cm genau, mit der das Netz etwa [[opencivil.decke.fem.rechnung#Konstanten|KNOTEN_HOECHSTENS]] Knoten hat.

### _daneben

```python
def _daneben(decke: Decke, netz: Netz) -> List[Meldung]
```

Was neben den Platten liegt und darum nichts trägt – grau, der Rest rechnet.

### _teile

```python
def _teile(decke: Decke, netz: Netz, system: System) -> List[Tuple[Set[int], Tuple[str, ...]]]
```

Je Teil, der sich frei bewegen könnte, seine Knoten und die Namen seiner Platten.

### _querkraft

```python
def _querkraft(d: Dreieck, momente: Sequence[Sequence[float]]) -> List[Tuple[float, float]]
```

`(v_x, v_y)` an den drei Ecken aus dem Gefälle der geglätteten Momente – im Dreieck gleich.

### _stuetzen

```python
def _stuetzen(heraus: Femfall, decke: Decke, netz: Netz, reste: Sequence[Sequence[float]], aus: Set[int]) -> Set[int]
```

Je Stütze die Kraft ihres Knotens – zurück: die Knoten, die Stützen tragen.

### _linienlager

```python
def _linienlager(heraus: Femfall, decke: Decke, netz: Netz, glaettung: Glaettung, reste: Sequence[Sequence[float]], ohne: Set[int]) -> None
```

Je Linienlager, was seine Knoten tragen, und wie es sich längs verteilt.

### _ausgleichen

```python
def _ausgleichen(werte: Sequence[Tuple[float, float]], innen: Sequence[bool], verbunden: Sequence[bool]) -> List[Tuple[float, float]]
```

Kraft und Moment der Knoten eines Lagers, ausgeglichen: jeder Knoten
mitten im Lager gibt je ein Viertel an seine Nachbarn, wenn sie auch
mitten im Lager liegen (`innen`) und ein Stück sie verbindet
(`verbunden[i]`: Knoten `i` und `i + 1`). Die Kräfte der Knoten
springen sonst von Knoten zu Knoten, je nachdem, wie viele Dreiecke an
ihnen hängen; die Summe bleibt. An den Enden, an Lücken und wo ein
anderes Lager anstösst, bleibt die Kraft, wo sie ist: dort greift eine
Kraft im Punkt an, etwa an der Ecke einer Platte (nach Vorgabe, nicht
nachgeschlagen).

### _seiten

```python
def _seiten(fall: Femfall, glaettung: Glaettung, netz: Netz, k: int, n: Tuple[float, float]) -> Tuple[float, float]
```

Das Moment der Platte quer zu einem Lager am Knoten `k`, `m_n` in
Nm/m, links – auf der Seite von `n` – und rechts: je das Mittel der
Sektoren auf dieser Seite, null, wo keine Platte ist.

### _luecken

```python
def _luecken(stufen: Sequence[Stufe], L: float) -> List[Stufe]
```

Die Stufen von 0 bis `L`: wo keine Platte ist – über ein Loch, neben den Platten –, null.

### _balken

```python
def _balken(system: System, u: Sequence[Tuple[float, float, float]]) -> Dict[str, List[Balkenwerte]]
```

Je Träger mit Höhe Moment und Querkraft seiner Stücke als Balken.


## Konstanten

- `KNOTEN_HOECHSTENS = 3000` – Mehr Knoten rechnet die Rechnung nicht: auf der Seite dauerte es zu lange (nach Vorgabe, nicht nachgeschlagen).
- `GROESSEN = {**feld.GROESSEN, 'w': 'w'}` – Was ein Bild der Platte in der FEM zeigen kann: die Grössen der Streifenmethode und die Durchbiegung.
- `Stufe = Tuple[float, float, float, float]` – Ein Stück längs eines Linienlagers: `(u_a, u_b, r, m)` wie [[opencivil.decke.rechnung#lagerverlauf|lagerverlauf]].

## Braucht

- [[opencivil.decke.feld]]
- [[opencivil.decke.fem.belastung]]
- [[opencivil.decke.fem.element]]
- [[opencivil.decke.fem.glaetten]]
- [[opencivil.decke.fem.netz]]
- [[opencivil.decke.fem.system]]
- [[opencivil.decke.geometrie]]
- [[opencivil.decke.lasten]]
- [[opencivil.decke.modell]]
- [[opencivil.decke.rechnung]]
- [[opencivil.decke.streifen]]
- [[opencivil.stabwerk.system]]

## Gebraucht von

- [[opencivil.decke.fem.auswertung]]
- [[opencivil.decke.fem.herleitung]]
- [[opencivil.decke.werk]]
- [[opencivil.projekt.decke]]
- [[opencivil.web.deckendaten]]
