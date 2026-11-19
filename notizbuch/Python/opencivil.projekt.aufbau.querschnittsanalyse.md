---
erzeugt: 98f8d6d49866
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/aufbau/querschnittsanalyse.py
> ein gezeichneter Querschnitt wird Rechnung.
> Paket [[opencivil.projekt.aufbau]] · [Quelltext](../../opencivil/projekt/aufbau/querschnittsanalyse.py)

## VERANTWORTUNG

Aus einem [[opencivil.projekt.querschnittsanalyse#QuerschnittsanalyseEintrag|QuerschnittsanalyseEintrag]]
die [[opencivil.querschnitt.analyse#Querschnittsanalyse|Querschnittsanalyse]] und ihre
Nachweise: Biegung und Normalkraft, Querkraft und Torsion, Duktilitaet,
sproedes Versagen, die Zwaengungen, die Stahlspannungen und das Knicken
([[opencivil.projekt.aufbau.querschnittsanalyse#bauen|bauen]]) -- dazu die Kennzahlen. Eine leere oder fehlerhafte
Zeichnung wird kein Bauteil, nur ein Hinweis.

## Inhalt

### bauen

```python
def bauen(art: 'Bauteilart', eintrag: QuerschnittsanalyseEintrag, aufbau: Aufbau) -> Optional[Bauteil]
```

Ein gezeichneter Querschnitt: das Bauteil und seine Nachweise.

Biegung und Normalkraft immer -- ihre Eckwerte gehoeren dem Querschnitt.
Querkraft und Torsion, sobald ein Lastfall sie hat oder die
Laengszugkraft zaehlt. Duktilitaet, sproedes Versagen und die Zwaengungen
immer, still, wenn ausgeschaltet -- wie bei der Platte. Ebenso die
Stahlspannungen, sobald es Lastfaelle gibt
([[opencivil.projekt.aufbau.kern#spannungsnachweise|spannungsnachweise]]), und das
Knicken, sobald ein Fall eingeschaltet ist.

Ist noch nichts gezeichnet ([[opencivil.projekt.querschnittsanalyse#QuerschnittsanalyseEintrag.leer|QuerschnittsanalyseEintrag.leer]]), gibt
es nichts zu rechnen und kein Bauteil -- aber auch keinen Fehler, der das
ganze Projekt aufhielte: so beginnt jede neue Analyse (Benutzer,
2026-10-19). Ebenso eine Zeichnung, die sich noch nicht rechnen laesst,
etwa Bewehrung ohne Polygon darum: die Zeichnung sagt, was nicht
stimmt, und der Rest rechnet weiter ([[opencivil.projekt.aufbau.kern#Aufbau.unfertig|Aufbau.unfertig]]).

### _analyse

```python
def _analyse(eintrag: QuerschnittsanalyseEintrag, baustoffe: Mapping[str, Baustoff], *, praefix: str) -> Querschnittsanalyse
```

Aus der Beschreibung das Bauteil. Laesst sich die Zeichnung nicht
rechnen, ein [[opencivil.querschnitt.geometrie#GeometrieFehler|GeometrieFehler]] mit dem ersten Grund.


## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.material.basis]]
- [[opencivil.nachweis.qa_gebrauch]]
- [[opencivil.nachweis.qa_kennzahlen]]
- [[opencivil.nachweis.qa_knicken]]
- [[opencivil.nachweis.richtungsnachweise]]
- [[opencivil.nachweis.schiefe_biegung]]
- [[opencivil.nachweis.schubwandnachweis]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.biegung]]
- [[opencivil.querschnitt.geometrie]]

## Gebraucht von

- [[opencivil.projekt.aufbau]]
