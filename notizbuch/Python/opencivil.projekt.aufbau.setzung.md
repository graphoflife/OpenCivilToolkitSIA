---
erzeugt: 71a34e763afc
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/aufbau/setzung.py
> eine Setzungsberechnung wird Rechnung.
> Paket [[opencivil.projekt.aufbau]] · [Quelltext](../../opencivil/projekt/aufbau/setzung.py)

## VERANTWORTUNG

Aus einem [[opencivil.projekt.setzung#SetzungEintrag|SetzungEintrag]] das Fundament
und sein Nachweis, die Setzung ([[opencivil.projekt.aufbau.setzung#bauen|bauen]]).

## Inhalt

### bauen

```python
def bauen(art: 'Bauteilart', eintrag: SetzungEintrag, aufbau: Aufbau) -> Bauteil
```

Ein Fundament und seine Setzung, sobald es eine Schicht gibt. Ohne sie
steht das Fundament allein da, wie ein Grundbruch ohne Kombination.
Jede Zahl in der Einheit ihres Feldes
([[opencivil.projekt.lesen#als_groesse|als_groesse]]).


## Braucht

- [[opencivil.geotechnik.setzung]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.setzung]]

## Gebraucht von

- [[opencivil.projekt.aufbau]]
