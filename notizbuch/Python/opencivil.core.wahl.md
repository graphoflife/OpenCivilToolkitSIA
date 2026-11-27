---
erzeugt: fe405f3b66d7
art: modul
tags: [modul]
---
> [!abstract] opencivil/core/wahl.py
> was ein Wahlfeld annehmen kann.
> Paket [[opencivil.core]] · [Quelltext](../../opencivil/core/wahl.py)

## VERANTWORTUNG

Die Grundlage jeder Wahl im Projekt: Rechenart, Wertesatz, Zugseite,
Rissanforderung und die übrigen. Ein Mitglied ist zugleich sein Text –
`Rechenart.BLOCK == "block"`, und `json.dumps` schreibt `"block"` –,
und es gibt sich als dieser Text aus, in Meldungen und in Formeln. Ein
Text, den es nicht gibt, meldet sich mit den möglichen Werten.

Bis 2026-10-17 trug jede Wahl ihr eigenes `__str__` oder keines: acht von
zwölf schrieben sich in einer Meldung als «Rechenart.BLOCK».

## Inhalt

### Wahl

```python
class Wahl(StrEnum)
```

Eine Wahl: das Mitglied ist sein Text.


## Gebraucht von

- [[opencivil.bewehrungssuche.laengs]]
- [[opencivil.decke.modell]]
- [[opencivil.durchstanzen.flaeche]]
- [[opencivil.durchstanzen.stelle]]
- [[opencivil.durchstanzen.systeme]]
- [[opencivil.erdbeben.ersatzkraft]]
- [[opencivil.geotechnik.setzung]]
- [[opencivil.geotechnik.verhalten]]
- [[opencivil.material.basis]]
- [[opencivil.material.holz]]
- [[opencivil.material.spannstahl]]
- [[opencivil.nachweis.biegung_normalkraft]]
- [[opencivil.nachweis.rissanforderung]]
- [[opencivil.pfahl.boden]]
- [[opencivil.pfahl.pfahl]]
- [[opencivil.projekt.balkensystem]]
- [[opencivil.projekt.staebe]]
- [[opencivil.querschnitt.bauweise]]
- [[opencivil.querschnitt.geometrie]]
- [[opencivil.querschnitt.gesetzwahl]]
- [[opencivil.querschnitt.platte]]
- [[opencivil.querschnitt.spannglieder]]
- [[opencivil.querschnitt.zugseite]]
- [[opencivil.spannungsanalyse.art]]
- [[opencivil.stabwerk.modell]]
- [[opencivil.stabwerk3d.modell]]
- [[opencivil.stahlbau.stabilitaet]]
- [[opencivil.stahlprofile.bleche]]
- [[opencivil.verbund.blechdecke]]
- [[opencivil.verbund.duebel]]
