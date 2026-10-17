---
erzeugt: 4bdf3c9f4b1e
art: modul
tags: [modul]
---
> [!abstract] opencivil/core/wahl.py
> was ein Wahlfeld annehmen kann.
> Paket [[opencivil.core]] · [Quelltext](../../opencivil/core/wahl.py)

## VERANTWORTUNG

Die Grundlage jeder Wahl im Projekt: Rechenart, Wertesatz, Zugseite,
Rissanforderung und die übrigen. Ein Mitglied ist zugleich sein Text --
`Rechenart.BLOCK == "block"`, und `json.dumps` schreibt `"block"` --,
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
- [[opencivil.material.basis]]
- [[opencivil.nachweis.biegung_normalkraft]]
- [[opencivil.nachweis.querschnittsloeser]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.nachweis.rissanforderung]]
- [[opencivil.querschnitt.geometrie]]
- [[opencivil.querschnitt.platte]]
- [[opencivil.querschnitt.schnittanalyse]]
- [[opencivil.spannungsanalyse]]
- [[opencivil.stabwerk.modell]]
