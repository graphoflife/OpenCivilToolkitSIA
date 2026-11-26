---
erzeugt: d4dc63bc3730
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
def bauen(art: 'Bauteilart', eintrag: QuerschnittsanalyseEintrag, aufbau: Aufbau) -> Bauteil
```

Ein gezeichneter Querschnitt: das Bauteil und seine Nachweise.

Biegung und Normalkraft immer -- ihre Eckwerte gehoeren dem Querschnitt.
Querkraft und Torsion, sobald ein Lastfall sie hat oder die
Laengszugkraft zaehlt. Duktilitaet, sproedes Versagen und die Zwaengungen
immer, still, wenn ausgeschaltet -- wie bei der Platte. Ebenso die
Stahlspannungen, sobald es Lastfaelle gibt
([[opencivil.projekt.aufbau.kern#spannungsnachweise|spannungsnachweise]]), und das
Knicken, sobald ein Fall eingeschaltet ist.

Das alles beim Stahlbeton. Ein Querschnitt aus Stahl, Holz oder im
Verbund ([[opencivil.querschnitt.bauweise|bauweise]]) rechnet bisher nur seine
Werte -- Flaeche, Schwerpunkt, Traegheitsmomente --, und seine
Zusammenfassung sagt, dass die Nachweise fehlen ([[opencivil.projekt.aufbau.querschnittsanalyse#ohne_nachweise|ohne_nachweise]]).

Ist noch nichts gezeichnet ([[opencivil.projekt.querschnittsanalyse#QuerschnittsanalyseEintrag.leer|QuerschnittsanalyseEintrag.leer]]), gibt
es nichts zu rechnen und kein Bauteil -- aber auch keinen Fehler, der das
ganze Projekt aufhielte: so beginnt jede neue Analyse (Benutzer,
2026-10-19). Ebenso eine Zeichnung, die sich noch nicht rechnen laesst,
etwa Bewehrung ohne Polygon darum: die Zeichnung sagt, was nicht
stimmt, und der Rest rechnet weiter ([[opencivil.projekt.aufbau.kern#Aufbau.unfertig|Aufbau.unfertig]]).

### ohne_nachweise

```python
def ohne_nachweise(bauweise: Bauweise) -> str
```

Warum ein Querschnitt dieser Bauweise keinen Nachweis hat -- leer beim
Stahlbeton. Ein Satzteil ohne Punkt, fuer die Zusammenfassung
([[opencivil.projekt.aufbau.kern#Aufbau.ohne_nachweis|ohne_nachweis]]) und fuer die
Zeichnung ([[opencivil.web.zeichengeometrie#geometrie|geometrie]]).

### _in_si

```python
def _in_si(fall: Any, *groessen: str) -> Dict[str, float]
```

Je Groesse `N`, `M_y` ... die Zahl ihres Feldes `N_Ed`, `M_y_Ed`
... in SI, aus der Einheit des Feldes.

### _analyse

```python
def _analyse(eintrag: QuerschnittsanalyseEintrag, baustoffe: Mapping[str, Baustoff], *, praefix: str) -> Querschnittsanalyse
```

Aus der Beschreibung das Bauteil. Laesst sich die Zeichnung nicht
rechnen, ein [[opencivil.querschnitt.geometrie#GeometrieFehler|GeometrieFehler]] mit dem ersten Grund.

### _glied

```python
def _glied(g: Mapping, stahl: Baustoff, wo: str) -> Spannglied
```

Ein Spannglied mit seinem Spannstahl -- und dem Erzeugnis, das sein
Durchmesser in der Sorte waehlt. Nennt Tabelle 7 keines, fehlt die Wahl
noch ([[opencivil.projekt.aufbau.querschnittsanalyse#erzeugnis_grund|erzeugnis_grund]]).

### erzeugnis_grund

```python
def erzeugnis_grund(name: str, sorte: str, durchmesser: float) -> str
```

Warum ein Spannglied noch kein Erzeugnis hat -- die eine Stelle fuer den
Aufbau und das Zeichenfenster ([[opencivil.web.zeichengeometrie]]). Es
fehlt nur eine Wahl, etwa nach dem Wechsel zu einer Sorte, die es nur in
Staeben gibt.


## Braucht

- [[opencivil.material.basis]]
- [[opencivil.material.spannstahl]]
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
- [[opencivil.projekt.spannglieder]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.bauweise]]
- [[opencivil.querschnitt.biegung]]
- [[opencivil.querschnitt.geometrie]]
- [[opencivil.querschnitt.spannglieder]]

## Gebraucht von

- [[opencivil.projekt.aufbau]]
- [[opencivil.web.zeichengeometrie]]
