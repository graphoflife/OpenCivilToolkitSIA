---
erzeugt: 79138f0189c2
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/aufbau/fachwerkmodell.py
> ein Fachwerkmodell wird Rechnung.
> Paket [[opencivil.projekt.aufbau]] · [Quelltext](../../opencivil/projekt/aufbau/fachwerkmodell.py)

## VERANTWORTUNG

Aus einem [[opencivil.projekt.fachwerkmodell#FachwerkmodellEintrag|FachwerkmodellEintrag]]
das Modell in SI ([[opencivil.projekt.aufbau.fachwerkmodell#modell_von|modell_von]]), die Zahlen seines Verfahrens
([[opencivil.projekt.aufbau.fachwerkmodell#einstellung_von|einstellung_von]]) und das Bauteil im Rechenwerk ([[opencivil.projekt.aufbau.fachwerkmodell#bauen|bauen]]).
Hart scheitert nichts: was dem Modell fehlt – ein Knoten, auf den etwas
zeigt –, steht in seinen Meldungen, und der Rest des Projekts rechnet.

## Inhalt

### modell_von

```python
def modell_von(eintrag: FachwerkmodellEintrag) -> Tuple[Modell, List[Meldung]]
```

Das Modell der Beschreibung in SI: Kräfte in N, die senkrechte nach
oben positiv. Ein Teil, das auf einen Knoten zeigt, den es nicht gibt,
fehlt im Modell; die Meldung sagt es.

### einstellung_von

```python
def einstellung_von(eintrag: FachwerkmodellEintrag) -> Einstellung
```

Die Zahlen des Verfahrens in SI: die Rasterweite in m, N_min als Teil der grössten Kraft.

### bauen

```python
def bauen(art: 'Bauteilart', eintrag: FachwerkmodellEintrag, aufbau: Aufbau) -> Bauteil
```

Ein Fachwerkmodell: sein Modell und sein Verfahren, angemeldet im Rechenwerk.


## Braucht

- [[opencivil.decke.geometrie]]
- [[opencivil.fachwerkmodell.modell]]
- [[opencivil.fachwerkmodell.suche]]
- [[opencivil.fachwerkmodell.werk]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.faelle]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.fachwerkmodell]]
- [[opencivil.projekt.lesen]]
- [[opencivil.stabwerk.system]]

## Gebraucht von

- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.fachwerkmodell]]
- [[opencivil.web.fachwerkdaten]]
