---
erzeugt: 02a83c013073
art: modul
tags: [modul]
---
> [!abstract] opencivil/decke/geometrie.py
> Vielecke in der Ebene der Decke.
> Paket [[opencivil.decke]] · [Quelltext](../../opencivil/decke/geometrie.py)

## VERANTWORTUNG

Was die Streifenmethode an Geometrie braucht, und nur das: Fläche,
Schwerpunkt und Umlaufsinn eines Vielecks, ob ein Punkt darin liegt, die
Zerlegung in Dreiecke, das Abschneiden an einer Halbebene und an einem
konvexen Vieleck, und die Breite eines konvexen Vielecks quer zu einer
Richtung -- das Stück einer Last, das ein Streifen trägt.


## PUNKTE UND VIELECKE

Ein Punkt ist ein Paar `(x, y)` in m, `x` nach rechts, `y` nach oben.
Ein Vieleck ist eine Folge von Punkten ohne Wiederholung des ersten am Ende.
Was hier ein konvexes Vieleck verlangt, verlangt es im Gegenuhrzeigersinn;
[[opencivil.decke.geometrie#gegen_uhrzeiger|gegen_uhrzeiger]] dreht eines um.


## RICHTUNG UND QUERRICHTUNG

Ein Streifen läuft in Richtung `n`; quer dazu steht `t`, `n` um 90°
im Gegenuhrzeigersinn gedreht. Längs misst `s = p·n`, quer `τ = p·t`.

## Inhalt

### richtung

```python
def richtung(winkel: float) -> Tuple[Punkt, Punkt]
```

`(n, t)` zu einem Winkel gegen die x-Achse, im Gegenuhrzeigersinn.

### skalar

```python
def skalar(p: Punkt, r: Punkt) -> float
```

### flaeche

```python
def flaeche(v: Vieleck) -> float
```

Die Fläche mit Vorzeichen: im Gegenuhrzeigersinn positiv.

### schwerpunkt

```python
def schwerpunkt(v: Vieleck) -> Punkt
```

Der Flächenschwerpunkt -- bei einem entarteten Vieleck das Mittel der Ecken.

### gegen_uhrzeiger

```python
def gegen_uhrzeiger(v: Vieleck) -> List[Punkt]
```

### bereinigt

```python
def bereinigt(v: Vieleck) -> List[Punkt]
```

Ohne doppelte Ecken und ohne Ecken auf einer Geraden mit ihren Nachbarn.

### ist_konvex

```python
def ist_konvex(v: Vieleck) -> bool
```

Ob alle Ecken in dieselbe Richtung abbiegen -- `v` bereinigt.

### innen

```python
def innen(p: Punkt, v: Vieleck) -> bool
```

Ob `p` im Vieleck liegt -- auf dem Rand zählt als innen.

### dreiecke

```python
def dreiecke(v: Vieleck) -> List[List[Punkt]]
```

Ein einfaches Vieleck in konvexe Stücke: ein konvexes bleibt ganz, ein
anderes wird in Dreiecke zerlegt (Ohren abschneiden). Alle Stücke im
Gegenuhrzeigersinn.

### halbebene

```python
def halbebene(v: Vieleck, r: Punkt, c: float) -> List[Punkt]
```

Was von `v` in `p·r <= c` liegt (Sutherland-Hodgman).

### schnitt

```python
def schnitt(v: Vieleck, konvex: Vieleck) -> List[Punkt]
```

`v` geschnitten mit dem konvexen Vieleck `konvex` (Gegenuhrzeigersinn) -- leer, wenn nichts bleibt.

### im_band

```python
def im_band(v: Vieleck, t: Punkt, von: float, bis: float) -> List[Punkt]
```

Was von `v` im Band `von <= p·t <= bis` liegt.

### bereich

```python
def bereich(v: Vieleck, r: Punkt) -> Tuple[float, float]
```

Kleinstes und grösstes `p·r` über die Ecken.

### breite

```python
def breite(v: Vieleck, n: Punkt) -> List[Tuple[float, float]]
```

Wie breit das konvexe Vieleck quer zu `n` ist, längs `s = p·n`: die
Paare `(s, b)` an jeder Ecke, aufsteigend in `s`. Dazwischen ist die
Breite linear -- die Ränder eines konvexen Vielecks sind dort Geraden.
Eine Kante quer zu `n` am Anfang oder Ende zählt dort mit ihrer Länge.

### strecke_in_konvex

```python
def strecke_in_konvex(a: Punkt, b: Punkt, konvex: Vieleck) -> Optional[Tuple[float, float]]
```

Welcher Teil der Strecke `a → b` im konvexen Vieleck liegt, als
Parameter `(u0, u1)` mit `p = a + u·(b - a)` -- `None`, wenn keiner
(Cyrus-Beck).

### strecke_im_vieleck

```python
def strecke_im_vieleck(a: Punkt, b: Punkt, v: Vieleck) -> List[Tuple[float, float]]
```

Welche Teile der Strecke `a → b` im Vieleck liegen -- auch einem nicht
konvexen --, als Parameter `(u0, u1)`. Ein Stück auf dem Rand zählt.

### schnittstellen

```python
def schnittstellen(a: Punkt, b: Punkt, v: Vieleck) -> List[float]
```

Wo die Strecke `a → b` den Rand des Vielecks trifft oder an einer Ecke
vorbeigeht, als Parameter in `[0, 1]` -- mit 0 und 1, aufsteigend.
Zwischen zwei Stellen liegt sie ganz innen, ganz aussen oder ganz auf dem Rand.

### rechteck

```python
def rechteck(a: Punkt, b: Punkt, breite_: float) -> List[Punkt]
```

Das Rechteck um die Strecke `a → b`, je `breite_/2` zu beiden Seiten -- im Gegenuhrzeigersinn.

### achsrechteck

```python
def achsrechteck(mitte: Punkt, lx: float, ly: float) -> List[Punkt]
```

Das Rechteck `lx × ly` um `mitte`, achsparallel, im Gegenuhrzeigersinn.

### vereinigt

```python
def vereinigt(intervalle: Sequence[Tuple[float, float]]) -> List[Tuple[float, float]]
```

Intervalle, die sich berühren oder überlappen, zu einem.


## Konstanten

- `TOLERANZ = 1e-07` – Was in m als gleich gilt -- das Zeichenfenster rundet auf ein Millionstel.

## Gebraucht von

- [[opencivil.decke.aufteilung]]
- [[opencivil.decke.feld]]
- [[opencivil.decke.herleitung]]
- [[opencivil.decke.lasten]]
- [[opencivil.decke.modell]]
- [[opencivil.decke.rechnung]]
- [[opencivil.decke.streifen]]
- [[opencivil.projekt.aufbau.decke]]
- [[opencivil.web.deckendaten]]
