---
erzeugt: 7be9fc68e2ef
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
Stegen und dem Schnitt um ihn, je für sich. Dazu die Legende unter dem Bild
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
([[opencivil.durchstanzen.stelle#eingaben_fuer|opencivil.durchstanzen.stelle.eingaben_fuer]]).

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

### _ansicht

```python
def _ansicht(befund: Durchstanzbefund, stelle: Durchstanzstelle, werte: Dict[str, Wert]) -> Dict[str, Any]
```

Eine Leiste in der Ansicht, längs geschnitten: die mit den meisten
Elementen, unter ihnen die, die am ehesten nach rechts läuft. Die Stütze
steht, wo die Linie der Leiste ihren Rand trifft – mit einem Stahlpilz
vor dem Rand der gestützten Fläche –, ihre Achse, wo die Linie ihr am
nächsten kommt. Eine Lage der Zugbewehrung läuft «längs», wenn sie eher
in Richtung der Leiste liegt; die andere steht im Bild als Punkte.

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
def _legende(befund: Durchstanzbefund, urteile: Sequence[NachweisUrteil]) -> List[list]
```

Die Zeilen unter dem Bild: der Schnitt und was von ihm nicht zählt; ohne
Bewehrung der Vergleich mit seinem Urteil, sonst was ohne sie fehlt, der
Pilz und die Leisten mit ihren Schnitten – und das Urteil über alle. Passt
kein Produkt, sagt die letzte Zeile das statt eines Grads: die Nachweise
mit Bewehrung sind dann nicht geführt ([[opencivil.core.nachweis#NachweisUrteil|NachweisUrteil.offen]]).
Ohne Stützenkraft steht statt des Vergleichs der Satz aller Nachweise ohne
Einwirkung.

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


## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.nachweis]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.core.wert]]
- [[opencivil.durchstanzen.bewehrung]]
- [[opencivil.durchstanzen.flaeche]]
- [[opencivil.durchstanzen.nachweis]]
- [[opencivil.durchstanzen.schnitt]]
- [[opencivil.durchstanzen.stelle]]
- [[opencivil.durchstanzen.systeme]]
- [[opencivil.projekt]]
- [[opencivil.querschnitt.platte]]
- [[opencivil.web.anzeige]]

## Gebraucht von

- [[opencivil.web.api]]
- [[opencivil.web.zeichendaten]]
