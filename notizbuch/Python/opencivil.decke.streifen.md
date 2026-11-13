---
erzeugt: b507ff768791
art: modul
tags: [modul]
---
> [!abstract] opencivil/decke/streifen.py
> die Decke in Streifen zerlegt.
> Paket [[opencivil.decke]] · [Quelltext](../../opencivil/decke/streifen.py)

## VERANTWORTUNG

Aus der [[opencivil.decke.modell#Decke|Decke]] die Streifen der
Streifenmethode: je Richtung der Lastabtragung ein Satz paralleler
Feldstreifen, dazu die versteckten Unterzüge als Streifen eigener Breite.
Jeder Streifen zerfällt in Träger -- Stücke, die über Platten
durchlaufen -- und jeder Träger weiss, worauf er liegt.


## DIE STREIFEN EINER RICHTUNG

Alle Platten, die in einer Richtung tragen, bilden ihre Familie; über sie
hinweg laufen die Streifen dieser Richtung durch. Quer zur Richtung wird
die Familie an festen Stellen geteilt -- an den Ecken der Platten, an den
Rändern paralleler Unterzüge, an den Enden der Lager, an den Rändern der
Stützenbereiche und der Unterzüge, die quer liegen. Was dazwischen liegt,
wird in gleich breite Streifen von höchstens
[[opencivil.decke.modell#Decke|streifenbreite]] geteilt. So liegt
keine Ecke im Innern eines Streifens, und ein Lager, ein Unterzug, ein
Stützenbereich überdeckt einen Streifen ganz oder gar nicht.


## WORAUF EIN TRÄGER LIEGT

* Auf einem **Linienlager**, das ihn quer schneidet -- als Punkt; es hält
  die Höhe, die Drehung oder beides.
* Auf einem **Unterzug höherer Stufe**, den seine Achse quer kreuzt; die
  Feldstreifen haben Stufe 0. Ein Flächenlager mit gleichmässiger Pressung
  über die Fläche, die beide teilen (Stahlbeton II, 7.2 Platten, Folie 33).
* Auf einer **Stütze**, deren Stützenbereich seine Achse kreuzt -- ebenso
  ein Flächenlager (Folie 36: «Lastverteilelemente als Flächenlager mit
  gleichmässiger Pressung»).

Liegen zwei davon an derselben Stelle -- die eine in der Fläche der
anderen --, trägt das erste in dieser Folge: Linienlager, Unterzug (höhere
Stufe zuerst), Stütze. So liegt in der Musterlösung des Kolloquiums 4 der
Unterzug in x-Richtung über der Stütze auf den Unterzügen in y-Richtung,
und erst diese auf der Stütze.

Ein Unterzug parallel zu einer Richtung nimmt in seiner Fläche deren
Lastanteil auf; quer liegende Streifen laufen über ihn hinweg und legen
ihren Anteil auf ihn ([[opencivil.decke.lasten|lasten]]).

## Inhalt

### Richtung

```python
@dataclass(frozen=True)
class Richtung
```

Eine Richtung der Lastabtragung: Winkel in [0, π), `n` längs, `t` quer.

- `winkel: float`
- `n: Punkt`
- `t: Punkt`
- `name: str`

#### Richtung.parallel

```python
def parallel(self, andere: 'Richtung') -> bool
```

#### Richtung.punkt

```python
def punkt(self, s: float, tau: float) -> Punkt
```

Der Punkt mit `p·n = s` und `p·t = τ`.

### richtung

```python
def richtung(winkel: float) -> Richtung
```

Die Richtung zu einem Winkel -- auf [0, π) gebracht; `x` und `y` heissen so.

### richtung_der_strecke

```python
def richtung_der_strecke(a: Punkt, b: Punkt) -> Richtung
```

### Auflager

```python
@dataclass(frozen=True)
class Auflager
```

Worauf ein Träger an einer Stelle liegt. `s` in m ab dem Anfang des
Trägers -- bei einem Flächenlager der Schwerpunkt der Fläche, die beide
teilen (`kontakt`). Dort drückt das Lager mit `pressung`, je Kraft
eins: ein Verlauf über `s`, dessen Integral eins ist.

- `s: float`
- `vertikal: bool`
- `eingespannt: bool`
- `art: str`
- `name: str`
- `kontakt: Tuple[Punkt, ...] = ()`
- `strecke: Tuple[Punkt, ...] = ()` – Bei einem Linienlager: das Stück von ihm, über das der Streifen geht.
- `pressung: Tuple[Streckenlast, ...] = ()`

#### Auflager.bereich

```python
@property
def bereich(self) -> Tuple[float, float]
```

Von wo bis wo das Lager drückt, in `s` des Trägers.

### Lage

```python
@dataclass
class Lage
```

Wo eine Stelle auf ihrem Träger liegt -- für die Aufteilung der Last.

- `traegt: bool`
- `spannweite: float` – Die Spannweite des Felds, in dem sie liegt; bei einer Kragplatte das Doppelte ihrer Länge.
- `abstand: float` – Bis zum nächsten Lager, das die Höhe hält -- null in seiner Fläche.

### Traeger

```python
@dataclass
class Traeger
```

Ein Stück eines Streifens, das von einem Ende zum anderen durchläuft.

- `name: str`
- `streifen: str`
- `s0: float`
- `s1: float` – Anfang und Ende in `s = p·n` der Richtung des Streifens.
- `abschnitte: Tuple[Tuple[float, float, float], ...]` – `(von, bis, EI)` in m ab dem Anfang und Nm².
- `auflager: List[Auflager]`
- `_balken: Optional[Balken] = field(default=None, repr=False)`

#### Traeger.L

```python
@property
def L(self) -> float
```

#### Traeger.balken

```python
@property
def balken(self) -> Balken
```

#### Traeger.lage

```python
def lage(self, s: float) -> Lage
```

Spannweite und Abstand zum Lager an der Stelle `s` (m ab dem Anfang).

### Streifen

```python
@dataclass
class Streifen
```

Ein Streifen: quer von `von` bis `bis` in `τ = p·t`. Ein
Feldstreifen hat Stufe 0; ein Unterzug seine Stufe, seinen Eintrag und
sein Gebiet -- das Rechteck, das er belegt.

- `name: str`
- `richtung: Richtung`
- `von: float`
- `bis: float`
- `stufe: int = 0`
- `unterzug: Optional[Unterzug] = None`
- `gebiet: Tuple[Punkt, ...] = ()`
- `traeger: List[Traeger] = field(default_factory=list)`

#### Streifen.breite

```python
@property
def breite(self) -> float
```

#### Streifen.mitte

```python
@property
def mitte(self) -> float
```

#### Streifen.laengs

```python
@property
def laengs(self) -> Tuple[float, float]
```

Wie weit der Streifen längs reicht -- ein Unterzug über sein Gebiet, ein Feldstreifen unbegrenzt.

#### Streifen.band

```python
def band(self, s_von: float, s_bis: float) -> List[Punkt]
```

Das Rechteck des Streifens von `s_von` bis `s_bis`, im Gegenuhrzeigersinn.

#### Streifen.traeger_bei

```python
def traeger_bei(self, s: float) -> Optional[Traeger]
```

Der Träger, auf dem `s = p·n` liegt -- sonst der nächste.

### Gruppe

```python
@dataclass
class Gruppe
```

Platten mit denselben zwei Richtungen -- für sie gilt eine Aufteilung der Last.

- `richtungen: Tuple[Richtung, Richtung]`
- `platten: List[Platte]`
- `stuecke: List[List[Punkt]]` – Die Platten in konvexen Stücken.

### Zerlegung

```python
@dataclass
class Zerlegung
```

- `richtungen: List[Richtung]`
- `streifen: List[Streifen]`
- `gruppen: List[Gruppe]`
- `stuetzenbereiche: Dict[str, List[Punkt]]`
- `parallele: Dict[str, List[Streifen]]` – Je Feldstreifen die Unterzüge in seiner Richtung, in deren Breite er liegt.
- `meldungen: List[Meldung]`

#### Zerlegung.feldstreifen

```python
def feldstreifen(self, r: Richtung) -> List[Streifen]
```

#### Zerlegung.unterzuege

```python
@property
def unterzuege(self) -> List[Streifen]
```

#### Zerlegung.traeger

```python
@property
def traeger(self) -> List[Traeger]
```

### richtungen_der_platte

```python
def richtungen_der_platte(p: Platte) -> Tuple[Richtung, Richtung]
```

### stuetzenbereich

```python
def stuetzenbereich(stuetze: Stuetze, unterzuege: Sequence[Unterzug]) -> List[Punkt]
```

Die Fläche `lx × ly`, über die die Stütze trägt. Ohne Angabe ein
Quadrat, so breit wie der breiteste Unterzug über ihr und mindestens so
gross wie die Stütze -- in der Musterlösung des Kolloquiums 4 die
1 m × 1 m, wo sich die Unterzüge kreuzen. Nach Vorgabe, nicht
nachgeschlagen: Folie 39 lässt die Grösse frei.

### zerlegen

```python
def zerlegen(decke: Decke) -> Zerlegung
```

Die Streifen, ihre Träger und deren Lager -- oder, was dem im Weg steht.

### _feldstreifen

```python
def _feldstreifen(r: Richtung, platten: Sequence[Platte], decke: Decke, unterzuege: Sequence[Streifen], bereiche: Dict[str, List[Punkt]], stuecke: Dict[str, List[List[Punkt]]]) -> List[Streifen]
```

Die Feldstreifen einer Richtung, nach ihrer Lage quer geordnet und nummeriert.

### _traeger

```python
def _traeger(streifen: Streifen, platten: Sequence[Platte], decke: Decke, unterzuege: Sequence[Streifen], bereiche: Dict[str, List[Punkt]], stuecke: Dict[str, List[List[Punkt]]]) -> List[Traeger]
```

Wo der Streifen über Platten läuft, ein Träger je zusammenhängendes Stück -- mit Steifigkeit und Lagern.

### _abschnitte

```python
def _abschnitte(streifen: Streifen, s0: float, s1: float, teile: Sequence[Tuple[float, float, Platte]]) -> Tuple[Tuple[float, float, float], ...]
```

Die Biegesteifigkeit `E · b · h³/12` längs der Achse: je Platte, über
die die Achse läuft. Wo sie neben den Platten läuft -- an einem schiefen
Rand --, gilt die der nächsten.

### _flaechenlager

```python
def _flaechenlager(streifen: Streifen, s0: float, L: float, achse: Tuple[Punkt, Punkt], gebiet: Sequence[Punkt], art: str, name: str) -> Optional[Auflager]
```

Ein Flächenlager, wenn die Achse des Streifens das Gebiet kreuzt -- mit
Pressung über die Fläche, die beide auf dem Träger teilen, und dort, wo
ihr Schwerpunkt liegt. Liegt die Fläche ganz hinter seinem Ende, ein
Punkt dort.

### pressung

```python
def pressung(kontakt: Sequence[Punkt], n: Punkt, s0: float=0.0) -> List[Streckenlast]
```

Eine gleichmässige Pressung je Kraft eins auf dem konvexen `kontakt`,
als Last je Länge längs `n`, in `s = p·n - s0`. Ihr Integral ist
eins, ihr Schwerpunkt der des Kontakts.

### _an_derselben_stelle

```python
def _an_derselben_stelle(a: Auflager, b: Auflager) -> bool
```

Ob zwei Lager an derselben Stelle liegen -- das eine in der Fläche des anderen.

### pruefen

```python
def pruefen(decke: Decke) -> List[Meldung]
```

Was die Zerlegung aufhält -- Fehler -- und was auffällt -- Hinweise.

### _ueberlappen

```python
def _ueberlappen(a: Sequence[Sequence[Punkt]], b: Sequence[Sequence[Punkt]]) -> bool
```

Ob sich zwei Flächen aus konvexen Stücken mehr als berühren.


## Konstanten

- `TEILUNG = 0.001` – Wie nahe zwei Teilungsstellen quer liegen dürfen, in m -- näher gelten sie als eine.
- `RAND = 0.0001` – So weit über sein Ende hinaus sucht ein Träger seine Lager, in m.
- `STREIFEN_HOECHSTENS = 4000` – Mehr Streifen rechnet die Decke nicht -- sonst warten Benutzer und Browser zu lange.
- `PARALLEL = 1e-06` – Unter diesem Winkel gelten zwei Richtungen als parallel, in rad.

## Braucht

- [[opencivil.decke.geometrie]]
- [[opencivil.decke.modell]]
- [[opencivil.decke.traeger]]
- [[opencivil.stabwerk.system]]

## Gebraucht von

- [[opencivil.decke.aufteilung]]
- [[opencivil.decke.lasten]]
- [[opencivil.decke.rechnung]]
