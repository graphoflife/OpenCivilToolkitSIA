---
erzeugt: 5fd2d65b603c
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/aufbau/pfahl.py
> ein Pfahl wird Rechnung.
> Paket [[opencivil.projekt.aufbau]] · [Quelltext](../../opencivil/projekt/aufbau/pfahl.py)

## VERANTWORTUNG

Aus einem [[opencivil.projekt.pfahl#PfahlEintrag|PfahlEintrag]] der Pfahl, seine
beiden Nachweise längs der Achse, äusserer und innerer Widerstand, seine
Steifigkeit und die beiden quer dazu ([[opencivil.projekt.aufbau.pfahl#bauen|bauen]]).

## Inhalt

### bauen

```python
def bauen(art: 'Bauteilart', eintrag: PfahlEintrag, aufbau: Aufbau) -> Bauteil
```

Ein Pfahl und seine beiden Nachweise, sobald eine Kombination
eingeschaltet ist -- ohne sie steht er allein da, wie ein Grundbruch
ohne Kombination. Seine Steifigkeit, gleich ob mit Kombinationen, sobald
unter dem Fuss Boden ist; sie liest nur die Schichten, auch wenn R_a,k
aus einem Versuch kommt. Mit ihr der äussere und der innere Widerstand
quer, sobald eine Kombination quer belastet: beide lesen ihre Verläufe
und den Querschnitt des inneren Widerstands. Jede Zahl in der Einheit ihres Feldes
([[opencivil.projekt.lesen#als_groesse|als_groesse]]).


## Braucht

- [[opencivil.pfahl.aussen]]
- [[opencivil.pfahl.boden]]
- [[opencivil.pfahl.innen]]
- [[opencivil.pfahl.innen_quer]]
- [[opencivil.pfahl.pfahl]]
- [[opencivil.pfahl.quer]]
- [[opencivil.pfahl.steifigkeit]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.pfahl]]

## Gebraucht von

- [[opencivil.projekt.aufbau]]
