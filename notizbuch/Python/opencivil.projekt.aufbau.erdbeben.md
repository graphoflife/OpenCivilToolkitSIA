---
erzeugt: dacb5334b4f0
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/aufbau/erdbeben.py
> ein Gebaeude im Erdbeben wird Rechnung.
> Paket [[opencivil.projekt.aufbau]] · [Quelltext](../../opencivil/projekt/aufbau/erdbeben.py)

## VERANTWORTUNG

Aus einem [[opencivil.projekt.erdbeben#ErdbebenEintrag|ErdbebenEintrag]] das
[[opencivil.erdbeben.ersatzkraft#Gebaeude|Gebaeude]] und sein
Ersatzkraftverfahren ([[opencivil.projekt.aufbau.erdbeben#bauen|bauen]]). Jede Wand nimmt ihren Querschnitt aus
einer Querschnittsanalyse des Projekts, mit deren Beton – was ihr dazu
fehlt, sagt [[opencivil.projekt.aufbau.erdbeben#wandquerschnitt|wandquerschnitt]], fuer die Rechnung und fuer das Bild.

## Inhalt

### bauen

```python
def bauen(art: 'Bauteilart', eintrag: ErdbebenEintrag, aufbau: Aufbau) -> Bauteil
```

Ein Gebaeude und sein Ersatzkraftverfahren, sobald es ein Geschoss hat
und jede Wand einen Querschnitt. Rechnet eine Wand nicht, rechnet das
Gebaeude nicht: ohne sie stimmten Schwingzeit und Verteilung nicht, und
die Zahlen saehen doch richtig aus. Ohne Wand rechnet es nur mit T_1 von
Hand – die Kraefte je Geschoss, ohne Verteilung. Gleiche Gruende
mehrerer Waende stehen einmal da, mit allen Namen.

### wandquerschnitt

```python
def wandquerschnitt(wand: TragwandEintrag, aufbau: Aufbau) -> Union[Wandquerschnitt, Grund]
```

Was eine Wand aus ihrer Querschnittsanalyse nimmt – oder warum sie
nichts nehmen kann, klein beginnend: noch keine gewaehlt, eine, die es
nicht mehr gibt oder die nicht rechnet, oder eine mit mehr als einem
Beton – E_cm gilt nur fuer einen. Das fehlt nur. Falsch ist eine
Analyse aus Holz, Stahl oder im Verbund
([[opencivil.querschnitt.bauweise|bauweise]]): die Steifigkeit einer Wand
nimmt E_cm, sie ist aus Stahlbeton – und hat damit einen Beton.


## Braucht

- [[opencivil.erdbeben.ersatzkraft]]
- [[opencivil.material.basis]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.erdbeben]]
- [[opencivil.projekt.lesen]]
- [[opencivil.querschnitt.bauweise]]

## Gebraucht von

- [[opencivil.projekt.aufbau]]
- [[opencivil.web.erdbebendaten]]
