---
erzeugt: 94b2c1902116
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/aufbau/querschnittsanalyse.py
> ein gezeichneter Querschnitt wird Rechnung.
> Paket [[opencivil.projekt.aufbau]] · [Quelltext](../../opencivil/projekt/aufbau/querschnittsanalyse.py)

## VERANTWORTUNG

Aus einem [[opencivil.projekt.querschnittsanalyse#QuerschnittsanalyseEintrag|QuerschnittsanalyseEintrag]]
die [[opencivil.querschnitt.analyse#Querschnittsanalyse|Querschnittsanalyse]] -- jeder Fehler
der Zeichnung als Satz, der sie nennt -- und ihre Nachweise: Biegung und
Normalkraft, Querkraft und Torsion, Duktilitaet, sproedes Versagen, die
Zwaengungen, die Stahlspannungen und das Knicken ([[opencivil.projekt.aufbau.querschnittsanalyse#bauen|bauen]]) -- dazu die
Kennzahlen.

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
2026-10-19).

### _analyse

```python
def _analyse(eintrag: QuerschnittsanalyseEintrag, baustoffe: Mapping[str, Baustoff], *, praefix: str) -> Querschnittsanalyse
```

Aus der Beschreibung das Bauteil -- und aus jedem Fehler der Zeichnung
einen Satz, der die Analyse nennt.


## Braucht

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
