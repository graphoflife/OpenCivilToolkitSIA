---
erzeugt: 7ad335fdd1b0
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/aufbau/balkensystem.py
> ein Balkensystem wird Rechnung.
> Paket [[opencivil.projekt.aufbau]] · [Quelltext](../../opencivil/projekt/aufbau/balkensystem.py)

## VERANTWORTUNG

Aus einem [[opencivil.projekt.balkensystem#BalkensystemEintrag|BalkensystemEintrag]] das
Stabwerk mit aufgeloesten Querschnitten ([[opencivil.projekt.aufbau.balkensystem#bauen|bauen]]). Ein Querschnitt kann
eine Platte oder eine Querschnittsanalyse des Projekts nehmen; die muessen
dann schon gebaut sein -- darum kommt das Balkensystem in
[[opencivil.projekt.aufbau#Konstanten|BAUTEILE]] nach ihnen.

## Inhalt

### bauen

```python
def bauen(art: 'Bauteilart', eintrag: BalkensystemEintrag, aufbau: Aufbau) -> Bauteil
```

Ein Balkensystem: das Stabwerk der Beschreibung, seine Querschnitte
aufgeloest. Hart scheitert nur ein Verweis, den es nicht gibt -- ein
Material, eine Platte, eine Querschnittsanalyse --; was dem System selbst
fehlt, steht in seinen Meldungen, und der Rest des Projekts rechnet.

### _stabquerschnitt

```python
def _stabquerschnitt(q: StabquerschnittEintrag, aufbau: Aufbau, wo: str) -> Stabquerschnitt
```

Woher A und I eines Querschnitts kommen -- die Platte oder Analyse dazu muss es geben.


## Braucht

- [[opencivil.material.basis]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.balkensystem]]
- [[opencivil.projekt.lesen]]
- [[opencivil.stabwerk.rechnung]]

## Gebraucht von

- [[opencivil.projekt.aufbau]]
