---
erzeugt: ddbe7414403b
art: modul
tags: [modul]
---
> [!abstract] opencivil/fachwerkmodell/verfahren.py
> wie ein Fachwerk gesucht wird.
> Paket [[opencivil.fachwerkmodell]] · [Quelltext](../../opencivil/fachwerkmodell/verfahren.py)

## VERANTWORTUNG

Die zwei Verfahren eines Fachwerkmodells ([[opencivil.fachwerkmodell.verfahren#Verfahren|Verfahren]]) und ihre
Zahlen ([[opencivil.fachwerkmodell.verfahren#Konstanten|VORGABEN]]) – in der Maske die Kachel «Verfahren», in der
Herleitung ein Kasten:

- Ground Structure ([[opencivil.fachwerkmodell.suche|suche]]): Knoten in
  einem Raster, je zwei ein möglicher Stab; eine lineare Optimierung wählt
  das leichteste Fachwerk im Gleichgewicht, Runde um Runde mit mehr Stäben.
- SIMP ([[opencivil.fachwerkmodell.form|form]]): das Material verteilt sich
  Schritt um Schritt zur steifsten Form; aus ihr liest das Werkzeug ein
  Fachwerk, dessen Kräfte dieselbe Optimierung bestimmt.

Beide teilen das Gewicht des Zugs gegenüber dem Druck und die kleinste
Stabkraft, die stehen bleibt.

## Inhalt

### Verfahren

```python
class Verfahren(Wahl)
```

Wie ein Fachwerk gesucht wird – siehe Dateikopf.

- `GROUND_STRUCTURE = 'ground_structure'`
- `SIMP = 'simp'`

#### Verfahren.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Verfahren.erklaerung

```python
@property
def erklaerung(self) -> str
```

### _felder

```python
def _felder(verfahren: Verfahren) -> Tuple[Feld, ...]
```

Die Zahlen des Verfahrens: zuerst, was nur es hat, dann, was beide teilen.


## Konstanten

- `VORGABEN = (Gruppe('Verfahren', _felder, nach=('verfahren',)),)` – Die Zahlen der Verfahren, in der Maske eine Kachel, in der Herleitung ein Kasten.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.vorgaben]]
- [[opencivil.core.wahl]]
- [[opencivil.fachwerkmodell.grundstruktur]]
- [[opencivil.fachwerkmodell.simp]]

## Gebraucht von

- [[opencivil.fachwerkmodell.form]]
- [[opencivil.fachwerkmodell.suche]]
- [[opencivil.fachwerkmodell.werk]]
- [[opencivil.projekt.aufbau.fachwerkmodell]]
- [[opencivil.projekt.beispiele]]
- [[opencivil.projekt.fachwerkmodell]]
- [[opencivil.web.api]]
- [[opencivil.web.fachwerkdaten]]
