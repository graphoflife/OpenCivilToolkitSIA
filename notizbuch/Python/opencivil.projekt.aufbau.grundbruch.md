---
erzeugt: 050de19da28c
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/aufbau/grundbruch.py
> ein Fundament wird Rechnung.
> Paket [[opencivil.projekt.aufbau]] · [Quelltext](../../opencivil/projekt/aufbau/grundbruch.py)

## VERANTWORTUNG

Aus einem [[opencivil.projekt.grundbruch#GrundbruchEintrag|GrundbruchEintrag]] das
Fundament und seine beiden Nachweise, Grundbruch und Gleiten ([[opencivil.projekt.aufbau.grundbruch#bauen|bauen]]).

## Inhalt

### bauen

```python
def bauen(art: 'Bauteilart', eintrag: GrundbruchEintrag, aufbau: Aufbau) -> Bauteil
```

Ein Fundament und seine beiden Nachweise -- Grundbruch und Gleiten --,
sobald eine Kombination eingeschaltet ist. Ohne sie steht das Fundament
allein da, wie eine Platte ohne Einwirkung.

Jede Zahl in der Einheit ihres Feldes ([[opencivil.projekt.lesen#als_groesse|als_groesse]])
-- bis 2026-10-18 stand sie hier ein zweites Mal.


## Braucht

- [[opencivil.geotechnik.grundbruch]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.grundbruch]]
- [[opencivil.projekt.lesen]]

## Gebraucht von

- [[opencivil.projekt.aufbau]]
