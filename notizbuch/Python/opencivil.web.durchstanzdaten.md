---
erzeugt: 98956a73e40b
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/durchstanzdaten.py
> was die Oberflaeche von einer Durchstanzstelle zeichnet.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/durchstanzdaten.py)

## VERANTWORTUNG

Je Durchstanzstelle der Grundriss, wie der Kern ihn gerechnet hat, in mm:
der Umriss der gestützten Fläche, die Plattenränder, die Aussparungen und
der Nachweisschnitt -- je Stück, ob es zählt. Dazu die Zahlen der Legende.
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


## Braucht

- [[opencivil.core.rechenwerk]]
- [[opencivil.durchstanzen.nachweis]]
- [[opencivil.projekt]]

## Gebraucht von

- [[opencivil.web.api]]
