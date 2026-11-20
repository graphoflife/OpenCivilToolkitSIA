---
erzeugt: 2f4935d5b480
art: modul
tags: [modul]
---
> [!abstract] opencivil/querschnitt/widerstandsflaeche.py
> die Flaeche aller Bruchzustaende, geschnitten.
> Paket [[opencivil.querschnitt]] · [Quelltext](../../opencivil/querschnitt/widerstandsflaeche.py)

## VERANTWORTUNG

Alle Bruchzustaende eines Querschnitts zusammen bilden im Raum
(N, M_y, M_z) eine geschlossene Flaeche; jeder Faecher
([[opencivil.querschnitt.interaktion#Querschnitt.faecher|faecher]]) ist eine
Linie darauf. Das Interaktionsdiagramm der Querschnittsanalyse ist ein
Schnitt durch sie, bei festem N, M_y oder M_z ([[opencivil.querschnitt.widerstandsflaeche#schnitt|schnitt]]). Nur das
Bild liest ihn, kein Nachweis rechnet damit. Bis 2026-11-20 stand er in
[[opencivil.querschnitt.interaktion]].


## EINHEITEN

SI-Basis: Newton und Newtonmeter.

## Inhalt

### schnitt

```python
def schnitt(q: Querschnitt, fest: str, wert: float, neigungen: int=FLAECHE_NEIGUNGEN) -> List[Tuple[float, float, float]]
```

Die Flaeche aller Bruchzustaende im Raum (N, M_y, M_z), geschnitten bei
einem festen Wert von N, M_y oder M_z: ein geschlossener Zug von Punkten
`(N, M_y, M_z)`, auf dem die feste Groesse diesen Wert hat. Leer, wo
die Ebene die Flaeche nicht trifft.

Bei festem N je Neigung der Punkt des Faechers mit diesem N -- dieselbe
Suche wie im Nachweis. Bei festem Moment die Faecher aller Neigungen,
je auf Stufen in N gelesen; auf jeder Stufe schneidet die Gerade des
festen Moments den Umriss in zwei Punkten. Zwischen den Stuetzstellen
eines Faechers wird dabei linear gelesen: genau genug fuer ein Bild,
nachgewiesen wird damit nichts.

### _flaechenstufen

```python
def _flaechenstufen(q: Querschnitt, neigungen: int) -> Stufen
```

Je Stufe in N der Umriss `(M_y, M_z)` ueber alle Neigungen -- aus den
Faechern, einmal je Querschnitt. Die Stufen liegen wie die Knoten von
Tschebyschow zwischen reinem Zug und reinem Druck, ohne die Enden: dort
zieht sich der Umriss auf einen Punkt zusammen.

### _bei_n_gelesen

```python
def _bei_n_gelesen(faecher: Sequence[Bruchpunkt], N: float) -> Punkt
```

`(M_y, M_z)` auf einem Faecher bei diesem N, linear zwischen den beiden
Stuetzstellen, zwischen denen N liegt. Vom Zug zum Druck nimmt N ab.

### _schnittstellen

```python
def _schnittstellen(umriss: Sequence[Punkt], achse: int, wert: float) -> List[float]
```

Wo die Gerade `Punkt[achse] = wert` den geschlossenen Umriss kreuzt --
die andere Koordinate jeder Stelle.


## Konstanten

- `FLAECHE_SCHRITTE = 8` – Stuetzstellen je Abschnitt fuer die Flaeche der Widerstaende -- weniger als fuer eine Linie; die Luecken fuellt das Halbieren.
- `FLAECHE_NEIGUNGEN = 72` – Neigungen, mit denen die Flaeche der Widerstaende abgetastet wird -- alle 5°.
- `SCHNITT_STUFEN = 120` – Stufen in N, auf denen die Flaeche bei festem Moment geschnitten wird. Zu den Enden hin dichter, wo sie sich zum reinen Zug und Druck schliesst.
- `GROESSEN = ('N', 'M_y', 'M_z')` – Wonach geschnitten werden kann.
- `Stufen = List[Tuple[float, List[Punkt]]]` – Je Stufe in N der Umriss `(M_y, M_z)` ueber alle Neigungen.
- `_STUFEN = WeakKeyDictionary()` – Die Stufen je Querschnitt und Zahl der Neigungen, solange es den Querschnitt gibt: ein anderer Schnitt durch dieselbe Flaeche liest dieselben Faecher. Bis 2026-11-20 trug der Querschnitt sie selbst.

## Braucht

- [[opencivil.querschnitt.interaktion]]

## Gebraucht von

- [[opencivil.web.diagrammdaten]]
- [[opencivil.web.dienst]]
