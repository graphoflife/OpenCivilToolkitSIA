---
erzeugt: a90da0107868
art: modul
tags: [modul]
---
> [!abstract] opencivil/fachwerkmodell/suche.py
> das leichteste Fachwerk, Runde um Runde.
> Paket [[opencivil.fachwerkmodell]] · [Quelltext](../../opencivil/fachwerkmodell/suche.py)

## VERANTWORTUNG

Die Suche des Verfahrens Ground Structure nach He, Gilbert & Song (2019),
Abschnitt 3: eine Optimierung über einen Teil der möglichen Stäbe
([[opencivil.fachwerkmodell.optimierung|optimierung]]), dann die Stäbe dazu, die
das Fachwerk leichter machten – bis keiner mehr fehlt ([[opencivil.fachwerkmodell.suche#runde|runde]]).
Dann ist es das Fachwerk, das die Optimierung über alle möglichen Stäbe
fände. Jede Runde gibt ein Fachwerk im Gleichgewicht ([[opencivil.fachwerkmodell.suche#nachbearbeiten|nachbearbeiten]]);
wer die Suche anhält, hat das der letzten.


## DIE RUNDEN

- In der ersten die kurzen Stäbe, höchstens 1.5 h lang: je Knoten seine
  Nachbarn im Raster, auch schräg (nach Vorgabe, nicht nachgeschlagen).
- Nach jeder Optimierung je Stab ausserhalb seine Dehnung im Feld der
  virtuellen Verschiebungen. Liegt sie über w_Z oder unter −w_D, verletzt
  er die Bedingung, und das Fachwerk würde mit ihm leichter. Die am
  stärksten verletzen, kommen dazu – so viele, wie Gl. (7) sagt, mit
  α = β = 0.05.
- Fertig, wenn keiner mehr verletzt.


## DER ZUSTAND

Zwischen zwei Runden: welche Stäbe im Modell sind, zu welchem Modell
([[opencivil.fachwerkmodell.suche#Suchzustand|Suchzustand]]). Die Seite hält ihn und schickt ihn mit der nächsten
Anfrage zurück. Die Grundstruktur bleibt hier im Speicher
([[opencivil.fachwerkmodell.suche#_grundstruktur|_grundstruktur]]): sie folgt aus dem Modell und der Rasterweite.


## DIE NACHBEARBEITUNG

Ein Innere-Punkte-Verfahren endet innen: jeder Stab trägt ein wenig, und wo
mehrere Fachwerke gleich leicht sind, trägt jedes einen Teil. Darum fallen
die Stäbe unter N_min der grössten Kraft weg, und die Optimierung sucht das
Gleichgewicht ohne sie neu – und wieder, bis keiner mehr wegfällt. Geht
es ohne sie nicht auf, versucht sie es mit der halben Schwelle: was dann
bleibt, braucht das Gleichgewicht ([[opencivil.fachwerkmodell.suche#_ohne_duenne|_ohne_duenne]]). Zuletzt werden
zwei Stäbe in einer Flucht einer, wo zwischen ihnen nur ein Knoten ohne
Last und Lager liegt.


## DER ABDRUCK

Woran ein gefundenes Fachwerk sein Modell erkennt ([[opencivil.fachwerkmodell.suche#abdruck|abdruck]]): die
ganze Scheibe mit Lagern und Lasten und die drei Zahlen des Verfahrens.
Ändert sich eines, gehört das Fachwerk zu einem früheren Stand.

## Inhalt

### Einstellung

```python
@dataclass(frozen=True)
class Einstellung
```

Die drei Zahlen des Verfahrens in SI.

- `weite: float` – Die Rasterweite h in m.
- `w_Z: float` – Das Gewicht des Zugs; Druck zählt 1.
- `N_min: float` – Die kleinste Stabkraft als Teil der grössten: 0.01 ist 1 %.

### Suchzustand

```python
@dataclass(frozen=True)
class Suchzustand
```

Was von einer Runde zur nächsten geht.

- `abdruck: str`
- `runde: int` – Die Nummer der Runde, die ihn gab.
- `aktiv: Tuple[int, ...]` – Die Stäbe im Modell der nächsten Runde, als Platz in der Grundstruktur.

### Fachwerk

```python
@dataclass(frozen=True)
class Fachwerk
```

Ein Fachwerk im Gleichgewicht: Knoten in m, Stäbe von Knoten zu Knoten mit der Kraft in N, Zug positiv.

- `knoten: Tuple[Punkt, ...]`
- `staebe: Tuple[Tuple[int, int, float], ...]`

### Suchergebnis

```python
@dataclass(frozen=True)
class Suchergebnis
```

Das Fachwerk einer Runde und woher es kommt – so steht es im Projekt.

- `fachwerk: Fachwerk`
- `abdruck: str`
- `runden: int` – Die Nummer der Runde, die es gab.
- `fertig: bool` – Ob die Suche zu Ende kam – sonst wurde sie angehalten.
- `moeglich: int` – Wie viele Stäbe die Grundstruktur hat.
- `im_modell: int` – Wie viele Stäbe in dieser Runde im Modell waren.

### Runde

```python
@dataclass(frozen=True)
class Runde
```

Was eine Runde gibt.

- `ergebnis: Suchergebnis`
- `zustand: Suchzustand` – Für die nächste – nach der letzten ohne Bedeutung.
- `dazu: int` – Wie viele Stäbe für die nächste dazukommen.

### abdruck

```python
def abdruck(modell: Modell, einstellung: Einstellung) -> str
```

Siehe Dateikopf: 16 Zeichen, gleich für gleiche Eingaben – auch in Pyodide.

### runde

```python
def runde(modell: Modell, einstellung: Einstellung, zustand: Optional[Suchzustand]) -> Runde
```

Die nächste Runde der Suche – die erste, wenn `zustand` fehlt oder
nicht zu Modell und Verfahren passt: ein anderer Abdruck, Stäbe, die es
nicht gibt, einer doppelt. Das Modell ist geprüft; wirft
[[opencivil.fachwerkmodell.grundstruktur#ZuVieleKnoten|ZuVieleKnoten]], wenn das
Raster zu fein ist.

### ganz_suchen

```python
def ganz_suchen(modell: Modell, einstellung: Einstellung) -> Suchergebnis
```

Runde um Runde bis zum Ende, wie die Seite sucht – nur ohne Bild dazwischen.

### _optimum

```python
def _optimum(gs: Grundstruktur, aktiv: Sequence[int], einstellung: Einstellung, skala: float) -> Optimum
```

Die Optimierung über die Stäbe `aktiv`, die Lasten bezogen auf die grösste.

### _strafe

```python
def _strafe(gs: Grundstruktur, einstellung: Einstellung) -> float
```

Was ein Rest des Gleichgewichts je Einheit kostet: tausendmal mehr, als
die Kraft der Einheit über die Diagonale der Scheibe zu tragen kostet –
so viel kostet kein Weg durch die Stäbe (nach Vorgabe).

### _verletzt

```python
def _verletzt(gs: Grundstruktur, aktiv: Sequence[int], u: Sequence[float], einstellung: Einstellung) -> Dict[int, float]
```

Je Stab ausserhalb, der die Bedingung verletzt, um wie viel: seine Dehnung durch die erlaubte.

### nachbearbeiten

```python
def nachbearbeiten(gs: Grundstruktur, aktiv: Sequence[int], opt: Optimum, einstellung: Einstellung, skala: float, gruendlich: bool) -> Fachwerk
```

Das Fachwerk der Runde, wie der Dateikopf es beschreibt: ohne die
dünnen Stäbe, im Gleichgewicht neu gesucht, und mit einem Stab statt
zweien in einer Flucht. Nur `gruendlich` – in der letzten Runde –
wird neu gesucht, bis keiner mehr wegfällt; sonst einmal, und geht es
ohne die dünnen nicht auf, bleiben sie: die Runden davor zeigen nur,
wie die Suche vorankommt, und jede weitere Optimierung kostete in jeder
Runde Zeit.

### _ohne_duenne

```python
def _ohne_duenne(gs: Grundstruktur, kraefte: Dict[int, float], einstellung: Einstellung, skala: float, hoechstens: int) -> Dict[int, float]
```

Die Kräfte je Stab ohne die dünnen: die unter der Schwelle fallen weg,
und die Optimierung sucht das Gleichgewicht ohne sie neu – mit N_min
wieder von vorn, bis keiner mehr wegfällt. Geht es ohne sie nicht auf,
gilt die halbe Schwelle. Höchstens `hoechstens` Mal neu gesucht.
Beispiel: die Wandscheibe im Raster von
0.55 m geht ohne die Stäbe unter 1 % nicht auf, ohne die unter 0.25 %
schon – 62 statt 111 Stäbe, gleich leicht.

### _zusammengelegt

```python
def _zusammengelegt(knoten: Sequence[Punkt], staebe: List[Tuple[int, int, float]], fest: set) -> List[Tuple[int, int, float]]
```

Zwei Stäbe in einer Flucht als einer, wo zwischen ihnen nur ein Knoten
ohne Last und Lager liegt – ihre Kräfte sind im Gleichgewicht gleich;
der eine trägt ihr Mittel.

### _in_flucht

```python
def _in_flucht(knoten: Sequence[Punkt], k: int, s1: Tuple[int, int, float], s2: Tuple[int, int, float]) -> bool
```

Ob zwei Stäbe an Knoten `k` in einer Flucht weiterlaufen.

### _gefasst

```python
def _gefasst(knoten: Sequence[Punkt], staebe: Sequence[Tuple[int, int, float]]) -> Fachwerk
```

Nur die Knoten, an denen ein Stab hängt, neu gezählt; die Stäbe nach der Grösse ihrer Kraft.

### _grundstruktur

```python
def _grundstruktur(modell: Modell, weite: float) -> Grundstruktur
```

Die Grundstruktur, aus dem Speicher, wenn sie zu Modell und Rasterweite schon gebaut ist.


## Konstanten

- `QUELLE = 'He, Gilbert & Song (2019), Abschnitt 3, Gl. (7)'` – Wo die Suche nachzulesen ist.
- `VORGABEN = (Gruppe('Verfahren', lambda: (Feld('rasterweite', 'h', M, 'Abstand de…` – Die Zahlen des Verfahrens, in der Maske eine Kachel, in der Herleitung ein Kasten.
- `KURZ = 1.5` – Wie lang die Stäbe der ersten Runde höchstens sind, in Rasterweiten – nach Vorgabe.
- `ALPHA = 0.05` – α und β aus Gl. (7): wie viele der verletzenden Stäbe je Runde dazukommen.
- `VERLETZT_AB = 0.0001` – Ab wann ein Stab die Bedingung verletzt: 1 + diese Zahl.
- `W_DRUCK = 1.0` – Das Gewicht des Drucks: die Einheit, gegen die w_Z zählt.
- `OFFEN_HOECHSTENS = 1e-06` – Was vom Gleichgewicht offen bleiben darf, bezogen auf die grösste Last – nach Vorgabe. Mit derselben Grenze prüft die Nachrechnung das gefundene Fachwerk.
- `NULL = 1e-09` – Unter diesem Teil der grössten Kraft trägt ein Stab nichts.
- `NEU_HOECHSTENS = 30` – Wie oft die Nachbearbeitung höchstens neu optimiert – nach Vorgabe, nicht nachgeschlagen.
- `_GEBAUT = OrderedDict()` – Die zuletzt gebauten Grundstrukturen, nach Modell und Rasterweite.
- `_PLAETZE = 2` – Wie viele es höchstens behält.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.vorgaben]]
- [[opencivil.decke.geometrie]]
- [[opencivil.fachwerkmodell.grundstruktur]]
- [[opencivil.fachwerkmodell.modell]]
- [[opencivil.fachwerkmodell.optimierung]]

## Gebraucht von

- [[opencivil.fachwerkmodell.herleitung]]
- [[opencivil.fachwerkmodell.nachrechnung]]
- [[opencivil.fachwerkmodell.werk]]
- [[opencivil.projekt.aufbau.fachwerkmodell]]
- [[opencivil.projekt.fachwerkmodell]]
- [[opencivil.web.api]]
- [[opencivil.web.fachwerkdaten]]
