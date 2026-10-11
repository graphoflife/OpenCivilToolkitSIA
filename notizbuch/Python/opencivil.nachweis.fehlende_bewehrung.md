---
erzeugt: 1064f57a9003
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/fehlende_bewehrung.py
> Nachweise, die mangels Bewehrung entfallen.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/fehlende_bewehrung.py)

## VERANTWORTUNG

Sagt, dass in dieser Tragrichtung nichts zu rechnen ist -- und sagt es
sichtbar. Gerechnet wird hier nichts.


## WARUM ES DEN BAUSTEIN GIBT

Liegt in einer Richtung keine Bewehrung, laesst sich weder die Resistenzlinie
der Handrechnung aufstellen noch eine statische Hoehe bestimmen. Frueher entfiel
der Nachweis darum stillschweigend: wer eine Einwirkung in y-Richtung angegeben
hatte, fand sie in der Zusammenfassung nirgends wieder. Ein leerer Platz liest
sich aber wie *geprueft und in Ordnung*.

Ohne Stahl ist der Momentenwiderstand der Handrechnung **null** -- nicht etwa
das, was der Beton allein noch aufnaehme. Der Erfuellungsgrad ist damit
ebenfalls null und der Nachweis nicht erfuellt. Genau das steht jetzt da.


## NICHT ZU VERWECHSELN MIT

Der Fall, dass nur *eine Seite* unbewehrt ist -- untere Lage vorhanden, obere
nicht --, wird von den Nachweisen selbst behandelt. Hier geht es um eine
Richtung, in der ueberhaupt kein Posten liegt.

## Inhalt

### Ausgefallen

```python
@dataclass(frozen=True)
class Ausgefallen
```

Ein einzelner Nachweis, der nicht gefuehrt werden kann.

- `art: str` – Kurzzeichen der Nachweisart -- `M-N` oder `V`.
- `langname: str` – Die Nachweisart ausgeschrieben, mit Richtung.
- `fall: str` – Name der Einwirkungskombination.
- `symbol: str` – Symbol des Widerstands, z.B. `M_{Rd,y}`.
- `einwirkung_symbol: str`
- `einwirkung: Groesse`
- `einheit: Einheit`

#### Ausgefallen.kennung

```python
@property
def kennung(self) -> str
```

### FehlendeBewehrung

```python
class FehlendeBewehrung(Nachweis)
```

Die Nachweise einer unbewehrten Tragrichtung -- alle nicht erfuellt.

Ein Baustein je Platte und Richtung, ein Urteil je ausgefallenem Nachweis.
Er hat keine Eingaenge: es gibt nichts zu beschaffen, wenn nichts da ist.

#### FehlendeBewehrung.grund

```python
@property
def grund(self) -> str
```

#### FehlendeBewehrung.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll)
```


## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.querschnitt.platte]]

## Gebraucht von

- [[opencivil.projekt.aufbau]]
