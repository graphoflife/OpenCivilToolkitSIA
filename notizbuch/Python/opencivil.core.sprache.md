---
erzeugt: f232479482aa
art: modul
tags: [modul]
---
> [!abstract] opencivil/core/sprache.py
> wie das Werkzeug Woerter in einen Satz setzt.
> Paket [[opencivil.core]] · [Quelltext](../../opencivil/core/sprache.py)

## VERANTWORTUNG

«A, B und C», «Beton, Baustahl oder Holz»: die eine Stelle, an der eine
Aufzaehlung zum Satzteil wird. Bis 2026-11-27 stand dieselbe Zeile an fuenf
Stellen, zweimal als eigene Hilfe. Dazu ein Satzteil am Satzanfang.

## Inhalt

### aufgezaehlt

```python
def aufgezaehlt(teile: Sequence[str], wort: str='und') -> str
```

«A», «A und B», «A, B und C» – mit `wort` «oder»: «A, B oder C».

### satzanfang

```python
def satzanfang(text: str) -> str
```

Der Satzteil mit grossem Anfang: «an der Stufe von …» – «An der Stufe von …».


## Gebraucht von

- [[opencivil.durchstanzen.kennzahl]]
- [[opencivil.durchstanzen.mit_bewehrung]]
- [[opencivil.durchstanzen.nachweis]]
- [[opencivil.material.arten]]
- [[opencivil.mauerwerk.herleitung]]
- [[opencivil.mauerwerk.pruefen]]
- [[opencivil.nachweis.qa_verbund_werte]]
- [[opencivil.projekt.aufbau.aus_system]]
- [[opencivil.projekt.aufbau.balkensystem]]
- [[opencivil.querschnitt.bauweise]]
- [[opencivil.stabwerk.stellen]]
- [[opencivil.verbund.blechdecke]]
- [[opencivil.web.mauerwerkdaten]]
