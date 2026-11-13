---
erzeugt: e56996e41eeb
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
   teilen (Stahlbeton II, 7.2 Platten, Folie 33: «Anschliessend werden die
   Reaktionen des Flächenlagers als Belastung auf den versteckten Unterzug
   aufgebracht»).
3. Was in Linienlager und Stützen geht, sind die Lagerkräfte der Decke.

Am Ende eine Probe: alle Lagerkräfte zusammen sind die Last, abzüglich
dessen, was neben den Platten liegt oder auf einem Streifen, der nicht trägt.


## DIE LAGERKRÄFTE

Eine Stütze bekommt die Summe der Kräfte aller Träger auf ihr. Ein
Linienlager bekommt von jedem Träger, der es kreuzt, dessen Kraft --
gleichmässig verteilt über das Stück des Lagers, über das der Träger geht --
und bei Einspannung dessen Moment ebenso: ein Verlauf in kN/m und kNm/m
längs des Lagers.

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
- `C: float` – Das Einspannmoment, in Nm -- positiv, wenn es den Träger im Gegenuhrzeigersinn hält.

#### Wandkraft.laenge

```python
@property
def laenge(self) -> float
```

#### Wandkraft.je_meter

```python
@property
def je_meter(self) -> Tuple[float, float]
```

`(r, m)`: Kraft in N/m und Moment in Nm/m.

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
def _weitergeben(k: Lagerkraft, traeger: Traeger, zerlegung: Zerlegung, heraus: Fallergebnis, uebertragen: Dict[str, List[Teillast]]) -> None
```

Die Kraft eines Lagers auf den Träger geht, umgekehrt, in das, worauf er liegt.

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
