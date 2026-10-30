---
erzeugt: 0524bfe9c6e5
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/durchstanzdaten.py
> was die Oberflaeche von einer Durchstanzstelle zeichnet.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/durchstanzdaten.py)

## VERANTWORTUNG

Je Durchstanzstelle der Grundriss, wie der Kern ihn gerechnet hat, in mm:
der Umriss der gestützten Fläche, die Plattenränder, die Aussparungen und
der Nachweisschnitt -- je Stück, ob es zählt --, und wo es eine braucht, die
Durchstanzbewehrung: die Leisten mit ihren Ankern und der äussere Schnitt.
Dazu die Zahlen der Legende.
Gezeichnet wird in der Oberflaeche, gerechnet nichts: die Linien kommen aus
dem Befund des Nachweises ([[opencivil.durchstanzen.nachweis]]).

## Inhalt

### situationen

```python
def situationen(aufbau: Aufbau, loesung: Loesung) -> Dict[str, Any]
```

Je Durchstanzstelle, nach Kennung, was die Zeichnung vom Kern braucht.

### situation

```python
def situation(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Optional[Dict[str, Any]]
```

Was der Grundriss einer Stelle braucht -- `None`, wenn ihr Nachweis nicht gelaufen ist.

### _bewehrung

```python
def _bewehrung(b: Optional[Bewehrungsbefund]) -> Optional[Dict[str, Any]]
```

Was die Bemessung vorschlägt, in mm und kN: die Leisten mit ihren Ankern
und der äussere Schnitt um sie, der Stahlpilz mit seinen Stegen und dem
Schnitt um ihn -- was es davon gibt --, und die Zahlen der Legende.


## Braucht

- [[opencivil.core.rechenwerk]]
- [[opencivil.durchstanzen.mit_bewehrung]]
- [[opencivil.durchstanzen.nachweis]]
- [[opencivil.projekt]]

## Gebraucht von

- [[opencivil.web.api]]
