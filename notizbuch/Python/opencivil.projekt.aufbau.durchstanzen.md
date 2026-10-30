---
erzeugt: beb4b4de6584
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/aufbau/durchstanzen.py
> eine Durchstanzstelle wird Rechnung.
> Paket [[opencivil.projekt.aufbau]] · [Quelltext](../../opencivil/projekt/aufbau/durchstanzen.py)

## VERANTWORTUNG

Aus einem [[opencivil.projekt.durchstanzen#DurchstanzEintrag|DurchstanzEintrag]] die
Durchstanzstelle mit ihren Vorgaben und ihr Nachweis ([[opencivil.projekt.aufbau.durchstanzen#bauen|bauen]]). Hier
werden die Aussparungen aus ihren Knoten gelesen und geprüft: eine
Aussparung braucht drei Ecken, darf sich nicht selbst schneiden und nicht
über die gestützte Fläche reichen.

## Inhalt

### aussparungen

```python
def aussparungen(eintrag: DurchstanzEintrag) -> List[List[Tuple[float, float]]]
```

Die Aussparungen als Ecken in m -- geprüft, sonst ein Satz, was nicht stimmt.

### bauen

```python
def bauen(art: 'Bauteilart', eintrag: DurchstanzEintrag, aufbau: Aufbau) -> Bauteil
```

Eine Durchstanzstelle und ihr Nachweis. Jede Zahl in der Einheit ihres
Feldes ([[opencivil.projekt.lesen#als_groesse|als_groesse]]).


## Konstanten

- `MM = 0.001` – mm in m.

## Braucht

- [[opencivil.durchstanzen.nachweis]]
- [[opencivil.durchstanzen.stelle]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.durchstanzen]]
- [[opencivil.projekt.lesen]]
- [[opencivil.querschnitt.geometrie]]

## Gebraucht von

- [[opencivil.projekt.aufbau]]
