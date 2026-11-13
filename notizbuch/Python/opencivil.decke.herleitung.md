---
erzeugt: ff71f8ae157f
art: modul
tags: [modul]
---
> [!abstract] opencivil/decke/herleitung.py
> wie eine Decke ihre Rechnung aufschreibt.
> Paket [[opencivil.decke]] · [Quelltext](../../opencivil/decke/herleitung.py)

## VERANTWORTUNG

Die Herleitung der Streifenmethode, so dass man sie von Hand nachvollziehen
kann: die Decke in Tabellen -- Platten, Linienlager, Stützen, Unterzüge,
Lasten je Lastfall und die Kombinationen --, die Streifen je Richtung, in
welcher Reihenfolge die Träger rechnen, wie die Last auf die Richtungen
geht, je Fall die Last und was die Lager davon tragen, und die Meldungen.


## EINHEITEN

Längen in m, Dicken und Stützen in mm, Winkel in Grad gegen x, E in N/mm²,
Gewichte und Flächenlasten in kN/m², Linienlasten in kN/m, Kräfte in kN.

## Inhalt

### schreiben

```python
def schreiben(p: Protokoll, system: 'Deckensystem', befund: 'Deckenbefund') -> None
```

Die ganze Herleitung einer Decke.

### _lasten

```python
def _lasten(p: Protokoll, decke: Decke) -> None
```

Die Lasten je Lastfall, wie sie beschrieben sind, und die Beiwerte der Kombinationen.

### _last

```python
def _last(last: Last) -> list
```

Name, Ort und Wert einer Last für die Tabelle.

### _faelle

```python
def _faelle(p: Protokoll, e: Ergebnis) -> None
```

Je Lastfall und Kombination die Last und was die Lager tragen -- die Probe --, und die Meldungen des Falls.


## Konstanten

- `ANNAHME = 'Streifenmethode (Stahlbeton II, 7.2 Platten, Folien 27 bis 39): jede…` – Was die Streifenmethode annimmt -- die Steifigkeit nach Vorgabe, nicht nachgeschlagen.
- `AUTOMATISCH = 'Automatisch, nach Folie 31 verallgemeinert: je Zelle zweier Feldstre…` – Die automatische Aufteilung in Worten -- die Regel steht in [[opencivil.decke.aufteilung|aufteilung]].

## Braucht

- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.decke.geometrie]]
- [[opencivil.decke.modell]]
- [[opencivil.decke.rechnung]]
- [[opencivil.decke.streifen]]
- [[opencivil.decke.werk]]

## Gebraucht von

- [[opencivil.decke.werk]]
