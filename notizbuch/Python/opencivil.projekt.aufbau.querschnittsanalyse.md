---
erzeugt: 3702adc81122
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
([[opencivil.projekt.aufbau.querschnittsanalyse#bauen|bauen]]) – dazu die Kennzahlen. Ein Querschnitt aus Stahl hat seine
eigenen ([[opencivil.projekt.aufbau.querschnittsanalyse#_stahl|_stahl]]), einer im Verbund ([[opencivil.projekt.aufbau.querschnittsanalyse#_verbund|_verbund]]), eine
Blechverbunddecke ([[opencivil.projekt.aufbau.querschnittsanalyse#_blechverbund|_blechverbund]]) und einer aus Holz auch
([[opencivil.projekt.aufbau.querschnittsanalyse#_holz|_holz]]). Eine leere oder fehlerhafte Zeichnung wird kein Bauteil,
nur ein Hinweis.

## Inhalt

### bauen

```python
def bauen(art: 'Bauteilart', eintrag: QuerschnittsanalyseEintrag, aufbau: Aufbau) -> Bauteil
```

Ein gezeichneter Querschnitt: das Bauteil und seine Nachweise.

Biegung und Normalkraft immer – ihre Eckwerte gehoeren dem Querschnitt.
Querkraft und Torsion, sobald ein Lastfall sie hat oder die
Laengszugkraft zaehlt. Duktilitaet, sproedes Versagen und die Zwaengungen
immer, still, wenn ausgeschaltet – wie bei der Platte. Ebenso die
Stahlspannungen, sobald es Lastfaelle gibt
([[opencivil.projekt.aufbau.kern#spannungsnachweise|spannungsnachweise]]), und das
Knicken, sobald ein Fall eingeschaltet ist.

Das alles beim Stahlbeton. Ein Querschnitt aus Stahl rechnet nach SIA 263
([[opencivil.projekt.aufbau.querschnittsanalyse#_stahl|_stahl]]), einer im Verbund nach SIA 264 ([[opencivil.projekt.aufbau.querschnittsanalyse#_verbund|_verbund]]), eine
Blechverbunddecke auch ([[opencivil.projekt.aufbau.querschnittsanalyse#_blechverbund|_blechverbund]]), einer aus Holz nach
SIA 265 ([[opencivil.projekt.aufbau.querschnittsanalyse#_holz|_holz]]). Einer aus mehreren Hoelzern rechnet bisher nur
seine Werte – Flaeche, Schwerpunkt, Traegheitsmomente –; seine
Zusammenfassung sagt, dass die Nachweise fehlen ([[opencivil.projekt.aufbau.querschnittsanalyse#ohne_nachweise|ohne_nachweise]]).
Seine Spannung-Dehnung-Analysen rechnet er trotzdem. Der Verbund und die
Blechverbunddecke haben noch keine ([[opencivil.projekt.aufbau.querschnittsanalyse#ohne_analysen|ohne_analysen]]).

Ist noch nichts gezeichnet ([[opencivil.projekt.querschnittsanalyse#QuerschnittsanalyseEintrag.leer|QuerschnittsanalyseEintrag.leer]]), gibt
es nichts zu rechnen und kein Bauteil – aber auch keinen Fehler, der das
ganze Projekt aufhielte: so beginnt jede neue Analyse (Benutzer,
2026-10-19). Ebenso eine Zeichnung, die sich noch nicht rechnen laesst,
etwa Bewehrung ohne Polygon darum: die Zeichnung sagt, was nicht
stimmt, und der Rest rechnet weiter ([[opencivil.projekt.aufbau.kern#Aufbau.unfertig|Aufbau.unfertig]]).

### _lastfaelle

```python
def _lastfaelle(eintrag: QuerschnittsanalyseEintrag) -> List[Lastfall]
```

Die eingeschalteten Lastfaelle in SI, aus der Einheit ihrer Felder: N, M_y ... aus N_Ed, M_y_Ed ...

### _stahl

```python
def _stahl(eintrag: QuerschnittsanalyseEintrag, analyse: Querschnittsanalyse, teil: Bauteil, aufbau: Aufbau) -> Bauteil
```

Ein Querschnitt aus Stahl nach SIA 263 ([[opencivil.nachweis.qa_stahl|qa_stahl]]):
je Lastfall Biegung und Normalkraft, Querkraft, sobald einer sie hat –
beide lesen den Widerstand gegen Querkraft aus den Kennzahlen. Torsion
weist er nicht nach; ein Lastfall mit `T_Ed` sagt es. Knicken und
Kippen, sobald ein Fall eingeschaltet ist
([[opencivil.nachweis.qa_stahl_stabilitaet|qa_stahl_stabilitaet]]). Die Kennzahlen
stehen in der Herleitung vor den Nachweisen, die aus ihnen lesen.

### _verbund

```python
def _verbund(eintrag: QuerschnittsanalyseEintrag, analyse: Querschnittsanalyse, teil: Bauteil, aufbau: Aufbau) -> Bauteil
```

Ein Querschnitt aus Baustahl und Beton nach SIA 264
([[opencivil.nachweis.qa_verbund|qa_verbund]]): je Lastfall Biegung und
Normalkraft, plastisch, und Querkraft, sobald einer sie hat – die traegt
der Stahl allein. Beide lesen den Widerstand gegen Querkraft aus den
Kennzahlen. Mit Kopfbolzenduebeln steht ihr `P_Rd` in den Kennzahlen,
und je Lastfall die Verduebelung bei Biegung und Normalkraft, mit seiner
Zahl der Duebel. Torsion weist er nicht nach; ein Lastfall mit `T_Ed`
sagt es. Sobald ein Stabilitaetsfall eingeschaltet ist, die
Verbundstuetze ([[opencivil.nachweis.qa_verbund_stuetze|qa_verbund_stuetze]]); das
Kippen des Verbundtraegers fehlt noch, ebenso die
Spannung-Dehnung-Analysen ([[opencivil.projekt.aufbau.querschnittsanalyse#ohne_analysen|ohne_analysen]]).

### _blechverbund

```python
def _blechverbund(eintrag: QuerschnittsanalyseEintrag, analyse: Querschnittsanalyse, teil: Bauteil, aufbau: Aufbau) -> Bauteil
```

Eine Blechverbunddecke nach SIA 264, 5.4
([[opencivil.nachweis.qa_blechverbund|qa_blechverbund]]): je Lastfall Biegung und
Normalkraft, plastisch, und Querkraft und Laengsschub, sobald einer
`V_z` hat – beide lesen ihre Widerstaende aus den Kennzahlen. Die
Decke traegt in einer Richtung: ein Lastfall mit `M_z`, `V_y` oder
`T` sagt, dass sie nicht nachgewiesen werden. Eine Analyse rechnet
eine Decke ([[opencivil.projekt.querschnittsanalyse#QuerschnittsanalyseEintrag.elemente|QuerschnittsanalyseEintrag.elemente]]).

### _holz

```python
def _holz(eintrag: QuerschnittsanalyseEintrag, analyse: Querschnittsanalyse, teil: Bauteil, aufbau: Aufbau) -> Bauteil
```

Ein Querschnitt aus einem einzigen Holz nach SIA 265: seine Werte fuer die
Feuchteklasse der Analyse ([[opencivil.nachweis.qa_holz_werte|qa_holz_werte]]), je
Lastfall Biegung und Normalkraft, Schub und Torsion, sobald einer sie hat
([[opencivil.nachweis.qa_holz|qa_holz]]), Knicken und Kippen, sobald ein Fall
eingeschaltet ist ([[opencivil.nachweis.qa_holz_stabilitaet|qa_holz_stabilitaet]]). Alle
lesen aus den Werten; «stossartig» gilt je Fall.

### _stossartig

```python
def _stossartig(faelle: Iterable[Any]) -> frozenset
```

Die Namen der eingeschalteten Faelle, die stossartig sind.

### _kennzahlen

```python
def _kennzahlen(kennzahlen: Kennzahlprozedur, teil: Bauteil, aufbau: Aufbau) -> None
```

Die Kennzahlen ins Rechenwerk und unter das Bauteil.

### ohne_nachweise

```python
def ohne_nachweise(bauweise: Bauweise, stoffe: Iterable[Tuple[Baustoffart, str]]) -> str
```

Warum ein Querschnitt dieser Bauweise keinen Nachweis hat – leer bei
jeder Bauweise (Stahl, Holz und Verbund seit 2026-11-26) ausser beim
Holz aus mehreren Hoelzern: es braeuchte einen nach ihren Steifigkeiten
gewichteten Querschnitt, den das Werkzeug nicht rechnet (nach Vorgabe,
nicht nachgeschlagen). `stoffe`: Art und Name jedes Baustoffs, wie fuer
[[opencivil.querschnitt.bauweise#bauweise|bauweise]]. Ein Satzteil ohne
Punkt, fuer die Zusammenfassung
([[opencivil.projekt.aufbau.kern#Aufbau.ohne_nachweis|ohne_nachweis]]) und fuer die
Zeichnung ([[opencivil.web.zeichengeometrie#geometrie|geometrie]]).

### ohne_diagramm

```python
def ohne_diagramm(bauweise: Bauweise, stoffe: Iterable[Tuple[Baustoffart, str]]) -> str
```

Warum ein Querschnitt dieser Bauweise kein Interaktionsdiagramm hat –
leer beim Stahlbeton, dem einzigen mit einer Widerstandsflaeche. Ein
Satz mit Punkt, fuer die Diagramme
([[opencivil.web.diagrammdaten|analyse_diagramme]]); `stoffe` wie
bei [[opencivil.projekt.aufbau.querschnittsanalyse#ohne_nachweise|ohne_nachweise]].

### ohne_analysen

```python
def ohne_analysen(bauweise: Bauweise) -> str
```

Warum ein Querschnitt dieser Bauweise keine Spannung-Dehnung-Analyse hat
– leer, wo er eine hat. Ein Satz mit Punkt, fuer die Zeichnung
([[opencivil.web.zeichengeometrie#geometrie|geometrie]]). Der Verbund und die
Blechverbunddecke rechnen ihre Nachweise plastisch; ihre Linien
braeuchten den Riss am ideellen Querschnitt, mit `E_a/E_cm` gewichtet,
und die Werte der Analyse sind ungewichtet.

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

Ein Spannglied mit seinem Spannstahl – und dem Erzeugnis, das sein
Durchmesser in der Sorte waehlt. Nennt Tabelle 7 keines, fehlt die Wahl
noch ([[opencivil.projekt.aufbau.querschnittsanalyse#erzeugnis_grund|erzeugnis_grund]]).

### erzeugnis_grund

```python
def erzeugnis_grund(name: str, sorte: str, durchmesser: float) -> str
```

Warum ein Spannglied noch kein Erzeugnis hat – die eine Stelle fuer den
Aufbau und das Zeichenfenster ([[opencivil.web.zeichengeometrie]]). Es
fehlt nur eine Wahl, etwa nach dem Wechsel zu einer Sorte, die es nur in
Staeben gibt.


## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.material.basis]]
- [[opencivil.material.spannstahl]]
- [[opencivil.nachweis.qa_blechverbund]]
- [[opencivil.nachweis.qa_gebrauch]]
- [[opencivil.nachweis.qa_holz]]
- [[opencivil.nachweis.qa_holz_kennzahlen]]
- [[opencivil.nachweis.qa_holz_stabilitaet]]
- [[opencivil.nachweis.qa_holz_werte]]
- [[opencivil.nachweis.qa_kennzahlen]]
- [[opencivil.nachweis.qa_knicken]]
- [[opencivil.nachweis.qa_stahl]]
- [[opencivil.nachweis.qa_stahl_kennzahlen]]
- [[opencivil.nachweis.qa_stahl_stabilitaet]]
- [[opencivil.nachweis.qa_verbund]]
- [[opencivil.nachweis.qa_verbund_kennzahlen]]
- [[opencivil.nachweis.qa_verbund_stuetze]]
- [[opencivil.nachweis.richtungsnachweise]]
- [[opencivil.nachweis.schiefe_biegung]]
- [[opencivil.nachweis.schubwandnachweis]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.blechdecken]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.projekt.spannglieder]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.bauweise]]
- [[opencivil.querschnitt.biegung]]
- [[opencivil.querschnitt.geometrie]]
- [[opencivil.querschnitt.profilblech]]
- [[opencivil.querschnitt.spannglieder]]
- [[opencivil.verbund.duebel]]

## Gebraucht von

- [[opencivil.projekt.aufbau]]
- [[opencivil.web.diagrammdaten]]
- [[opencivil.web.zeichengeometrie]]
