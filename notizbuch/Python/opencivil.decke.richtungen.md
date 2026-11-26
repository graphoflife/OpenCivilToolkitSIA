---
erzeugt: 6a8268ac9a67
art: modul
tags: [modul]
---
> [!abstract] opencivil/decke/richtungen.py
> die zwei Richtungen, die eine Platte selbst wählt.
> Paket [[opencivil.decke]] · [Quelltext](../../opencivil/decke/richtungen.py)

## VERANTWORTUNG

Für jede Platte mit `von_selbst` ([[opencivil.decke.modell#Platte|Platte]])
Richtung 1 und 2 der Lastabtragung, entlang ihrer Ränder -- bevor die Decke
in Streifen zerfällt ([[opencivil.decke.rechnung#rechnen|rechnen]]). Die übrigen
Platten behalten ihre Richtungen, wie der Benutzer sie gab.


## DIE REGEL

* Platten, die von selbst wählen und aneinanderstossen -- ein Stück Rand
  gemeinsam haben, nicht nur eine Ecke --, bekommen dieselben Richtungen,
  damit ihre Streifen über die Fuge laufen. Eine Platte mit Richtungen von
  Hand ändert nichts an denen daneben.
* Richtung 1 läuft parallel zu den meisten Metern Rand; ein Rand quer dazu
  zählt mit, denn Richtung 2 steht rechtwinklig auf ihr. Es zählt der Rand
  einer Gruppe nach aussen, keine Fuge in ihr. Richtung 1 liegt über −45°
  bis 45° gegen x; bei gleich vielen Metern gilt die näher an x.
* Nach Vorgabe, nicht nachgeschlagen: die Norm lässt jede Aufteilung der
  Last zu, die im Gleichgewicht ist (SIA 262:2025, 4.1.4.2.2). Geplant war
  der nach Länge gewichtete Mittelwert der Randrichtungen. Er legte die
  Streifen eines Trapezes mit einem schiefen Rand schief zu allen Rändern:
  unten 6 m, oben 4 m, 5 m hoch, auf −4.9° statt auf 0°.

## Inhalt

### festgelegt

```python
def festgelegt(decke: Decke) -> Decke
```

Die Decke, in der jede Platte mit `von_selbst` ihre Richtungen gewählt hat -- die übrigen, wie sie sind.

### entlang

```python
def entlang(raender: Sequence[Tuple[float, float]]) -> Tuple[float, float]
```

Richtung 1 und 2 in rad zu Rändern, je `(Winkel, Länge)`: Richtung 1
parallel zu den meisten Metern -- ein Rand quer dazu zählt mit --, über
−45° bis 45°; bei gleich vielen Metern die näher an x. Ohne Rand x und y.

### raender

```python
def raender(platten: Sequence[Platte]) -> List[Tuple[float, float]]
```

Je Rand der Platten sein Winkel in rad und seine Länge nach aussen, in m -- was in einer Fuge liegt, zählt nicht.

### gemeinsam

```python
def gemeinsam(k: Kante, m: Kante) -> float
```

Wie lang zwei Ränder aufeinander liegen, in m -- null, wenn sie sich nur kreuzen oder an einer Ecke treffen.

### _gruppen

```python
def _gruppen(platten: Sequence[Platte]) -> List[List[int]]
```

Die Platten, die aneinanderstossen, je in einer Gruppe -- als Stellen in `platten`, in ihrer Folge.

### kanten

```python
def kanten(p: Platte) -> List[Kante]
```

Die Ränder der Platte im Gegenuhrzeigersinn -- innen liegt links.

### _abstand

```python
def _abstand(v: float, w: float) -> float
```

Wie weit zwei Winkel auseinander liegen, über 90° gefaltet -- −45° und 45° sind derselbe.


## Konstanten

- `FUGE = 1e-06` – So nahe liegen zwei Ränder einer Fuge mindestens beieinander, in m -- und so lang ist sie mindestens.
- `GLEICH = 1e-06` – Unter diesem Winkel laufen zwei Ränder gleich, in rad -- wie [[opencivil.decke.streifen#Konstanten|PARALLEL]].

## Braucht

- [[opencivil.decke.geometrie]]
- [[opencivil.decke.modell]]

## Gebraucht von

- [[opencivil.decke.baender]]
- [[opencivil.decke.rechnung]]
