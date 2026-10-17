---
erzeugt: 46d950662477
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


## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.geotechnik.grundbruch]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.grundbruch]]

## Gebraucht von

- [[opencivil.projekt.aufbau]]
