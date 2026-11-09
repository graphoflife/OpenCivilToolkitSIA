---
erzeugt: 670907ca580e
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
Stegen und dem Schnitt um ihn, je für sich. Dazu die Zahlen der Legende.
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

### _linien

```python
def _linien(schnitt: Nachweisschnitt) -> list
```

Die Stücke eines Schnitts fürs Bild, je mit der Angabe, ob es zählt.

### _leisten

```python
def _leisten(b: Optional[Leistenpruefung]) -> Optional[Dict[str, Any]]
```

Die Leisten mit ihren Ankern, der äussere Schnitt um sie und ihre Zahlen -- in mm, kN.

### _pilz

```python
def _pilz(b: Optional[Pilzbefund]) -> Optional[Dict[str, Any]]
```

Der Stahlpilz mit seinen Stegen, seiner Fläche und dem Schnitt um sie -- in mm, kN.


## Braucht

- [[opencivil.core.rechenwerk]]
- [[opencivil.durchstanzen.nachweis]]
- [[opencivil.durchstanzen.pruefung]]
- [[opencivil.durchstanzen.schnitt]]
- [[opencivil.projekt]]

## Gebraucht von

- [[opencivil.web.api]]
