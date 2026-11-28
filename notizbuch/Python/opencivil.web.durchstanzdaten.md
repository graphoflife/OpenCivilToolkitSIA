---
erzeugt: ce86ebaa3d5a
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/durchstanzdaten.py
> was die Oberflaeche von einer Durchstanzstelle zeichnet.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/durchstanzdaten.py)

## VERANTWORTUNG

Je Durchstanzstelle der Grundriss, wie der Kern ihn gerechnet hat, in mm:
der Umriss der gestützten Fläche, die Plattenränder, die Aussparungen und
der Nachweisschnitt – je Stück, ob es zählt –, und wo es sie braucht, die
Leisten mit ihren Ankern und dem äusseren Schnitt und der Stahlpilz mit seinen
Stegen und dem Schnitt um ihn, je für sich. Die Plattenbereiche mit ihrer
Dicke, an jeder Stufe ihr Schnitt, je in seiner Farbe ([[opencivil.web.durchstanzdaten#Konstanten|STUFENFARBEN]]),
und der Schnitt durch verschiedene Dicken. Dazu die Legende unter dem Bild
([[opencivil.web.anzeige]]): die Schnitte mit ihren Zahlen und das Urteil.
Gezeichnet wird in der Oberflaeche, gerechnet nichts: die Linien kommen aus
dem Befund des Nachweises ([[opencivil.durchstanzen.nachweis]]).

Wo es Durchstanzbewehrung braucht, auch eine Leiste in der Ansicht
([[opencivil.web.durchstanzdaten#_ansicht|_ansicht]]): längs geschnitten, mit Platte, Zugbewehrung, Stütze und
Pilz, den Elementen und dem Bereich, in dem sie zählen – in mm, x ab dem
Rand der gestützten Fläche, z ab der Druckseite.

Für den Katalog die Wahlen der Maske ([[opencivil.web.durchstanzdaten#wahlen|wahlen]]): je Stellung ihre
Beschriftung, und welche Felder der Nachweis mit ihr liest – die festen, die
Masse je Lage und Form, die Felder je Näherungsstufe und Lage, die von k_e.
Die Maske zeigt die Vereinigung, so baut sie die Regel nicht nach
([[opencivil.durchstanzen.stelle#eingaben_fuer|opencivil.durchstanzen.stelle.eingaben_fuer]]). Dazu die beiden
Seiten, auf denen die Stufe eines Plattenbereichs liegen kann, und wie die
Kennungen der Polygone im Grundriss beginnen.

## Inhalt

### wahlen

```python
def wahlen() -> Dict[str, Any]
```

Die Schalter einer Durchstanzstelle mit ihren Stellungen – und je Lage
ihre Art: wie die Maske ihre Masse überschreibt, ob sie eine Form hat,
welche Masse sie je Form liest, was die Liste von ihr zeigt und welche
Felder jede Näherungsstufe an ihr liest. Dazu, was der Nachweis an jeder
Stelle liest (`fest`).

### situation

```python
def situation(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Optional[Dict[str, Any]]
```

Was der Grundriss einer Stelle braucht – `None`, wenn ihr Nachweis nicht gelaufen ist.

### _mit_schnitt

```python
def _mit_schnitt(befund: Durchstanzbefund) -> List[Stufenbefund]
```

Die Stufen, die einen eigenen Schnitt haben – in der Reihe ihrer Farben.

### _ansicht

```python
def _ansicht(befund: Durchstanzbefund, stelle: Durchstanzstelle, werte: Dict[str, Wert]) -> Dict[str, Any]
```

Eine Leiste in der Ansicht, längs geschnitten: die mit den meisten
Elementen, unter ihnen die, die am ehesten nach rechts läuft. Die Stütze
steht, wo die Linie der Leiste ihren Rand trifft – mit einem Stahlpilz
vor dem Rand der gestützten Fläche –, ihre Achse, wo die Linie ihr am
nächsten kommt. Eine Lage der Zugbewehrung läuft «längs», wenn sie eher
in Richtung der Leiste liegt; die andere steht im Bild als Punkte. Steht
die Leiste in einem Plattenbereich, ist `h` seine Dicke, und rechts
kommt seine Stufe ins Bild, wo sie nahe genug liegt ([[opencivil.web.durchstanzdaten#_stufe|_stufe]]).

### _stufe

```python
def _stufe(platz: Platz, leiste: Leiste, h_platte: float, sichtbar: float) -> Optional[Dict[str, Any]]
```

Die Stufe des Bereichs, in dem die Leiste steht, in mm: wie weit sie
längs der Leiste vom Rand der gestützten Fläche liegt, wie dick die
Platte dahinter ist und um wie viel Druck- und Zugseite dort
zurückspringen – die Seite des Bereichs (Figur 24a, 24c). `None`, wo
die Leiste in keinem Bereich steht oder die Stufe weiter als
`sichtbar` (m) liegt. Nur fürs Bild.

### _mm

```python
def _mm(laenge: float) -> str
```

Eine Länge in ganzen mm, für Sätze der Legende.

### _bis_zum_umriss

```python
def _bis_zum_umriss(p: Punkt, r: Punkt, umriss: Sequence[Punkt]) -> float
```

Wie weit der Strahl von `p` in Richtung `r` läuft, bis er den Umriss
trifft – null, wenn `p` auf ihm liegt oder der Strahl ihn verfehlt. Nur
fürs Bild.

### _linien

```python
def _linien(schnitt: Nachweisschnitt) -> list
```

Die Stücke eines Schnitts fürs Bild, je mit der Angabe, ob es zählt.

### _legende

```python
def _legende(befund: Durchstanzbefund, urteile: Sequence[NachweisUrteil], bereiche: Sequence[Plattenbereich]=()) -> List[list]
```

Die Zeilen unter dem Bild: der Schnitt und was von ihm nicht zählt; ohne
Bewehrung der Vergleich mit seinem Urteil, sonst was ohne sie fehlt, der
Pilz und die Leisten mit ihren Schnitten – und das Urteil über alle. Passt
kein Produkt, sagt die letzte Zeile das statt eines Grads: die Nachweise
mit Bewehrung sind dann nicht geführt ([[opencivil.core.nachweis#NachweisUrteil|NachweisUrteil.offen]]).
Ohne Stützenkraft steht statt des Vergleichs der Satz aller Nachweise ohne
Einwirkung. Mit Plattenbereichen je Stufe ihr Schnitt, und die Zahlen
stehen je Schnitt.

### _schnittzeilen

```python
def _schnittzeilen(befund: Durchstanzbefund) -> List[list]
```

Die Zahlen an den Stufen und am Schnitt durch verschiedene Dicken.

### _gesamtzeile

```python
def _gesamtzeile(urteile: Sequence[NachweisUrteil]) -> list
```

Das Urteil über alle geführten Nachweise, mit dem kleinsten Grad.

### _stufenzeilen

```python
def _stufenzeilen(befund: Durchstanzbefund) -> List[list]
```

Was die Plattenbereiche im Bild sind: getönt mit ihrer Dicke, an jeder
Stufe ihr Schnitt in seiner Farbe – oder warum sie keinen hat – und der
Schnitt durch verschiedene Dicken.

### _gesamt

```python
def _gesamt(urteile: Sequence[NachweisUrteil]) -> Tuple[bool, str]
```

Ob alle geführten Urteile aufgehen, und ihr kleinster Grad in LaTeX.

### _kraft

```python
def _kraft(si_wert: float) -> str
```

Eine Kraft der Legende: kN mit einer Stelle.


## Konstanten

- `STUFENFARBEN = ('grün', 'türkis', 'braun')` – Die Farben der Schnitte an den Stufen, der Reihe nach – im Bild die Klassen «ds-stufe-0» bis «ds-stufe-2» (web/css/80-skizzen.css).
- `WEGFARBE = 'blau'` – Die Farbe des Schnitts durch verschiedene Dicken – im Bild «ds-weg».

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.nachweis]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.core.wert]]
- [[opencivil.durchstanzen.bereiche]]
- [[opencivil.durchstanzen.bewehrung]]
- [[opencivil.durchstanzen.flaeche]]
- [[opencivil.durchstanzen.mit_bewehrung]]
- [[opencivil.durchstanzen.nachweis]]
- [[opencivil.durchstanzen.schnitt]]
- [[opencivil.durchstanzen.stelle]]
- [[opencivil.durchstanzen.systeme]]
- [[opencivil.durchstanzen.weg]]
- [[opencivil.projekt]]
- [[opencivil.projekt.durchstanzen]]
- [[opencivil.querschnitt.platte]]
- [[opencivil.web.anzeige]]

## Gebraucht von

- [[opencivil.web.api]]
- [[opencivil.web.zeichendaten]]
