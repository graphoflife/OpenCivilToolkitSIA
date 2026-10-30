---
erzeugt: fce4ef4a37b5
art: modul
tags: [modul]
---
> [!abstract] opencivil/durchstanzen/schnitt.py
> der Nachweisschnitt um die gestützte Fläche.
> Paket [[opencivil.durchstanzen]] · [Quelltext](../../opencivil/durchstanzen/schnitt.py)

## VERANTWORTUNG

Aus der gestützten Fläche -- einer Stütze oder dem Ende oder der Ecke einer
Wand --, ihrer Lage in der Platte, den Aussparungen und dem Abstand des
Schnitts der Nachweisschnitt nach SIA 262:2025, 4.3.6.2.2 und 4.3.6.2.3:
welche Teile von ihm zählen, seine wirksame Länge u, die Fläche, die er
umschliesst, und der Schwerpunkt seiner zählenden Teile. Mit der Fläche
zieht der Nachweis die Lasten darin ab (4.3.6.2.6) und rechnet `b` für k_e
(4.3.6.2.4), mit dem Schwerpunkt die Exzentrizität e_u. Die Abminderung für
Momente selbst, k_e, ist Sache des Nachweises.


## DER SCHNITT (Figur 22)

Im Abstand `a` um die gestützte Fläche -- `d_v/2`, beim äusseren Schnitt
`d_v,out/2` --, um ihre konvexe Hülle: bei konkaver Geometrie ist der
Umfang zu minimieren (Figur 22c). Eine Stütze ist ein konvexer Kern mit
einem Radius ([[opencivil.durchstanzen.schnitt#Stuetzenflaeche|Stuetzenflaeche]]): ein Rechteck hat den Radius null,
eine Rundstütze einen Punkt als Kern. Ihr Schnitt besteht aus Strecken
parallel zu den Seiten des Kerns und Bögen um seine Ecken ([[opencivil.durchstanzen.schnitt#rundum|rundum]]).
An einem Wandende und einer Wandecke läuft er um das Ende bzw. um die
äussere Ecke (Figur 23b und c).


## WAS NICHT ZÄHLT

(Figur 23), kumulativ

- An grossen gestützten Flächen zählt von einer geraden Strecke des Schnitts
  nur, was höchstens 1.5·d_v von einer Ecke entfernt liegt (Figur 23a bis c).
  Eine Strecke weiss darum, wie weit sie von jedem Ende her zählt
  ([[opencivil.durchstanzen.schnitt#Strecke|Strecke]]); wo eine Wand weiterläuft, zählt sie von dort her nicht.
- Am Plattenrand endet der Schnitt, wenn er dadurch kürzer wird (Figur
  22d). Gerechnet werden die möglichen Schnitte -- der geschlossene und die,
  die zu einem oder zu beiden Rändern laufen --, und es gilt der kürzeste
  ([[opencivil.durchstanzen.schnitt#nachweisschnitt|nachweisschnitt]]). Was ausserhalb der Platte liegt, zählt nie.
- Hinter einer Aussparung, die näher als 5·d_v am Schnitt liegt, zählt nicht,
  was zwischen den beiden Strahlen von der Stützenachse an ihr vorbei liegt
  (Figur 23d).


## GERECHNET

Mit Teilstücken von höchstens [[opencivil.durchstanzen.schnitt#Konstanten|TEILSTUECK]]: jedes zählt oder nicht, je
nach seiner Mitte. Die Länge ist damit auf Bruchteile eines Millimeters
genau, auch wo Rand, Ecke und Aussparung zusammentreffen, und kein Fall
braucht eine eigene Formel.


## EINHEITEN

m und rad.

## Inhalt

### Strecke

```python
@dataclass(frozen=True)
class Strecke
```

Ein gerades Stück des Schnitts, von `a` nach `b`. Es zählt, was
höchstens `zaehlt_a` von `a` oder `zaehlt_b` von `b` entfernt
liegt: neben einer Ecke 1.5·d_v (Figur 23), wo eine Wand weiterläuft
null, sonst unbegrenzt.

- `a: Punkt`
- `b: Punkt`
- `zaehlt_a: float = math.inf`
- `zaehlt_b: float = math.inf`

#### Strecke.laenge

```python
@property
def laenge(self) -> float
```

#### Strecke.teile

```python
def teile(self) -> Iterator[Tuple[Punkt, Punkt, bool]]
```

Die Teilstücke, je mit Anfang, Ende und ob es neben einer Ecke liegt und darum zählt.

#### Strecke.punkte

```python
def punkte(self) -> List[Punkt]
```

### Bogen

```python
@dataclass(frozen=True)
class Bogen
```

Ein Kreisbogen um `mitte`, gegen den Uhrzeigersinn von `von` bis `bis` (rad).

- `mitte: Punkt`
- `radius: float`
- `von: float`
- `bis: float`

#### Bogen.laenge

```python
@property
def laenge(self) -> float
```

#### Bogen.punkt

```python
def punkt(self, winkel: float) -> Punkt
```

#### Bogen.teile

```python
def teile(self) -> Iterator[Tuple[Punkt, Punkt, bool]]
```

#### Bogen.punkte

```python
def punkte(self, schritte: int=16) -> List[Punkt]
```

### Halbebene

```python
@dataclass(frozen=True)
class Halbebene
```

Die Seite einer Geraden, auf der die Platte liegt: `n · p <= c`.

- `n: Punkt`
- `c: float`

#### Halbebene.enthaelt

```python
def enthaelt(self, p: Punkt) -> bool
```

### Stuetzenflaeche

```python
@dataclass(frozen=True)
class Stuetzenflaeche
```

Eine Stütze: ein konvexer Kern -- Polygon gegen den Uhrzeigersinn, Strecke
oder Punkt -- mit einem Radius darum. Ein Rechteck ist sein eigener Kern
mit Radius null; eine Rundstütze ein Punkt mit dem halben Durchmesser.

- `kern: Tuple[Punkt, ...]`
- `radius: float = 0.0`

#### Stuetzenflaeche.achse

```python
@property
def achse(self) -> Punkt
```

Die Stützenachse: der Schwerpunkt des Kerns.

#### Stuetzenflaeche.umriss

```python
def umriss(self, schritte: int=16) -> List[Punkt]
```

Der Umriss der Stütze als Polygon -- fürs Bild und für Prüfungen.

#### Stuetzenflaeche.grenzen

```python
def grenzen(self) -> Tuple[float, float, float, float]
```

`(x_min, y_min, x_max, y_max)` der Stütze.

### rundum

```python
def rundum(kern: Sequence[Punkt], radius: float, zaehlt: Callable[[Punkt, Punkt], Tuple[float, float]]=lambda p, q: (math.inf, math.inf)) -> List[Stueck]
```

Der Rand des Kerns, um `radius` nach aussen gerückt: je Seite eine
Strecke, je Ecke ein Bogen, gegen den Uhrzeigersinn. Ein Punkt gibt einen
Kreis, eine Strecke zwei Strecken und zwei Halbkreise. `zaehlt` sagt je
Seite `p → q` des Kerns, wie weit ihre Strecke von jedem Ende her zählt.

### _normale

```python
def _normale(p: Punkt, q: Punkt) -> Punkt
```

Die Normale der Seite `p → q` nach aussen, für ein Polygon gegen den Uhrzeigersinn.

### konvexe_huelle

```python
def konvexe_huelle(punkte: Sequence[Punkt]) -> Tuple[Punkt, ...]
```

Die konvexe Hülle gegen den Uhrzeigersinn -- bei weniger als drei Ecken die Punkte selbst.

### _polygon

```python
def _polygon(stuecke: Sequence[Stueck], schritte: int=16) -> List[Punkt]
```

Die Stücke als geschlossenes Polygon -- die Endpunkte, Bögen in feinen Schritten.

### Kandidat

```python
@dataclass(frozen=True)
class Kandidat
```

Ein möglicher Schnitt: seine Stücke, die Platte, in der er gilt, das
Polygon der Fläche, die er umschliesst, und wie er heisst.

- `name: str`
- `stuecke: Tuple[Stueck, ...]`
- `platte: Tuple[Halbebene, ...]`
- `umschlossen: Tuple[Punkt, ...]`
- `raender: int = 0` – Zu wie vielen Plattenrändern er läuft.

### kandidaten_stuetze

```python
def kandidaten_stuetze(stuetze: Stuetzenflaeche, abstand: float, eckenbereich: float, raender: Sequence[Halbebene]=()) -> List[Kandidat]
```

Die möglichen Schnitte um eine Stütze im Abstand `abstand`: der
geschlossene und, je Teilmenge der Plattenränder, der Schnitt, der zu
diesen Rändern läuft (Figur 22d). Zum Rand verlängert wird der Kern: er
reicht dann bis über den Rand hinaus, und was jenseits liegt, zählt nicht.

Eine Strecke entlang einer Seite der Stütze zählt `eckenbereich` von
jeder Ecke her (1.5·d_v, Figur 23a); eine, die zum Rand läuft, ganz --
am freien Rand ballt sich keine Querkraft.

### _abstand_zum_rand

```python
def _abstand_zum_rand(stuetze: Stuetzenflaeche, h: Halbebene) -> float
```

Wie weit die Stütze vom Rand entfernt ist -- in Richtung seiner Normalen.

### kandidat_wandende

```python
def kandidat_wandende(dicke: float, abstand: float, d_v: float) -> Kandidat
```

Der Schnitt um das Ende einer Wand der Dicke `dicke` (Figur 23b): das
Ende liegt bei x = 0, die Wand läuft nach +x weiter. Entlang der Wand zählt
er 1.5·d_v vom Ende her, um das Ende ganz.

### kandidat_wandecke

```python
def kandidat_wandecke(dicke: float, abstand: float, d_v: float) -> Kandidat
```

Der Schnitt um die äussere Ecke zweier Wände der Dicke `dicke` (Figur
23c): die Ecke liegt im Ursprung, die Wände laufen nach +x und nach +y,
die Platte liegt aussen. Entlang jeder Wand zählt er 1.5·d_v von der Ecke.

### _rechtsrum

```python
def _rechtsrum(punkte: Sequence[Punkt]) -> List[Punkt]
```

Das Polygon gegen den Uhrzeigersinn.

### _abschneiden

```python
def _abschneiden(polygon: Sequence[Punkt], halbebenen: Sequence[Halbebene]) -> List[Punkt]
```

Das Polygon, auf die Halbebenen beschnitten (Sutherland-Hodgman).

### Schatten

```python
@dataclass(frozen=True)
class Schatten
```

Was eine Aussparung vom Schnitt wegnimmt: der Winkelbereich zwischen den
beiden Strahlen von der Stützenachse an ihr vorbei (Figur 23d), gegen den
Uhrzeigersinn von `von` bis `bis`.

- `von: float`
- `bis: float`

#### Schatten.enthaelt

```python
def enthaelt(self, winkel: float) -> bool
```

### schatten

```python
def schatten(aussparung: Sequence[Punkt], achse: Punkt) -> Schatten
```

Der Winkelbereich, den die Aussparung von der Achse aus verdeckt: der
kleinste Bogen, der die Richtungen zu allen ihren Ecken enthält.

### abstand_zum_schnitt

```python
def abstand_zum_schnitt(aussparung: Sequence[Punkt], stuecke: Sequence[Stueck]) -> float
```

Der kleinste Abstand zwischen der Aussparung und dem Schnitt -- auf 1 cm genau genügt.

### Linienzug

```python
@dataclass(frozen=True)
class Linienzug
```

Ein Stück des Schnitts fürs Bild: seine Punkte und ob es zählt.

- `punkte: Tuple[Punkt, ...]`
- `zaehlt: bool`

### Auswertung

```python
@dataclass(frozen=True)
class Auswertung
```

Was ein Kandidat ergibt. Längen in m: in der Platte, was davon an Ecken
grosser Flächen und hinter Aussparungen nicht zählt, und die wirksame
Länge `u`. Dazu die umschlossene Fläche, ohne Aussparungen, der
Schwerpunkt der zählenden Teile und die Linien fürs Bild.

- `kandidat: Kandidat`
- `in_der_platte: float`
- `an_ecken: float`
- `hinter_aussparungen: float`
- `flaeche: float`
- `flaeche_ohne_aussparungen: float`
- `schwerpunkt: Punkt`
- `linien: Tuple[Linienzug, ...]`

#### Auswertung.u

```python
@property
def u(self) -> float
```

### auswerten

```python
def auswerten(kandidat: Kandidat, *, d_v: float, achse: Punkt, aussparungen: Sequence[Sequence[Punkt]]=()) -> Auswertung
```

Welche Teile des Kandidaten zählen -- in der Platte, neben einer Ecke und
nicht hinter einer Aussparung, die näher als 5·d_v liegt.

### _vereinfacht

```python
def _vereinfacht(punkte: Sequence[Punkt], toleranz: float=0.0002) -> List[Punkt]
```

Fast gerade Folgen von Punkten auf ihre Ecken gekürzt -- fürs Bild genügt das.

### _ueberlappung

```python
def _ueberlappung(aussparung: Sequence[Punkt], umschlossen: Sequence[Punkt]) -> float
```

Wie viel der Aussparung in der umschlossenen Fläche liegt -- die ist konvex.

### Nachweisschnitt

```python
@dataclass(frozen=True)
class Nachweisschnitt
```

Der massgebende Schnitt -- der kürzeste der Kandidaten -- und alle, die gerechnet wurden.

- `massgebend: Auswertung`
- `alle: Tuple[Auswertung, ...] = field(default_factory=tuple)`

#### Nachweisschnitt.u

```python
@property
def u(self) -> float
```

### nachweisschnitt

```python
def nachweisschnitt(kandidaten: Sequence[Kandidat], *, d_v: float, achse: Punkt, aussparungen: Sequence[Sequence[Punkt]]=()) -> Nachweisschnitt
```

Alle Kandidaten ausgewertet; es gilt der mit der kleinsten wirksamen Länge
(Figur 22d). Sind zwei gleich lang -- die Stütze steht am Rand --, heisst
er nach dem, der zum Rand läuft.


## Konstanten

- `TEILSTUECK = 0.001` – Wie lang ein Teilstück des Schnitts höchstens ist, in m.
- `FEIN = 64` – In wie viele Schritte ein Viertelkreis zerfällt, wo eine Fläche gerechnet wird.
- `ECKENBEREICH = 1.5` – Wie weit von einer Ecke eine gerade Strecke des Schnitts zählt, in d_v (SIA 262:2025, 4.3.6.2.3, Figur 23a bis c).
- `AUSSPARUNGSABSTAND = 5.0` – Wie nahe eine Aussparung dem Schnitt sein muss, damit sie ihn mindert, in d_v (SIA 262:2025, 4.3.6.2.3, Figur 23d).

## Braucht

- [[opencivil.querschnitt.geometrie]]
