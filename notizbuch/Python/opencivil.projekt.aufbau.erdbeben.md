---
erzeugt: 2bcc22c2a787
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/aufbau/erdbeben.py
> ein Gebaeude im Erdbeben wird Rechnung.
> Paket [[opencivil.projekt.aufbau]] · [Quelltext](../../opencivil/projekt/aufbau/erdbeben.py)

## VERANTWORTUNG

Aus einem [[opencivil.projekt.erdbeben#ErdbebenEintrag|ErdbebenEintrag]] das
[[opencivil.erdbeben.ersatzkraft#Gebaeude|Gebaeude]] und sein
Ersatzkraftverfahren ([[opencivil.projekt.aufbau.erdbeben#bauen|bauen]]). Jedes Geschoss nimmt seinen Kern aus
einer Querschnittsanalyse des Projekts, mit deren Beton und ihren Teilen –
was ihm dazu fehlt, sagt [[opencivil.projekt.aufbau.erdbeben#kerne|kerne]], fuer die Rechnung und fuer das Bild.

## Inhalt

### bauen

```python
def bauen(art: 'Bauteilart', eintrag: ErdbebenEintrag, aufbau: Aufbau) -> Bauteil
```

Ein Gebaeude und sein Ersatzkraftverfahren, sobald es ein Geschoss hat
und jedes Geschoss einen Kern, der rechnet. Rechnet einer nicht, rechnet
das Gebaeude nicht: ohne ihn stimmten Schwingzeit und Verteilung nicht,
und die Zahlen saehen doch richtig aus. Ohne Kern in allen Geschossen
rechnet es nur mit T_1 von Hand – die Kraefte je Geschoss, ohne
Verteilung. Gleiche Gruende mehrerer Geschosse stehen einmal da, mit
allen Namen.

### kerne

```python
def kerne(eintrag: ErdbebenEintrag, aufbau: Aufbau) -> List[Kernbefund]
```

Je Geschoss, von unten, was sein Kern gibt oder warum er nichts gibt –
`None` in jedem, wo keines einen hat: dann rechnet das Gebaeude nur mit
T_1 von Hand. Hat eines einen, braucht jedes einen. Jede Analyse wird
einmal geprueft, auch wo viele Geschosse sie nehmen.

### kernquerschnitt

```python
def kernquerschnitt(kennung: str, aufbau: Aufbau) -> Union[Kerndaten, Grund]
```

Was ein Kern aus seiner Querschnittsanalyse nimmt – oder warum er
nichts nehmen kann, klein beginnend: noch keine gewaehlt, eine, die es
nicht mehr gibt oder die nicht rechnet, oder eine mit mehr als einem
Beton – E_cm gilt nur fuer einen. Das fehlt nur. Falsch ist eine
Analyse aus Holz, Stahl oder im Verbund
([[opencivil.querschnitt.bauweise|bauweise]]): die Steifigkeit des Kerns
nimmt E_cm, er ist aus Stahlbeton – und hat damit einen Beton.


## Konstanten

- `Kernbefund = Optional[Union[Kerndaten, Grund]]` – Was ein Geschoss von seinem Kern weiss: was er gibt, warum er nichts gibt – oder nichts, wo kein Geschoss einen Kern hat.

## Braucht

- [[opencivil.erdbeben.ersatzkraft]]
- [[opencivil.erdbeben.kern]]
- [[opencivil.material.basis]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.erdbeben]]
- [[opencivil.projekt.lesen]]
- [[opencivil.querschnitt.bauweise]]

## Gebraucht von

- [[opencivil.projekt.aufbau]]
- [[opencivil.web.erdbebendaten]]
