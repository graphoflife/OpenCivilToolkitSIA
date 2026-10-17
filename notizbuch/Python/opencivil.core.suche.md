---
erzeugt: cc47205cd8c6
art: modul
tags: [modul]
---
> [!abstract] opencivil/core/suche.py
> wo eine steigende Funktion null wird.
> Paket [[opencivil.core]] · [Quelltext](../../opencivil/core/suche.py)

## VERANTWORTUNG

Die Verfahren, mit denen das Werkzeug eine Nullstelle sucht, an einer
Stelle: [[opencivil.core.suche#Halbieren|Halbieren]], [[opencivil.core.suche#Illinois|Illinois]] mit [[opencivil.core.suche#illinois|illinois]] und
[[opencivil.core.suche#eingrenzen|eingrenzen]]. Gesucht wird ueberall dasselbe -- eine Stelle zwischen
zwei Grenzen, an der eine Funktion das Vorzeichen wechselt: die Dehnung, bei
der die Normalkraft stimmt, die Kruemmung zum Moment, der Bruchzustand bei
einer Normalkraft, die Neigung der Nulllinie. Bis 2026-10-17 stand Illinois
zweimal da, im Loeser des Querschnitts und in der Interaktion, und das
Eingrenzen mit wachsenden Schritten zweimal im Loeser.


## HALBIEREN ODER ILLINOIS

Halbieren ist sicher: es findet die Stelle auch, wo die Funktion springt,
und braucht bis auf die Schranke rund vierzig Schritte. Illinois -- eine
Sekante, die abwechselnd von beiden Seiten herankommt -- braucht auf glatten
Stuecken ein Viertel davon: zwischen zwei Knicken der Werkstoffgesetze ist
die Kraft eine Gerade, und dort trifft die Sekante. Springt die Funktion,
findet Illinois eine der Stellen um den Sprung, und welche, haengt am Weg
([[opencivil.nachweis.querschnittsloeser]]).

Wer eine Suche braucht, bekommt sie als Gegenstand ([[opencivil.core.suche#Suche|Suche]]) und
fragt sie zweierlei: ob sie bei der zuletzt gefundenen Stelle anfaengt
([[opencivil.core.suche#Suche|Suche.vom_letzten]]) und ob sie auch dort taugt, wo die Funktion
springt ([[opencivil.core.suche#Suche|Suche.auch_bei_sprung]]). Bis 2026-10-17 waren es
Unterklassen des Loesers, die sich mit einem Schalter an vier Stellen
wieder abschalteten.


## EINHEITEN

Keine -- hier gibt es nur Zahlen.

## Inhalt

### Suche

```python
class Suche(Protocol)
```

Was eine Suche kann und von sich sagt -- [[opencivil.core.suche#Halbieren|Halbieren]] oder [[opencivil.core.suche#Illinois|Illinois]].

- `vom_letzten: bool` – Ob sie bei der zuletzt gefundenen Stelle anfaengt und von dort eingrenzt ([[opencivil.core.suche#eingrenzen|eingrenzen]]) -- das lohnt nur, wo sie nahe am Ziel schnell trifft.
- `auch_bei_sprung: bool` – Ob sie auch dort taugt, wo die Funktion springt -- wo es also mehrere Stellen gibt und welche gefunden wird, am Weg haengt.
- `wie: str` – Wie sie die Stelle findet, in Worten -- fuer die Mitschrift: «durch Halbieren».

#### Suche.finde

```python
def finde(self, f: Callable[[float], Wert], unten: float, oben: float, schranke: float, f_unten: Wert=None, f_oben: Wert=None) -> Wert
```

Wo `f` zwischen `unten` und `oben` null wird.

### Halbieren

```python
class Halbieren
```

Das Fenster halbieren, bis es schmal genug ist. Braucht von ueberall
gleich viele Schritte und faengt darum von vorn an; sicher, auch wo die
Funktion springt: die Stelle haengt nur am Fenster.

- `vom_letzten = False`
- `auch_bei_sprung = True`
- `wie = 'durch Halbieren'`

#### Halbieren.finde

```python
def finde(self, f: Callable[[float], Wert], unten: float, oben: float, schranke: float, f_unten: Wert=None, f_oben: Wert=None) -> Wert
```

Wo `f` zwischen `unten` und `oben` null wird -- `f` steigt,
unten ist es negativ, oben nicht. Halbiert, bis das Fenster schmaler
ist als `schranke`; `None`, wenn `f` unterwegs keinen Wert hat.
`f_unten` und `f_oben` braucht das Halbieren nicht -- sie sind fuer
eine Suche, die mit ihnen schneller ist ([[opencivil.core.suche#Illinois|Illinois]]).

### Illinois

```python
class Illinois
```

Regula falsi mit der Illinois-Abwandlung: der naechste Punkt liegt, wo die
Sekante durch die beiden Enden null wird, und bleibt ein Ende zweimal
hintereinander stehen, wird sein Wert halbiert -- sonst kroeche die
Sekante an einer gekruemmten Funktion nur von einer Seite heran. Bleibt
eingegrenzt wie das Halbieren, konvergiert auf glatten Stuecken aber fast
so schnell wie das Sekantenverfahren -- am schnellsten, wo es nahe der
Stelle anfaengt: darum bei der zuletzt gefundenen.

Springt die Funktion, findet es eine der Stellen um den Sprung, und
welche, haengt am Weg -- von der zuletzt gefundenen Stelle aus also an
der Reihenfolge der Fragen. Taugen soll es dort nur, wo das nicht zaehlt:
`auch_bei_sprung` fuer eine Suche, die je Frage frisch anfaengt.

- `vom_letzten = True`
- `wie = 'mit dem Illinois-Verfahren, einer Sekante, die abwechselnd von beide…`

#### Illinois.finde

```python
def finde(self, f: Callable[[float], Wert], unten: float, oben: float, schranke: float, f_unten: Wert=None, f_oben: Wert=None) -> Wert
```

Wie [[opencivil.core.suche#Halbieren.finde|Halbieren.finde]]: wo `f` zwischen `unten` und `oben`
null wird, bis das Fenster schmaler ist als `schranke` -- zurueck
kommt die zuletzt gefundene Stelle. Die Werte an den Enden werden
gebraucht; wer sie schon kennt, gibt sie mit.

### illinois

```python
def illinois(f: Callable[[float], Tuple[float, Optional[B]]], a: float, fa: float, b: float, fb: float, *, schranke_x: float, schranke_f: float) -> Optional[B]
```

Eine Nullstelle von `f` zwischen `a` und `b`, die verschiedene
Vorzeichen haben -- mit [[opencivil.core.suche#Illinois|Illinois]], aber fuer eine Frage, die mehr
als die Stelle braucht: `f` gibt `(Wert, Beigabe)` zurueck, und
zurueck kommt die Beigabe der besten Stelle -- `None`, wenn schon die
erste keinen Wert hat. Fertig ist die Suche, sobald der Wert unter
`schranke_f` liegt oder das Fenster unter `schranke_x`.

Hat `f` an einer Stelle keinen Wert (`nan`), endet die Suche dort: ohne
ihn laesst sich nicht weiter eingrenzen. Bis 2026-10-17 rechnete sie mit
`nan` weiter, bis eine Zerlegung bei ψ = nan abbrach -- an der kippenden
Nulllinie eines L, wo zwischen zwei Neigungen mit Gleichgewicht eine ohne
liegen kann.

### _sekante

```python
def _sekante(a: float, fa: float, b: float, fb: float) -> float
```

Wo die Gerade durch `(a, fa)` und `(b, fb)` null wird.

### _weiter

```python
def _weiter(a: float, fa: float, b: float, fb: float, c: float, fc: float) -> Tuple[float, float, float, float]
```

Das Fenster nach dem Schritt nach `c`: `c` wird das neue Ende `b`.
Wechselt der Wert dort das Vorzeichen gegen `b`, wird `b` das andere
Ende; sonst bleibt `a` stehen, und sein Wert wird halbiert.

### eingrenzen

```python
def eingrenzen(f: Callable[[float], Wert], a: float, fa: float, schritt: float, *, faktor: float, unten: float=-math.inf, oben: float=math.inf) -> Optional[Tuple[float, float, float, float]]
```

Von `a` aus ein Fenster, in dem `f` das Vorzeichen wechselt -- mit
wachsenden Schritten in die Richtung, in der `f` null wird (`f`
steigt): `schritt`, dann mal `faktor`. Zurueck kommt
`(unten, oben, f_unten, f_oben)`, unten der kleinere Wert, wie
[[opencivil.core.suche#Illinois.finde|Illinois.finde]] sie nimmt -- `None`, wo `f` unterwegs keinen
Wert hat oder das Fenster an `unten` bzw. `oben` stoesst, ohne dass das
Vorzeichen wechselt.

Fuer Suchen, die bei einer Stelle anfangen, die nahe liegt -- der zuletzt
gefundenen Ebene: dort ist das Fenster in wenigen Schritten eng.


## Konstanten

- `SCHRITTE = 80` – Hoechstzahl der Schritte einer Suche. Erreicht wird sie nicht: abgebrochen wird an der Schranke. Die Zahl steht nur da, damit keine Schleife ewig laeuft.
- `Wert = Optional[float]` – Was eine Funktion an einer Stelle hat -- `None`, wo sie keinen Wert hat.
- `B = TypeVar('B')` – Was [[opencivil.core.suche#illinois|illinois]] neben dem Wert mitgibt und an der besten Stelle zurueckgibt.
- `HALBIEREN = Halbieren()` – Die beiden Suchen, wie sie meist gebraucht werden. Ohne eigenen Zustand -- wo eine Suche bei der zuletzt gefundenen Stelle anfaengt, merkt sich die Stelle, wer sucht.
- `ILLINOIS = Illinois()`

## Gebraucht von

- [[opencivil.nachweis.gebrauchsebene]]
- [[opencivil.nachweis.knicken]]
- [[opencivil.nachweis.qa_gebrauch]]
- [[opencivil.nachweis.qa_knicken]]
- [[opencivil.nachweis.querschnittsloeser]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.nachweis.resistenzlinie]]
- [[opencivil.querschnitt.interaktion]]
- [[opencivil.spannungsanalyse.schnitt]]
