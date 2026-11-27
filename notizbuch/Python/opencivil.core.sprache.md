---
erzeugt: 6aea9ba560b2
art: modul
tags: [modul]
---
> [!abstract] opencivil/core/sprache.py
> wie das Werkzeug eine Liste von Woertern in einen Satz setzt.
> Paket [[opencivil.core]] · [Quelltext](../../opencivil/core/sprache.py)

## VERANTWORTUNG

«A, B und C», «Beton, Baustahl oder Holz»: die eine Stelle, an der eine
Aufzaehlung zum Satzteil wird. Bis 2026-11-27 stand dieselbe Zeile an fuenf
Stellen, zweimal als eigene Hilfe.

## Inhalt

### aufgezaehlt

```python
def aufgezaehlt(teile: Sequence[str], wort: str='und') -> str
```

«A», «A und B», «A, B und C» – mit `wort` «oder»: «A, B oder C».


## Gebraucht von

- [[opencivil.nachweis.qa_verbund_werte]]
- [[opencivil.projekt.aufbau.balkensystem]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.querschnitt.bauweise]]
- [[opencivil.verbund.blechdecke]]
