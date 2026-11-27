---
erzeugt: 4024f3568ac5
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/aufbau/fachwerkmodell.py
> ein Fachwerkmodell wird Rechnung.
> Paket [[opencivil.projekt.aufbau]] · [Quelltext](../../opencivil/projekt/aufbau/fachwerkmodell.py)

## VERANTWORTUNG

Aus einem [[opencivil.projekt.fachwerkmodell#FachwerkmodellEintrag|FachwerkmodellEintrag]]
das Modell in SI ([[opencivil.projekt.aufbau.fachwerkmodell#modell_von|modell_von]]) und das Bauteil im Rechenwerk
([[opencivil.projekt.aufbau.fachwerkmodell#bauen|bauen]]). Hart scheitert nichts: was dem Modell fehlt – ein
Knoten, auf den etwas zeigt –, steht in seinen Meldungen, und der Rest des
Projekts rechnet.

## Inhalt

### modell_von

```python
def modell_von(eintrag: FachwerkmodellEintrag) -> Tuple[Modell, List[Meldung]]
```

Das Modell der Beschreibung in SI: Kräfte in N, die senkrechte nach
oben positiv. Ein Teil, das auf einen Knoten zeigt, den es nicht gibt,
fehlt im Modell; die Meldung sagt es.

### bauen

```python
def bauen(art: 'Bauteilart', eintrag: FachwerkmodellEintrag, aufbau: Aufbau) -> Bauteil
```

Ein Fachwerkmodell: sein Modell, angemeldet im Rechenwerk.


## Braucht

- [[opencivil.decke.geometrie]]
- [[opencivil.fachwerkmodell.modell]]
- [[opencivil.fachwerkmodell.werk]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.faelle]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.fachwerkmodell]]
- [[opencivil.stabwerk.system]]

## Gebraucht von

- [[opencivil.projekt.aufbau]]
