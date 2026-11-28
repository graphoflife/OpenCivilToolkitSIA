---
erzeugt: fc4be8c5633d
art: modul
tags: [modul]
---
> [!abstract] opencivil/fachwerkmodell/form.py
> das Verfahren SIMP: die steifste Form, und aus ihr ein Fachwerk.
> Paket [[opencivil.fachwerkmodell]] · [Quelltext](../../opencivil/fachwerkmodell/form.py)

## VERANTWORTUNG

Die Suche des Verfahrens SIMP, Schritt um Schritt, wie die der Ground
Structure Runde um Runde ([[opencivil.fachwerkmodell.form#schritte|schritte]]): das Material verteilt sich
zur steifsten Form ([[opencivil.fachwerkmodell.simp|simp]]). Ist sie
fertig, oder hält jemand an, liest das Werkzeug aus ihr ein Fachwerk
([[opencivil.fachwerkmodell.skelett|skelett]]), und die Optimierung der
Ground Structure bestimmt seine Kräfte
([[opencivil.fachwerkmodell.suche#optimum|optimum]], danach ohne die dünnen
Stäbe, [[opencivil.fachwerkmodell.suche#nachbearbeiten|nachbearbeiten]]).


## FERTIG

wenn sich in einem Schritt keine Dichte um mehr als [[opencivil.fachwerkmodell.form#Konstanten|GENUG]] ändert
– so hört auch die Quelle auf –, spätestens nach
[[opencivil.fachwerkmodell.form#Konstanten|HOECHSTENS_SCHRITTE]] Schritten (nach Vorgabe, nicht nachgeschlagen).


## DER ZUSTAND

Zwischen zwei Anfragen die Dichten, zu welchem Modell und nach welchem
Schritt ([[opencivil.fachwerkmodell.form#Formzustand|Formzustand]]); die Seite hält ihn wie den der Ground
Structure. Eine Anfrage rechnet Schritte, bis [[opencivil.fachwerkmodell.form#Konstanten|SEKUNDEN]] um sind:
so zeigt die Seite die Form wachsen, gleich wie schnell sie rechnet. Was
herauskommt, hängt nicht daran – jeder Schritt folgt nur aus den Dichten
davor. Das Netz bleibt hier im Speicher ([[opencivil.fachwerkmodell.form#_netz|_netz]]).


## DAS BILD DER FORM

Je Feld des Rechtecks um die Scheiben ein Zeichen, Zeile um Zeile von
unten: «-», wo kein Element ist, sonst die gefilterte Dichte in
Fünfzehnteln, «0» bis «f» ([[opencivil.fachwerkmodell.form#formtext|formtext]]). So steht sie kurz im
Projekt, und die Seite zeichnet sie.

## Inhalt

### Formeinstellung

```python
@dataclass(frozen=True)
class Formeinstellung
```

Das Verfahren SIMP: seine vier Zahlen in SI.

- `verfahren: ClassVar[Verfahren] = Verfahren.SIMP`
- `zug_achsparallel: ClassVar[bool] = False` – Den Schalter hat nur die Ground Structure: die Form kennt keine Richtung des Zugs.
- `weite: float` – Die Netzweite h in m.
- `volumen: float` – Der Anteil des Materials an der Fläche: 0.3 ist 30 %.
- `w_Z: float` – Das Gewicht des Zugs im Fachwerk; Druck zählt 1.
- `N_min: float` – Die kleinste Stabkraft als Teil der grössten: 0.01 ist 1 %.

### Formzustand

```python
@dataclass(frozen=True)
class Formzustand
```

Was von einer Anfrage zur nächsten geht.

- `abdruck: str`
- `schritt: int` – Wie viele Schritte gerechnet sind.
- `dichte: Tuple[float, ...]` – Je Element seine Dichte nach dem Schritt, ungefiltert – in der Folge des Netzes.

### Formrunde

```python
@dataclass(frozen=True)
class Formrunde
```

Was eine Anfrage gibt.

- `zustand: Formzustand`
- `form: str` – Das Bild der Form nach dem letzten Schritt (Dateikopf).
- `elemente: int`
- `aenderung: float` – Wie stark sich die Dichten im letzten Schritt höchstens änderten – ohne Schritt unendlich.
- `fertig: bool`
- `ergebnis: Optional[Suchergebnis]` – Das Fachwerk der Form – nur, wenn sie fertig ist oder abgeschlossen wurde.

### schritte

```python
def schritte(modell: Modell, einstellung: Formeinstellung, zustand: Optional[Formzustand], sekunden: float=SEKUNDEN, abschliessen: bool=False) -> Formrunde
```

Die nächsten Schritte, bis `sekunden` um sind, mindestens einer – von
vorn, wenn `zustand` fehlt oder nicht zu Modell und Verfahren passt.
Mit `abschliessen` keiner mehr: das Fachwerk der Form, wie sie ist,
angehalten. Das Modell ist geprüft; wirft
[[opencivil.fachwerkmodell.simp#NetzFehler|NetzFehler]].

### ganz_formen

```python
def ganz_formen(modell: Modell, einstellung: Formeinstellung) -> Suchergebnis
```

Schritt um Schritt bis zum Ende, wie die Seite sucht – nur ohne Bild dazwischen.

### _fachwerk

```python
def _fachwerk(n: Netz, x: Sequence[float], einstellung: Formeinstellung, rahmen: Suchergebnis) -> Suchergebnis
```

Das Fachwerk der Form mit den Dichten `x`: die möglichen Stäbe aus
ihren Mittellinien, die Kräfte aus der Optimierung – in `rahmen`,
was es sonst sagt.

### formtext

```python
def formtext(n: Netz, x: Sequence[float]) -> str
```

Das Bild der Form mit den Dichten `x` – siehe Dateikopf.

### _netz

```python
@lru_cache(maxsize=2)
def _netz(modell: Modell, weite: float) -> Netz
```

Das Netz, aus dem Speicher, wenn es zu Modell und Netzweite schon gebaut ist.


## Konstanten

- `QUELLE = simp.QUELLE` – Wo das Verfahren nachzulesen ist und wo das Lesen der Form.
- `QUELLE_SKELETT = skelett.QUELLE`
- `GENUG = 0.01` – Fertig, wenn sich keine Dichte in einem Schritt um mehr als so viel ändert.
- `HOECHSTENS_SCHRITTE = 200` – Wie viele Schritte höchstens – nach Vorgabe, nicht nachgeschlagen.
- `SEKUNDEN = 1.0` – Wie lange eine Anfrage rechnet, in s – nach Vorgabe.
- `STUFEN = '0123456789abcdef'` – Die Zeichen der Dichte im Bild der Form: «0» leer bis «f» voll.

## Braucht

- [[opencivil.fachwerkmodell.modell]]
- [[opencivil.fachwerkmodell.simp]]
- [[opencivil.fachwerkmodell.skelett]]
- [[opencivil.fachwerkmodell.suche]]
- [[opencivil.fachwerkmodell.verfahren]]

## Gebraucht von

- [[opencivil.fachwerkmodell.herleitung]]
- [[opencivil.fachwerkmodell.werk]]
- [[opencivil.projekt.aufbau.fachwerkmodell]]
- [[opencivil.projekt.fachwerkmodell]]
- [[opencivil.web.fachwerkdaten]]
