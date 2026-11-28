---
erzeugt: 050dd16b6fae
art: modul
tags: [modul]
---
> [!abstract] opencivil/fachwerkmodell/herleitung.py
> wie ein Fachwerkmodell seine Rechnung aufschreibt.
> Paket [[opencivil.fachwerkmodell]] · [Quelltext](../../opencivil/fachwerkmodell/herleitung.py)

## VERANTWORTUNG

Die Scheibe in Tabellen – Scheiben und Löcher mit ihrer Fläche, die Lager
mit dem, was sie halten, die Lasten mit ihrer Summe –, dann das gefundene
Fachwerk: wie es gesucht wurde, je nach Verfahren, seine Stäbe mit ihren
Kräften, das Ziel V der Optimierung und was die Lager aufnehmen. Zuletzt
die Meldungen: rot, was falsch ist, sonst als Hinweis.


## EINHEITEN

Orte in m, Flächen in m², Kräfte in kN: `F_h` nach rechts, `F_v` nach
unten positiv, wie in der Maske; eine Stabkraft `N` mit Zug positiv.

## Inhalt

### schreiben

```python
def schreiben(p: Protokoll, befund: 'Fachwerkbefund') -> None
```

Die ganze Herleitung – nichts davon geht in den Befund ein, also still gar keine.

### _gesucht

```python
def _gesucht(p: Protokoll, gefunden: Suchergebnis, einstellung: Einstellung) -> None
```

Wie die Ground Structure das Fachwerk suchte.

### _aus_der_form

```python
def _aus_der_form(p: Protokoll, gefunden: Suchergebnis, einstellung: Formeinstellung) -> None
```

Wie SIMP die Form fand und das Werkzeug aus ihr das Fachwerk las.

### _danach

```python
def _danach(einstellung: 'Verfahrenseinstellung') -> str
```

Was nach der Optimierung mit dem Fachwerk geschieht – in beiden Verfahren gleich.

### _ziel

```python
def _ziel(p: Protokoll) -> None
```

Was die Optimierung der Kräfte klein macht – in beiden Verfahren dasselbe.

### _fachwerk

```python
def _fachwerk(p: Protokoll, n: Nachrechnung) -> None
```

Die Stäbe des Fachwerks, sein V und die Kräfte der Lager.


## Konstanten

- `ANNAHME = 'Ein Fachwerkmodell der Scheibe: Druckstreben und Zugglieder tragen d…` – Was das Fachwerkmodell annimmt.

## Braucht

- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.decke.geometrie]]
- [[opencivil.decke.herleitung]]
- [[opencivil.fachwerkmodell.form]]
- [[opencivil.fachwerkmodell.modell]]
- [[opencivil.fachwerkmodell.nachrechnung]]
- [[opencivil.fachwerkmodell.simp]]
- [[opencivil.fachwerkmodell.skelett]]
- [[opencivil.fachwerkmodell.suche]]
- [[opencivil.fachwerkmodell.werk]]

## Gebraucht von

- [[opencivil.fachwerkmodell.werk]]

## Formeln aus diesem Modul

- [[Leichtestes Fachwerk]] · `_ziel`
- [[Steifste Form]] · `_aus_der_form`
