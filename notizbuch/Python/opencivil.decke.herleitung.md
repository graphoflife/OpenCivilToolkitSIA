---
erzeugt: 966fa64602c7
art: modul
tags: [modul]
---
> [!abstract] opencivil/decke/herleitung.py
> wie eine Decke ihre Rechnung aufschreibt.
> Paket [[opencivil.decke]] · [Quelltext](../../opencivil/decke/herleitung.py)

## VERANTWORTUNG

Die Herleitung der Streifenmethode, so dass man sie von Hand nachvollziehen
kann: die Decke in Tabellen -- Platten, Linienlager, Stützen, Unterzüge --,
die Streifen je Richtung, in welcher Reihenfolge die Träger rechnen, wie die
Last auf die Richtungen geht, und die Meldungen.


## EINHEITEN

Längen in m, Dicken und Stützen in mm, Winkel in Grad gegen x, E in N/mm²,
Gewichte in kN/m².

## Inhalt

### schreiben

```python
def schreiben(p: Protokoll, system: 'Deckensystem', befund: 'Deckenbefund') -> None
```

Die ganze Herleitung einer Decke.


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
