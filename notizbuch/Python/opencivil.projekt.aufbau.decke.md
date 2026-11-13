---
erzeugt: e72f2fa8f745
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/aufbau/decke.py
> eine Decke wird Rechnung.
> Paket [[opencivil.projekt.aufbau]] · [Quelltext](../../opencivil/projekt/aufbau/decke.py)

## VERANTWORTUNG

Aus einem [[opencivil.projekt.decke#DeckeEintrag|DeckeEintrag]] das Modell der
Streifenmethode in SI ([[opencivil.projekt.aufbau.decke#modell_von|modell_von]]) und das Bauteil im Rechenwerk
([[opencivil.projekt.aufbau.decke#bauen|bauen]]). Hart scheitert nur ein Verweis auf einen Beton, den es im
Projekt nicht gibt -- wie im Balkensystem. Was der Decke selbst fehlt --
ein Knoten, eine Platte ohne Beton --, steht in ihren Meldungen, und der
Rest des Projekts rechnet.

## Inhalt

### modell_von

```python
def modell_von(eintrag: DeckeEintrag) -> Tuple[Decke, List[Meldung]]
```

Die Decke der Beschreibung in SI -- E und Gewicht der Platten null, die
kommen beim Rechnen von ihrem Beton. Ein Teil, das auf einen Knoten
zeigt, den es nicht gibt, fehlt im Modell; die Meldung sagt es.

### _betone

```python
def _betone(eintrag: DeckeEintrag, aufbau: Aufbau) -> Tuple[Dict[str, Baustoff], List[Meldung]]
```

Je Platte ihr Beton -- und eine Meldung je Platte, die keinen hat.

### bauen

```python
def bauen(art: 'Bauteilart', eintrag: DeckeEintrag, aufbau: Aufbau) -> Bauteil
```

Eine Decke: ihr Modell, ihre Betone, angemeldet im Rechenwerk.


## Braucht

- [[opencivil.decke.geometrie]]
- [[opencivil.decke.modell]]
- [[opencivil.decke.werk]]
- [[opencivil.material.basis]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.decke]]
- [[opencivil.projekt.lesen]]
- [[opencivil.stabwerk.system]]

## Gebraucht von

- [[opencivil.projekt.aufbau]]
