---
erzeugt: f4a5ae65904b
art: modul
tags: [modul]
---
> [!abstract] opencivil/fachwerkmodell/herleitung.py
> wie ein Fachwerkmodell seine Rechnung aufschreibt.
> Paket [[opencivil.fachwerkmodell]] · [Quelltext](../../opencivil/fachwerkmodell/herleitung.py)

## VERANTWORTUNG

Die Scheibe in Tabellen – Scheiben und Löcher mit ihrer Fläche, die Lager
mit dem, was sie halten, die Lasten mit ihrer Summe –, dann das gefundene
Fachwerk: wie es gesucht wurde, seine Stäbe mit ihren Kräften, das Ziel V
der Optimierung und was die Lager aufnehmen. Zuletzt die Meldungen: rot,
was falsch ist, sonst als Hinweis.


## EINHEITEN

Orte in m, Flächen in m², Kräfte in kN: `F_h` nach rechts, `F_v` nach
unten positiv, wie in der Maske; eine Stabkraft `N` mit Zug positiv.

## Inhalt

### schreiben

```python
def schreiben(p: Protokoll, befund: 'Fachwerkbefund', einstellung: Einstellung) -> None
```

Die ganze Herleitung – nichts davon geht in den Befund ein, also still gar keine.

### _fachwerk

```python
def _fachwerk(p: Protokoll, gefunden: Suchergebnis, n: Nachrechnung, einstellung: Einstellung) -> None
```

Wie das Fachwerk gesucht wurde, seine Stäbe, sein V und die Kräfte der Lager.


## Konstanten

- `ANNAHME = 'Ein Fachwerkmodell der Scheibe: Druckstreben und Zugglieder tragen d…` – Was das Fachwerkmodell annimmt.

## Braucht

- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.decke.geometrie]]
- [[opencivil.decke.herleitung]]
- [[opencivil.fachwerkmodell.modell]]
- [[opencivil.fachwerkmodell.nachrechnung]]
- [[opencivil.fachwerkmodell.suche]]
- [[opencivil.fachwerkmodell.werk]]

## Gebraucht von

- [[opencivil.fachwerkmodell.werk]]

## Formeln aus diesem Modul

- [[Leichtestes Fachwerk]] · `_fachwerk`
