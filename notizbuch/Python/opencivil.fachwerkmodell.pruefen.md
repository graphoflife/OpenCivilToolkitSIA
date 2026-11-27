---
erzeugt: 74da990a8b7d
art: modul
tags: [modul]
---
> [!abstract] opencivil/fachwerkmodell/pruefen.py
> was einem Fachwerkmodell fehlt oder an ihm nicht stimmt.
> Paket [[opencivil.fachwerkmodell]] · [Quelltext](../../opencivil/fachwerkmodell/pruefen.py)

## VERANTWORTUNG

Die Meldungen eines Modells, bevor ein Fachwerk gesucht wird, in dieser
Folge:

- ein Umriss, aus dem sich nicht rechnen lässt – zu wenig Ecken, sich
  selbst kreuzend, ohne Fläche: rot;
- noch keine Scheibe: grau;
- ein Loch neben jeder Scheibe: ein Hinweis, es nimmt nichts weg;
- ein Lager oder eine Last neben der Scheibe oder in einem Loch: rot;
- noch kein Lager, oder Lager, die die Scheibe noch nicht halten – sie
  könnte sich verschieben oder drehen: grau, mit der Bewegung, die bleibt;
- keine Last: grau, «Keine Last → kein Fachwerk.».

Was nur fehlt, steht grau und hält die Rechnung an; was falsch ist, steht
rot (Benutzer, 2026-11-19). Ein Fachwerk braucht beides nicht: es
genügt, dass die Lager die Scheibe als starren Körper halten.


## DIE LAGER HALTEN DIE SCHEIBE, WENN

keine Bewegung der starren Scheibe – verschoben um `(u, v)`, gedreht um
`θ` – jedes Lager in seiner Richtung stehen lässt. Ein Lager bei
`(x, y)`, fest in x, verlangt `u − θ·y = 0`, fest in y `v + θ·x = 0`;
drei unabhängige solche Gleichungen halten sie. Sind es weniger, sagt die
Bewegung, die bleibt, was fehlt: eine Verschiebung oder eine Drehung um
einen Punkt – etwa um das einzige Lager.

## Inhalt

### pruefen

```python
def pruefen(modell: Modell) -> List[Meldung]
```

Siehe Dateikopf – leer, wenn sich ein Fachwerk suchen lässt.

### _umriss

```python
def _umriss(u: Umriss) -> Optional[Meldung]
```

Was an einem Umriss nicht stimmt – rot, mit seinem Namen.

### _ohne_material

```python
def _ohne_material(modell: Modell, ort: geo.Punkt) -> str
```

Warum bei `ort` kein Material ist, als Satzteil – leer, wenn welches da ist.

### _ueberlappen

```python
def _ueberlappen(a: Umriss, b: Umriss) -> bool
```

Ob zwei Umrisse Fläche gemeinsam haben – auch wenn einer ganz im
anderen liegt; berühren sie sich nur am Rand, nicht. Je zwei ihrer
konvexen Stücke ([[opencivil.decke.geometrie#dreiecke|dreiecke]])
geschnitten: `a` und `b` sind geprüft, sie kreuzen sich nicht selbst.

### beweglich

```python
def beweglich(lager: Sequence[Lager]) -> str
```

Wie sich die starre Scheibe trotz `lager` noch bewegen kann, als
Satzteil nach «sie kann sich» – leer, wenn die Lager sie halten.

### _gleichungen

```python
def _gleichungen(lager: Sequence[Lager]) -> Tuple[List[List[float]], geo.Punkt, float]
```

Je Richtung, in der ein Lager hält, die Zeile `(u, v, θ)` seiner
Gleichung – in Koordinaten um die Mitte der Lager, geteilt durch ihre
Ausdehnung, damit die Schranke nicht von der Grösse abhängt. Dazu Mitte
und Ausdehnung.

### _rang

```python
def _rang(zeilen: List[List[float]]) -> Tuple[int, Optional[Tuple[float, float, float]]]
```

Der Rang der Zeilen – und bei Rang 2 die Bewegung, die sie stehen
lassen: das Kreuzprodukt zweier unabhängiger Zeilen.


## Konstanten

- `SCHRANKE = 1e-09` – Unter dieser Zahl gilt ein Rest der Gleichungen der Lager als null – in Koordinaten, die auf die Grösse der Lagerung bezogen sind.
- `KEINE_KRAFT = 1e-09` – Ab dieser Kraft in N zählt eine Last – darunter ist sie null.

## Braucht

- [[opencivil.decke.geometrie]]
- [[opencivil.decke.herleitung]]
- [[opencivil.fachwerkmodell.modell]]
- [[opencivil.querschnitt.geometrie]]
- [[opencivil.stabwerk.system]]

## Gebraucht von

- [[opencivil.fachwerkmodell.werk]]
