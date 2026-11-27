---
erzeugt: 7e5ef7d66391
art: modul
tags: [modul]
---
> [!abstract] opencivil/fachwerkmodell/herleitung.py
> wie ein Fachwerkmodell seine Rechnung aufschreibt.
> Paket [[opencivil.fachwerkmodell]] · [Quelltext](../../opencivil/fachwerkmodell/herleitung.py)

## VERANTWORTUNG

Die Scheibe in Tabellen – Scheiben und Löcher mit ihrer Fläche, die Lager
mit dem, was sie halten, die Lasten mit ihrer Summe –, dann die
Meldungen: rot, was falsch ist, sonst als Hinweis.


## EINHEITEN

Orte in m, Flächen in m², Kräfte in kN: `F_h` nach rechts, `F_v` nach
unten positiv, wie in der Maske.

## Inhalt

### schreiben

```python
def schreiben(p: Protokoll, befund: 'Fachwerkbefund') -> None
```

Die ganze Herleitung – nichts davon geht in den Befund ein, also still gar keine.


## Konstanten

- `ANNAHME = 'Ein Fachwerkmodell der Scheibe: Druckstreben und Zugglieder tragen d…` – Was das Fachwerkmodell annimmt.
- `KN = 0.001` – kN je N.

## Braucht

- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.decke.geometrie]]
- [[opencivil.decke.herleitung]]
- [[opencivil.fachwerkmodell.modell]]
- [[opencivil.fachwerkmodell.werk]]

## Gebraucht von

- [[opencivil.fachwerkmodell.werk]]
