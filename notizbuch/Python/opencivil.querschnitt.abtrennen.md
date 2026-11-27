---
erzeugt: 012175fd7cd0
art: modul
tags: [modul]
---
> [!abstract] opencivil/querschnitt/abtrennen.py
> was ein Schnitt vom Querschnitt abtrennt.
> Paket [[opencivil.querschnitt]] · [Quelltext](../../opencivil/querschnitt/abtrennen.py)

## VERANTWORTUNG

Ein Schnitt ist eine Strecke quer durch den gezeichneten Querschnitt, mit
einem Pfeil zu einer ihrer Seiten. Abgetrennt ist, was auf der Seite des
Pfeils an der Strecke liegt und mit dem Rest nur ueber sie zusammenhaengt
([[opencivil.querschnitt.abtrennen#abtrennen|abtrennen]]): beim Plattenbalken der Flansch neben dem Steg, bei einer
Aufdopplung der Aufbeton ueber der Fuge, beim Verbundtraeger die Platte ueber
dem Profil. Dazu die Laenge `b_i`, ueber die der Schnitt Material von
Material trennt, und welche Staebe und welche Stuecke einer verschmierten
Linie im abgetrennten Teil liegen ([[opencivil.querschnitt.abtrennen#Abgetrennt|Abgetrennt]]).


## WIE GETEILT WIRD

In Streifen parallel zum Schnitt, ihre Grenzen auf jeder Ecke und auf der
Geraden des Schnitts. Zwischen zwei Grenzen liegt keine Ecke, jede Kante
quert einen Streifen ganz: je Streifen zerfaellt der Querschnitt in Trapeze,
jedes aus dem Material des innersten Polygons dort – wie in den Fasern,
wo ein Polygon im anderen dieses ersetzt. Zwei Trapeze haengen zusammen, wo
sie ein Stueck Rand gemeinsam haben, laenger als
[[opencivil.querschnitt.geometrie#Konstanten|TOLERANZ]]; ein Punkt genuegt nicht,
wie bei [[opencivil.querschnitt.geometrie#beruehren|beruehren]]. Auf der Geraden
des Schnitts zaehlt nur, was ausserhalb der Strecke liegt: auf ihr trennt
er.

So gilt jede Lage der Strecke ohne Sonderfall – an einer Ecke, laengs
einer Kante, laengs der Grenze zweier Polygone, ueber den Rand hinaus.
Endet sie im Material oder geht sie nur durch eine Wand eines Kastens,
haengt der Teil jenseits noch am Rest: dann trennt sie nichts ab, und der
Satz dazu sagt es ([[opencivil.querschnitt.abtrennen#Konstanten|NICHT_GETRENNT]]).

`b_i` ist die Laenge, auf der beidseits der Strecke Material liegt – ueber
eine Aussparung oder den Rand hinaus zaehlt sie nicht.


## EINHEITEN

Die der Punkte, wie in [[opencivil.querschnitt.geometrie|geometrie]] – in der
Zeichnung Millimeter.

Ein gezeichneter Schnitt mit Name und Kennung ist ein [[opencivil.querschnitt.abtrennen#Schnitt|Schnitt]].

## Inhalt

### Stueck

```python
@dataclass(frozen=True)
class Stueck
```

Ein Trapez des abgetrennten Teils, aus dem Material eines Polygons – Ecken in der Ebene.

- `polygon: int` – Der Index des Polygons, dessen Material hier gilt – das innerste.
- `punkte: Tuple[Punkt, ...]`

### Abgetrennt

```python
@dataclass(frozen=True)
class Abgetrennt
```

Was ein Schnitt abtrennt: die Stuecke aus Material, die Laenge `b_i` und
die Lage des Schnitts, um Punkte und Strecken zuzuordnen.

- `stuecke: Tuple[Stueck, ...]`
- `breite: float` – `b_i`: wie lang der Schnitt Material von Material trennt.
- `von: Punkt`
- `t: Punkt` – Die Richtung der Strecke, ein Einheitsvektor.
- `n: Punkt` – Die Seite des Pfeils, ein Einheitsvektor senkrecht zur Strecke.
- `laenge: float`

#### Abgetrennt.flaeche

```python
@property
def flaeche(self) -> float
```

Die Flaeche des abgetrennten Teils.

#### Abgetrennt.polygone

```python
@property
def polygone(self) -> Tuple[int, ...]
```

Die Polygone, von denen etwas abgetrennt ist, in ihrer Folge.

#### Abgetrennt.auf_dem_schnitt

```python
def auf_dem_schnitt(self, p: Punkt) -> bool
```

Ob `p` auf der Strecke liegt – ein Stab dort zaehlt zum Rest.

#### Abgetrennt.enthaelt

```python
def enthaelt(self, p: Punkt) -> bool
```

Ob `p` im abgetrennten Teil liegt, auf seinem Rand – nicht auf dem Schnitt.

#### Abgetrennt.strecke_teilen

```python
def strecke_teilen(self, a: Punkt, b: Punkt) -> List[Tuple[Punkt, Punkt]]
```

Die Teile der Strecke `a`–`b` im abgetrennten Teil. Geteilt wird
nur am Schnitt: anderswo grenzt der abgetrennte Teil an kein Material
des Rests.

### _im_trapez

```python
def _im_trapez(p: Punkt, ecken: Sequence[Punkt]) -> bool
```

Ob `p` im konvexen Vieleck `ecken` liegt, Rand eingeschlossen.

### _Trapez

```python
@dataclass
class _Trapez
```

Ein Trapez eines Streifens, in den Koordinaten des Schnitts: u laengs, w quer.

- `streifen: int`
- `unten: float`
- `oben: float`
- `links: Tuple[float, float]` – u des linken Rands unten und oben.
- `rechts: Tuple[float, float]`
- `polygon: int`

### _ebenen

```python
def _ebenen(wert_w: Sequence[float]) -> List[float]
```

Die Grenzen der Streifen: jedes w einer Ecke und die Gerade des Schnitts,
naeher als [[opencivil.querschnitt.geometrie#Konstanten|TOLERANZ]] beieinander als eine – die Null bleibt null.

### _streifen

```python
def _streifen(uw: Sequence[Sequence[Punkt]], tiefe: Sequence[int], traegt: Sequence[bool], unten: float, oben: float, k: int) -> List[Optional[_Trapez]]
```

Die Trapeze eines Streifens, von links nach rechts – je Abschnitt
zwischen zwei Kanten eines, `None`, wo dort kein Material liegt und der
Abschnitt breiter ist als [[opencivil.querschnitt.geometrie#Konstanten|TOLERANZ]]. Ein Abschnitt ohne Breite
zwischen zwei Kanten, die aufeinander liegen, faellt weg: die Trapeze
beiderseits beruehren sich.

### _lage

```python
def _lage(von: Punkt, bis: Punkt, links: bool) -> Optional[Tuple[Punkt, Punkt, float]]
```

Richtung `t` und Seite `n` der Strecke, je ein Einheitsvektor, und
ihre Laenge – `n` links von ihr, in ihrer Richtung gesehen, oder
rechts. Ohne Laenge nichts.

### abtrennen

```python
def abtrennen(polygone: Sequence[Sequence[Punkt]], traegt: Sequence[bool], eltern: Sequence[Optional[int]], von: Punkt, bis: Punkt, *, links: bool=True) -> Union[Abgetrennt, str]
```

Was die Strecke von `von` nach `bis` abtrennt – auf ihrer linken
Seite, in Richtung `von` → `bis` gesehen, sonst auf der rechten. Trennt
sie nichts ab, ein Satzteil, warum. `traegt` sagt je Polygon, ob es
Material hat, `eltern`, in welchem es liegt
([[opencivil.querschnitt.geometrie#verschachteln|verschachteln]]).

### Schnitt

```python
@dataclass(frozen=True)
class Schnitt
```

Ein Schnitt der Zeichnung: die Strecke von `von` nach `bis`, in mm,
der Pfeil links von ihr, in ihrer Richtung gesehen – mit `links`
falsch rechts.

- `name: str`
- `kennung: str`
- `von: Punkt`
- `bis: Punkt`
- `links: bool`

#### Schnitt.abtrennen

```python
def abtrennen(self, polygone: Sequence[Sequence[Punkt]], traegt: Sequence[bool], eltern: Sequence[Optional[int]]) -> Union[Abgetrennt, str]
```

Was er von diesen Polygonen abtrennt – siehe [[opencivil.querschnitt.abtrennen#Schnitt.abtrennen|abtrennen]].

#### Schnitt.nichts_abgetrennt

```python
def nichts_abgetrennt(self, grund: str) -> str
```

Der Satz, dass er nichts abtrennt, mit dem Grund – ueberall derselbe.

#### Schnitt.pfeil

```python
def pfeil(self, links: bool) -> str
```

Wohin sein Pfeil auf dieser Seite zeigt, in Worten – «nach oben»,
«nach rechts unten» ([[opencivil.querschnitt.abtrennen#Konstanten|RICHTUNGEN]]): fuer den Schalter der
Seite. Links und rechts der Richtung, in der er gezeichnet ist, sieht
man im Bild nicht mehr. Ohne Laenge leer.

### aus_schnitt

```python
def aus_schnitt(s: Mapping) -> Schnitt
```

Ein Schnitt der Beschreibung, wie
[[opencivil.projekt.querschnittsanalyse#QuerschnittsanalyseEintrag.elemente|elemente]]
ihn gibt.


## Konstanten

- `OHNE_LAENGE = 'er hat keine Länge'` – Warum ein Schnitt nichts abtrennt – Satzteile ohne Punkt, fuer die Zeichnung und die Herleitung.
- `OHNE_MATERIAL = 'er trennt nirgends Material von Material – er muss durch den Quersch…`
- `NICHT_GETRENNT = 'der Teil auf der Seite des Pfeils hängt noch ausserhalb der Strecke …`
- `RICHTUNGEN = ('nach rechts', 'nach rechts oben', 'nach oben', 'nach links oben', '…` – Wie eine Richtung im Bild heisst, je Achtel des Kreises ab y, gegen den Uhrzeigersinn – z zeigt nach oben.

## Braucht

- [[opencivil.querschnitt.geometrie]]

## Gebraucht von

- [[opencivil.nachweis.qa_schubfluss]]
- [[opencivil.projekt.aufbau.querschnittsanalyse]]
- [[opencivil.web.zeichengeometrie]]
