---
erzeugt: 4c791e96fc5b
art: modul
tags: [modul]
---
> [!abstract] opencivil/decke/rechnung.py
> die Streifenmethode, Fall für Fall.
> Paket [[opencivil.decke]] · [Quelltext](../../opencivil/decke/rechnung.py)

## VERANTWORTUNG

Die ganze Rechnung einer Decke: zerlegen ([[opencivil.decke.streifen|streifen]]),
die Last aufteilen ([[opencivil.decke.aufteilung|aufteilung]]), je Lastfall auf die
Streifen legen ([[opencivil.decke.lasten|lasten]]), und dann je Lastfall und
Kombination die Träger rechnen -- von unten nach oben:

1. die Feldstreifen (Stufe 0),
2. die Unterzüge, nach Stufe aufsteigend. Was ein Streifen in einen
   Unterzug gibt, liegt auf diesem als Last -- mit umgekehrtem Vorzeichen
   die Pressung, mit der dieser ihn trägt, über die Fläche, die beide
   teilen (Stahlbeton II, 7.2 Platten, Folie 33: die Pressung des
   Flächenlagers wird zur Last des versteckten Unterzugs).
3. Was in Linienlager und Stützen geht, sind die Lagerkräfte der Decke.

Am Ende eine Probe: alle Lagerkräfte zusammen sind die Last, abzüglich
dessen, was neben den Platten liegt oder auf einem Streifen, der nicht trägt.


## DIE LAGERKRÄFTE

Eine Stütze bekommt die Summe der Kräfte aller Träger auf ihr. Ein
Linienlager bekommt von jedem Träger, der es kreuzt, dessen Kraft --
gleichmässig verteilt über das Stück des Lagers, über das der Träger geht --
und bei Einspannung dessen Moment ebenso: ein Verlauf in kN/m und kNm/m
längs des Lagers, das Moment mit dem Vorzeichen der Platte
([[opencivil.decke.rechnung#lagerverlauf|lagerverlauf]]).

## Inhalt

### Lagerkraft

```python
@dataclass(frozen=True)
class Lagerkraft
```

Was ein Lager auf einen Träger ausübt: `F` nach oben in N, `C` im Gegenuhrzeigersinn in Nm.

- `auflager: Auflager`
- `F: float`
- `C: float`

### Traegerergebnis

```python
@dataclass
class Traegerergebnis
```

- `traeger: Traeger`
- `lasten: List[Teillast]` – Was auf ihm liegt, ohne seine Lagerkräfte -- in m ab seinem Anfang.
- `lagerkraefte: List[Lagerkraft]`
- `stuecke: List[Stueck]` – Querkraft und Moment längs des Trägers, für den ganzen Streifen (N, Nm).

#### Traegerergebnis.last

```python
@property
def last(self) -> float
```

Was auf ihm liegt, zusammen, in N.

#### Traegerergebnis.beidseits

```python
def beidseits(self, s: float) -> Tuple[float, float]
```

`M` knapp vor und knapp nach der Stelle `s`, in Nm -- vor seinem Anfang und nach seinem Ende null.

### Wandkraft

```python
@dataclass(frozen=True)
class Wandkraft
```

Was ein Träger in ein Linienlager gibt -- gleichmässig über das Stück `a → b`.

- `traeger: str`
- `a: Punkt`
- `b: Punkt`
- `F: float` – Nach unten auf das Lager, in N.
- `vor: float`
- `nach: float` – Hält das Lager die Drehung, das Moment des Trägers knapp vor und knapp nach ihm, in Nm, `M > 0` zieht unten -- vor seinem Anfang und nach seinem Ende null. Was das Lager hält, ist der Unterschied. Ein Lager, das die Drehung nicht hält, hält kein Moment: dann beide null.
- `n: Punkt` – Die Richtung des Trägers: in ihr liegt `nach` hinter dem Lager.

#### Wandkraft.laenge

```python
@property
def laenge(self) -> float
```

#### Wandkraft.r

```python
@property
def r(self) -> float
```

Die Kraft je Meter des Lagers, in N/m.

### Fallergebnis

```python
@dataclass
class Fallergebnis
```

- `name: str`
- `summe: float` – Die ganze Last, in N.
- `daneben: float` – Was davon neben den Platten liegt.
- `traeger: Dict[str, Traegerergebnis] = field(default_factory=dict)`
- `stuetzen: Dict[str, List[Tuple[str, float]]] = field(default_factory=dict)` – Je Stütze, was jeder Träger auf ihr in sie gibt, in N.
- `linienlager: Dict[str, List[Wandkraft]] = field(default_factory=dict)`
- `nicht_getragen: float = 0.0` – Was auf Trägern liegt, die nicht tragen.
- `meldungen: List[Meldung] = field(default_factory=list)`

#### Fallergebnis.stuetzenkraft

```python
def stuetzenkraft(self, name: str) -> float
```

#### Fallergebnis.wandkraft

```python
def wandkraft(self, name: str) -> float
```

#### Fallergebnis.lagerkraft

```python
@property
def lagerkraft(self) -> float
```

Alle Kräfte in Linienlager und Stützen zusammen.

#### Fallergebnis.fehlbetrag

```python
@property
def fehlbetrag(self) -> float
```

Was die Lager weniger tragen, als auf den Trägern liegt -- null bis auf Rundung.

### Ergebnis

```python
@dataclass
class Ergebnis
```

- `decke: Decke`
- `zerlegung: Zerlegung`
- `aufteilungen: Optional[Aufteilungen]`
- `faelle: List[Fallergebnis]`
- `meldungen: List[Meldung]`

#### Ergebnis.fall

```python
def fall(self, name: str) -> Fallergebnis
```

### rechnen

```python
def rechnen(decke: Decke) -> Ergebnis
```

Die Decke nach der Streifenmethode, je Lastfall und Kombination.

### fall

```python
def fall(name: str, belastung: Belastung, zerlegung: Zerlegung) -> Fallergebnis
```

Ein Lastfall oder eine Kombination: alle Träger, von den Feldstreifen zu den Unterzügen.

### auf_traeger

```python
def auf_traeger(streifen: Streifen, lasten: Sequence[Teillast]) -> List[Tuple[Traeger, List[Teillast]]]
```

Die Lasten eines Streifens (in `s` seiner Richtung) auf seine Träger,
in m ab deren Anfang. Was zwischen oder hinter den Trägern liegt -- an
einem schiefen Rand ein Zwickel --, kommt als Einzellast an das nächste
Ende.

### gegenkraefte

```python
def gegenkraefte(kraefte: Sequence[Lagerkraft]) -> List[Teillast]
```

Die Lagerkräfte als Lasten auf den Träger: ein Linienlager als Punkt, ein
Flächenlager als gleichmässige Pressung über seine Fläche -- nach oben,
also negativ.

### _weitergeben

```python
def _weitergeben(k: Lagerkraft, ergebnis: Traegerergebnis, zerlegung: Zerlegung, heraus: Fallergebnis, uebertragen: Dict[str, List[Teillast]]) -> None
```

Die Kraft eines Lagers auf den Träger geht, umgekehrt, in das, worauf er liegt.

### lagerverlauf

```python
def lagerverlauf(lager: Linienlager, kraefte: Sequence[Wandkraft]) -> List[Tuple[float, float, float, float]]
```

Längs eines Linienlagers, was die Träger in es geben: Stufen
`(u_a, u_b, r, m)` von seinem Anfang bis zu seinem Ende, `u` in m ab
`lager.a`, `r` nach unten in N/m und `m` in Nm/m: das Moment, das
es hält, mit dem Vorzeichen der Platte -- negativ, wo es oben zieht, wie
herum das Lager auch gezeichnet ist ([[opencivil.decke.rechnung#_gehalten|_gehalten]]). Wo zwei Träger
dasselbe Stück tragen, zählen beide; ein schiefer gibt quer zum Lager
cos² seines Winkels weiter, wie die Platte (Folie 14).

### _gehalten

```python
def _gehalten(links: float, rechts: float) -> float
```

Was ein Lager an Moment hält, je Meter, wenn die Platte links von ihm
mit `links` an ihm zieht und rechts mit `rechts`: den Unterschied,
mit dem Vorzeichen der Seite, die stärker zieht. An einem Rand ist die
andere Seite null -- dann ist es das Moment der Platte dort.

### spitzen

```python
def spitzen(stufen: Sequence[Tuple[float, float, float, float]]) -> Tuple[float, float]
```

Aus den Stufen eines Linienlagers ([[opencivil.decke.rechnung#lagerverlauf|lagerverlauf]]): je der Wert von `r` und `m` mit dem grössten Betrag.

### _schwerpunkt

```python
def _schwerpunkt(l: Streckenlast) -> float
```

Wo die Resultierende einer Streckenlast liegt, ab ihrem Anfang.


## Konstanten

- `PROBE = 1e-06` – Unter diesem Anteil der Last gilt die Probe als erfüllt.

## Braucht

- [[opencivil.decke.aufteilung]]
- [[opencivil.decke.geometrie]]
- [[opencivil.decke.lasten]]
- [[opencivil.decke.modell]]
- [[opencivil.decke.streifen]]
- [[opencivil.decke.traeger]]
- [[opencivil.stabwerk.system]]

## Gebraucht von

- [[opencivil.decke.feld]]
- [[opencivil.decke.herleitung]]
- [[opencivil.decke.schnitt]]
- [[opencivil.decke.werk]]
- [[opencivil.web.deckendaten]]
