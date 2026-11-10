---
erzeugt: 5ae82ed713d4
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/durchstanzdaten.py
> was die Oberflaeche von einer Durchstanzstelle zeichnet.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/durchstanzdaten.py)

## VERANTWORTUNG

Je Durchstanzstelle der Grundriss, wie der Kern ihn gerechnet hat, in mm:
der Umriss der gestützten Fläche, die Plattenränder, die Aussparungen und
der Nachweisschnitt -- je Stück, ob es zählt --, und wo es sie braucht, die
Leisten mit ihren Ankern und dem äusseren Schnitt und der Stahlpilz mit seinen
Stegen und dem Schnitt um ihn, je für sich. Dazu die Legende unter dem Bild
([[opencivil.web.anzeige]]): die Schnitte mit ihren Zahlen und das Urteil.
Gezeichnet wird in der Oberflaeche, gerechnet nichts: die Linien kommen aus
dem Befund des Nachweises ([[opencivil.durchstanzen.nachweis]]).

Für den Katalog die Wahlen der Maske ([[opencivil.web.durchstanzdaten#wahlen|wahlen]]): je Stellung ihre
Beschriftung, und welche Felder der Nachweis mit ihr liest -- die Masse je
Lage und Form, die Felder je Näherungsstufe und Lage, die von k_e. Die Maske
zeigt die Vereinigung, so baut sie die Regel nicht nach
([[opencivil.durchstanzen.stelle#eingaben_fuer|opencivil.durchstanzen.stelle.eingaben_fuer]]).

## Inhalt

### wahlen

```python
def wahlen() -> Dict[str, Any]
```

Die Schalter einer Durchstanzstelle mit ihren Stellungen -- und je Lage
ihre Art: wie die Maske ihre Masse überschreibt, ob sie eine Form hat,
welche Masse sie je Form liest, was die Liste von ihr zeigt und welche
Felder jede Näherungsstufe an ihr liest.

### situation

```python
def situation(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Optional[Dict[str, Any]]
```

Was der Grundriss einer Stelle braucht -- `None`, wenn ihr Nachweis nicht gelaufen ist.

### _linien

```python
def _linien(schnitt: Nachweisschnitt) -> list
```

Die Stücke eines Schnitts fürs Bild, je mit der Angabe, ob es zählt.

### _legende

```python
def _legende(befund: Durchstanzbefund, urteile) -> List[list]
```

Die Zeilen unter dem Bild: der Schnitt und was von ihm nicht zählt; ohne
Bewehrung der Vergleich mit seinem Urteil, sonst was ohne sie fehlt, der
Pilz und die Leisten mit ihren Schnitten -- und das Urteil über alle.

### _kraft

```python
def _kraft(si_wert: float) -> str
```

Eine Kraft der Legende: kN mit einer Stelle.


## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.durchstanzen.flaeche]]
- [[opencivil.durchstanzen.nachweis]]
- [[opencivil.durchstanzen.schnitt]]
- [[opencivil.durchstanzen.stelle]]
- [[opencivil.projekt]]
- [[opencivil.web.anzeige]]

## Gebraucht von

- [[opencivil.web.api]]
- [[opencivil.web.zeichendaten]]
