---
erzeugt: 48778c51d415
art: modul
tags: [modul]
---
> [!abstract] opencivil/decke/baender.py
> die Bänder, die eine Decke selbst legt.
> Paket [[opencivil.decke]] · [Quelltext](../../opencivil/decke/baender.py)

## VERANTWORTUNG

Bei automatischer Aufteilung legt die Rechnung Bänder -- versteckte
Unterzüge ([[opencivil.decke.modell#Unterzug|Unterzug]] mit `von_selbst`),
so breit wie [[opencivil.decke.modell#Decke|bandbreite]] --, wo
Streifen sonst ohne Lager enden oder eine Stütze nur die Streifen fände,
die über sie laufen. Das geschieht, bevor die Decke in Streifen zerfällt
([[opencivil.decke.rechnung#rechnen|rechnen]]). Bei fester Aufteilung legt sie
keine: dort gilt, was der Benutzer gibt.


## WO BÄNDER LIEGEN

1. **Über Stützen**: durch die Mitte jeder Stütze, in den zwei Richtungen
   der Platte, auf der sie steht -- über alle Stützen auf dieser Linie bis
   zum nächsten Lager quer dazu, einer Wand oder einem Unterzug, oder bis
   zum Rand der Platte. Steht die Stütze näher am Rand als eine halbe
   Bandbreite, rückt das Band nach innen, bis es ganz in der Platte liegt;
   die Mitte der Stütze bleibt darin.
2. **An offenen Rändern**: wo die Streifen einer Platte enden, ohne dass
   ein Linienlager sie hält -- an einem freien Rand, am Rand eines Lochs, an
   einer Platte mit anderen Richtungen. Das Band liegt innen am Rand, längs
   dazu, und reicht beidseits bis zum nächsten Lager: einer Wand, einer
   Stütze, einem Band über Stützen, einem Unterzug.

Die Bänder liegen unter allen Unterzügen des Benutzers, mit den Stufen
[[opencivil.decke.baender|STUFE_RAND]] und
[[opencivil.decke.baender|STUFE_STUETZE]] zwischen den Feldstreifen (0)
und dessen Stufen (ab 1): ein Band liegt auf einem Unterzug, nie trägt es
einen -- und ein Band am Rand liegt auf einem über Stützen.

Ein Band liegt auf mindestens zwei Lagern, die die Höhe halten. Als Kragarm
legt die Rechnung keines: auf einer eingespannten Wand trägt die Platte
selbst als Kragplatte. Ein Band am Rand legt sie nur, wo die Streifen quer
zum Rand sonst schon ein Lager haben -- das Band gibt ihnen das zweite. Eine
Platte, die nur in einer Richtung trägt, bekommt an ihren freien Rändern
darum keines; zwei Bänder dort nähmen ihr die ganze Last ab. Ein offener
Rand, kürzer als ein Band breit, bekommt keines. Liegt schon ein Unterzug
des Benutzers oder ein anderes Band längs auf dem Weg, ersetzt es das Band.
Über eine Wand längs läuft keines: es endet, wo sie beginnt -- dort trägt
die Wand selbst.

Liegt eine Platte nur auf zwei Wänden über Eck, findet kein Band zwei
Lager: sie trüge nur mit Drillmomenten, und die rechnet die
Streifenmethode nicht. Wo die Last dann ausfällt, sagt
[[opencivil.decke.aufteilung|aufteilung]].

Nach Vorgabe, nicht nachgeschlagen: Lage, Stufe und Breite der Bänder. Die
Norm lässt jede Aufteilung der Last zu, die im Gleichgewicht ist
(SIA 262:2025, 4.1.4.2.2).

## Inhalt

### gelegt

```python
def gelegt(decke: Decke) -> Decke
```

Die Decke mit den Bändern, die sie selbst legt -- unverändert bei fester
Aufteilung, ohne Platte oder wenn ihre Geometrie nicht stimmt: das sagt
dann die Zerlegung.

### art

```python
def art(band: Unterzug) -> str
```

Wo ein Band liegt, in Worten: «über Stützen» oder «am Rand».

### offene_raender

```python
def offene_raender(platten: Sequence[Platte], decke: Decke) -> List[Kante]
```

Wo die Streifen der Platten `platten` -- einer Gruppe mit denselben
Richtungen -- ohne Lager enden: die Stücke ihrer Ränder ohne
Linienlager darauf und ohne eine Platte der Gruppe daneben, je
`(a, b)` mit der Platte links, mindestens so lang wie ein Band breit.

### _ueber_stuetze

```python
def _ueber_stuetze(stuetze: Stuetze, r: Richtung, decke: Decke, stuecke: Stuecke) -> Optional[Unterzug]
```

Das Band über der Stütze in Richtung `r`, über alle Stützen auf seinem
Weg bis zum nächsten anderen Lager oder zum Rand der Platte -- `None`,
wo schon eines über ihr liegt oder es nicht zwei Lager fände.

### _in_der_platte

```python
def _in_der_platte(tau: float, s: float, r: Richtung, breite: float, stuecke: Stuecke) -> float
```

Wo ein Band in Richtung `r` über der Stütze bei `(s, tau)` quer liegt:
durch ihre Mitte -- steht sie näher am Rand als eine halbe Bandbreite,
so weit innen, dass es ganz in der Platte liegt, die Mitte noch darin.
Ist die Platte dort schmaler als das Band, mitten über ihr.

### _am_rand

```python
def _am_rand(a: Punkt, b: Punkt, richtungen: Tuple[Richtung, Richtung], decke: Decke, stuecke: Stuecke) -> Optional[Unterzug]
```

Das Band am offenen Rand `a → b` (die Platte links), innen an ihm und
beidseits bis zum nächsten Lager -- `None`, wo es nicht zwei fände.
Liegt der Rand fast in einer Richtung der Platte ([[opencivil.decke.baender#Konstanten|WINKEL]]), läuft
das Band genau in ihr.

### _bis_zum_lager

```python
def _bis_zum_lager(lager: Sequence[Lager], waende: Sequence[Tuple[float, float]], von: float, bis: float, weit: Tuple[float, float]) -> Optional[Tuple[float, float]]
```

Das Stück `von → bis`, beidseits verlängert über das nächste Lager
hinweg, bis es ganz auf ihm liegt -- ohne Lager bis `weit`, zum Rand
der Platte. Über eine Wand längs (`waende`) läuft es nicht: es endet,
wo sie beginnt; liegt sie schon unter dem Stück selbst, `None`.

### _waende_laengs

```python
def _waende_laengs(r: Richtung, tau: float, decke: Decke) -> List[Tuple[float, float]]
```

Von wo bis wo, in `s` von `r`, Wände längs im Weg eines Bands quer
bei `tau` liegen -- auch auf seinem Rand.

### _quer_gehalten

```python
def _quer_gehalten(a: Punkt, b: Punkt, richtungen: Tuple[Richtung, Richtung], decke: Decke, eigene: Stuecke, stuecke: Stuecke) -> bool
```

Ob die Streifen, die am Rand `a → b` enden, sonst ein Lager haben:
ein Feldstreifen quer durch die Mitte des Rands, über die Platten
`eigene` der Gruppe, wie die Zerlegung ihn lagerte.

### _gepruft

```python
def _gepruft(band: Unterzug, decke: Decke, stuecke: Stuecke) -> Optional[Unterzug]
```

Das Band, wenn kein Unterzug längs auf seinem Weg liegt und jedes Stück auf zwei Lagern liegt -- sonst `None`.

### _lager

```python
def _lager(band: Unterzug, decke: Decke, stuecke: Stuecke) -> List[List[Lager]]
```

Je Träger des Bands die Lager, die seine Höhe halten -- wie die Zerlegung sie fände.

### _ueber_platten

```python
def _ueber_platten(r: Richtung, tau: float, breite: float, stuecke: Stuecke, bei: float) -> Optional[Tuple[float, float]]
```

Wie weit ein Band quer bei `tau` längs über die Platten reicht, in
`s` von `r` -- das Stück, in dem `bei` liegt; `None`, wenn dort
keine Platte ist.

### _richtungen_bei

```python
def _richtungen_bei(stuetze: Stuetze, decke: Decke, stuecke: Stuecke) -> List[Richtung]
```

Die Richtungen der Platten, auf denen die Stütze steht -- parallele einmal.

### _ueberdeckt

```python
def _ueberdeckt(band: Unterzug, andere: Sequence[Unterzug]) -> bool
```

Ob ein Unterzug längs auf dem Weg des Bands liegt -- dann ersetzt er es.

### _band

```python
def _band(r: Richtung, tau: float, laengs: Tuple[float, float], breite: float, stufe: float) -> Unterzug
```

Ein Band in Richtung `r`, quer bei `tau`, längs über `laengs` -- noch ohne Namen.

### _namen

```python
def _namen(decke: Decke) -> Iterator[str]
```

B1, B2, … -- ohne die Namen, die schon ein Teil der Decke trägt.

### _auf

```python
def _auf(k: Kante, s: float) -> Punkt
```

Der Punkt `s` Meter nach dem Anfang des Rands `k`.

### _laengs_zu

```python
def _laengs_zu(u: Union[Unterzug, Linienlager], winkel: float) -> bool
```

Ob `u` in `winkel` läuft, bis auf [[opencivil.decke.baender#Konstanten|WINKEL]].


## Konstanten

- `WINKEL = 0.001` – So nahe an einer Richtung der Platte, in rad, läuft ein Band am Rand in ihr: auf den Millimeter gerundete Ecken legen es nicht schief zu den Streifen. Ebenso nahe gilt ein Unterzug als längs zum Band.
- `NAH = 1e-06` – Was längs eines Bands als dieselbe Stelle gilt, in m.
- `SCHEIBE = 0.001` – Wie dick die Scheibe quer durch eine Stütze ist, in der ein Band sieht, wie breit die Platte dort ist, in m.
- `Lager = Tuple[float, float, float, str]` – Ein Lager eines Bands: wo es liegt, von wo bis wo es drückt -- in `s` der Richtung des Bands -- und seine Art.

## Braucht

- [[opencivil.decke.geometrie]]
- [[opencivil.decke.modell]]
- [[opencivil.decke.richtungen]]
- [[opencivil.decke.streifen]]

## Gebraucht von

- [[opencivil.decke.herleitung]]
- [[opencivil.decke.rechnung]]
- [[opencivil.web.deckendaten]]
