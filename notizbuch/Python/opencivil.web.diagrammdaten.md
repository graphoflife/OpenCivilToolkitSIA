---
erzeugt: 8ab2e231fc9f
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/diagrammdaten.py
> was die Oberflaeche zeichnet, als JSON.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/diagrammdaten.py)

## VERANTWORTUNG

Die Punktfolgen der Diagramme: M-N-Interaktionslinien samt Knickpunkten,
Werkstoffgesetze, Querkraft ueber Moment und ueber Neigung, die Bilder der
Spannung-Dehnung-Analyse. Aus [[opencivil.web.api]] herausgeloest, das
damit nur noch Katalog, Mitschrift, Loesung und Zusammenfassung abbildet.

Wie dort wird hier nichts nachgerechnet, was der Kern schon weiss: die Kurven
kommen aus denselben Funktionen wie die Nachweise, hier werden sie in kN,
kNm und mm umgesetzt.

## Inhalt

### linien

```python
def linien(aufbau: Aufbau, loesung: Loesung) -> dict
```

Je gerechneter M-N-Nachweis seine Linien, dazu die Bemessungs- und Knickpunkte.

### querkraftkurven

```python
def querkraftkurven(aufbau: Aufbau, loesung: Loesung, gewaehlt: Optional[Mapping[str, float]]=None) -> dict
```

Der Querkraftwiderstand ueber dem Moment -- eine Kurve je Tragrichtung.

Eine je Platte ohne Buegel, auch ohne Querkraft: dann rechnet der
Nachweis still, nur fuer dieses Bild. Die Waagrechte ist vorzeichenbehaftet: rechts das positive
Moment (Zug unten), links das negative (Zug oben). Beide Aeste im selben
Bild, weil sie dieselbe Platte beschreiben.

Einen Ast gibt es nur, wo auf der gezogenen Seite Bewehrung liegt. Fehlt
sie, gibt es kein `d` -- und ohne `d` keinen Widerstand.

`v_Rd` haengt ueber `m_Rd(N_Ed)` von der Normalkraft ab. Welche gilt,
waehlt der Benutzer unter dem Diagramm; `gewaehlt` bildet die Kennung auf
diese Normalkraft in kN ab. Ohne Angabe gilt die des ersten Falls dieser
Richtung -- dann liegen dessen Punkte auf der Kurve.

Einheiten wie in den anderen Diagrammen: kNm und kN/m.

### neigungskurven

```python
def neigungskurven(aufbau: Aufbau, loesung: Loesung) -> dict
```

Der Querkraftwiderstand ueber der Neigung der Druckdiagonalen.

Nur wo Buegel liegen -- sonst haengt der Widerstand am Moment und das
andere Diagramm gilt.

**Ein Bild je statischer Hoehe und Neigungsbereich.** Beides haengt am
einzelnen Fall: `d` am Vorzeichen des Moments, der Bereich am Vorzeichen
der Normalkraft. Faelle, die darin uebereinstimmen, liegen auf derselben
Kurve und kommen ins selbe Bild; die anderen bekommen ihr eigenes.

Gezeichnet wird ueber den ganzen Achsenbereich, auch ausserhalb der beiden
Grenzen -- dort blass. Die Oberflaeche entscheidet das an `gewaehlt`,
gerechnet wird beides hier.

### _bild_dict

```python
def _bild_dict(bild, h: float) -> dict
```

Ein Querschnittsbild in Zeichengroessen: mm, Promille, N/mm², kN.

### spannungsanalysen

```python
def spannungsanalysen(aufbau: Aufbau, loesung: Loesung) -> dict
```

Die Auswertungen am Querschnitt, je Platte -- fertig zum Zeichnen.

Gerechnet wird in [[opencivil.spannungsanalyse#analysen|opencivil.spannungsanalyse.analysen]]; hier wird
nur in Zeichengroessen abgebildet.

### _linie_dict

```python
def _linie_dict(linie) -> dict
```

Eine Linie in Zeichengroessen: die Kraft in kNm bzw. kN, die Verformung
als Kruemmung in 1/m bzw. als Dehnung in Promille.

### _modul_dict

```python
def _modul_dict(modul) -> dict
```

Der aequivalente E-Modul in Zeichengroessen: die laufende Kraft in kNm
bzw. kN, der Modul in N/mm², dazu E_cm, an dem er sich misst. Gerechnet
ist alles im Kern ([[opencivil.spannungsanalyse#Modullinie|Modullinie]]).

### werkstoffgesetze

```python
def werkstoffgesetze(aufbau: Aufbau, loesung: Loesung) -> dict
```

Punktfolgen der Spannungs-Dehnungs-Beziehungen, je Material.

Gerechnet wird mit denselben Gesetzen wie im Nachweis -- die Kurve zeigt
also genau das, was der Querschnittsintegration zugrunde liegt, und nicht
eine zweite, nachgebaute Fassung.

Vorzeichen wie im ganzen Werkzeug: Zug positiv. Der Beton liegt damit im
dritten Quadranten, der Stahl spannt sich ueber beide.

### _betonkurve

```python
def _betonkurve(stoff, wert, schritte: int=80) -> Optional[dict]
```

Parabel-Rechteck-Beziehung, von null bis zur Bruchdehnung.

### _spannungsblock

```python
def _spannungsblock(f_cd: float, eps_c2d: float) -> dict
```

Der vereinfachte, rechteckige Spannungsverlauf.

Unterhalb von `(1 - 0.85) * eps_c2d` wird keine Spannung angesetzt,
darueber durchgehend `f_cd`. Das ist dieselbe Vereinfachung, die auch der
Handrechnung zugrunde liegt -- dort als Druckzone der Hoehe `0.85 x`.
Beide Bilder gehoeren zusammen, und genau deshalb steht die Stufe hier neben
der Parabel: man sieht, was man aufgibt, wenn man von Hand rechnet.

### _stahlkurve

```python
def _stahlkurve(stoff, wert) -> Optional[dict]
```

Bilineare Beziehung ohne Verfestigung.

Fuenf Eckpunkte genuegen -- dazwischen ist sie gerade, und mehr Punkte
wuerden nur vortaeuschen, dass etwas gekruemmt waere.

### _knickpunkte

```python
def _knickpunkte(aufbau, nachweis, loesung) -> list
```

Die Knicknachweise als Punktepaare fuer das M-N-Diagramm.

Zu jedem Fall zwei Punkte auf derselben Hoehe N_Ed: das Moment 1. Ordnung
und das am verformten System. Die Strecke dazwischen ist der Zuwachs aus
Schiefstellung und Verformung -- im Diagramm sieht man sofort, ob er den
Punkt ueber die Linie schiebt.

Nur in x-Richtung, denn nur dort gibt es einen Knicknachweis.

### _knicken

```python
def _knicken(aufbau, nachweis)
```

Der Knicknachweis zu diesem M-N-Nachweis -- nur in x, nur wenn es ihn gibt.

### _linienzug

```python
def _linienzug(linie) -> Optional[dict]
```

Eine Resistenzlinie zum Zeichnen. `ecken`: ob ihre Punkte Eckpunkte mit
Namen sind -- beim Polygon der Handrechnung --, oder Stuetzstellen eines
Randes, die man nicht einzeln markiert.

### linie

```python
def linie(nachweis, loesung: Loesung, aufbau=None) -> dict
```

Die M-N-Interaktionslinien zum Zeichnen -- in kN und kNm.

Die massgebende Linie, gegen die nachgewiesen wird, und daneben die zum
Vergleich: die Parabel neben der Handrechnung, sonst die Handrechnung.
So sieht man, was die gewaehlte Rechenart gegenueber der anderen kostet
oder bringt.

### analyse

```python
def analyse(aufbau: Aufbau, loesung: Loesung, kennung: str, schnitt: Tuple[str, float]=('M_z', 0.0)) -> dict
```

Die Diagramme einer Querschnittsanalyse -- in mm, kN und kNm.

Das Interaktionsdiagramm: die Flaeche aller Bruchzustaende, geschnitten
bei `schnitt` -- der festen Groesse (N, M_y oder M_z) und ihrem Wert in
kN bzw. kNm. Welche beiden anderen auf welcher Achse stehen, waehlt die
Oberflaeche; die Punkte tragen alle drei. Es ist das einzige
Interaktionsdiagramm der Analyse: je Lastfall stehen darin seine
Einwirkung und der Widerstand seines Nachweises, ebenfalls mit allen
drei Groessen.

Je Lastfall ausserdem der Bruchzustand im Schnitt (Nulllinie, Druckzone,
die Dehnung jedes Stabs) und der Schubfluss in den Waenden. Was die
Nachweise schon wissen, kommt aus ihren Befunden in `loesung`; neu
gerechnet wird nur die Flaeche, nach der kein Nachweis fragt -- an
demselben Querschnitt.

Die Einwirkung steht so da, wie nachgewiesen: mit der Laengszugkraft aus
Querkraft und Torsion, wo sie zugeschaltet ist.

### _als_kn

```python
def _als_kn(punkte) -> List[dict]
```

Punkte `(N, M_y, M_z)` in N und Nm -- fuer die Oberflaeche in kN und kNm.

### _faecherpaar

```python
def _faecherpaar(q, psi: float)
```

Der Faecher bei ψ und der gegenueber -- zusammen eine geschlossene Linie.

### _interaktion

```python
def _interaktion(q, einachsig: bool, fest: str, wert: float) -> dict
```

Das Interaktionsdiagramm der Analyse: die Flaeche der Bruchzustaende,
geschnitten bei `fest = wert` (kN bzw. kNm).

Einachsig gibt es nur die Linie um y: die Nulllinie bleibt waagrecht,
und das M_z, das ein unsymmetrischer Querschnitt dabei weckt, zaehlt
nicht -- dieselben Faecher wie im Nachweis.

### _tiefe

```python
def _tiefe(eltern: Sequence[Optional[int]], i: int) -> int
```

Wie oft ein Polygon in einem anderen liegt -- Eltern werden zuerst gezeichnet.

### _zeichnung

```python
def _zeichnung(bauteil) -> dict
```

Was im Schnitt zu sehen ist, in mm -- die Stäbe der Linien schon aufgeloest.

### _halbebene

```python
def _halbebene(punkte: Sequence[Punkt], innen: Callable[[Punkt], float]) -> List[List[float]]
```

Das Stueck eines Polygons, auf dem `innen(p) <= 0` gilt -- nach
Sutherland und Hodgman, gegen eine einzige Gerade.

### _gerade_im_rahmen

```python
def _gerade_im_rahmen(stuetz: Punkt, richtung: Punkt, rahmen: Tuple[float, float, float, float]) -> Optional[List[List[float]]]
```

Das Stueck der Geraden `stuetz + s·richtung`, das im Rahmen liegt (Liang-Barsky).

### _bruch

```python
def _bruch(q, bauteil, punkt) -> dict
```

Der Bruchzustand im Schnitt: die Nulllinie, die gedrueckte Flaeche je
Polygon und die Dehnung jedes Stabs -- in mm und ‰.

Gedrueckt ist die Seite kleiner v: die Kruemmung zeigt nie gegen die
Zugrichtung. Ohne Kruemmung ist alles gedrueckt oder nichts.

### _schubfluss

```python
def _schubfluss(schub: Schubbefund, fall) -> Optional[dict]
```

Der Schubfluss je Stueck einer Wand, mit Vorzeichen entlang der Wand, in
kN/m -- und je Wand der Widerstand bei der Neigung, die der Nachweis
gewaehlt hat. Ohne Verteilung (keine Wand, keine Last) nichts.


## Konstanten

- `NEIGUNG_VON = 25` – Wie weit die Neigungskurve mindestens reicht, in Grad. Die beiden Grenzen des Benutzers liegen normalerweise darin; gehen sie darueber hinaus, waechst die Achse mit -- ein abgeschnittener Ast waere schlimmer als eine breite Achse.
- `NEIGUNG_BIS = 45`

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.nachweis.querkraft]]
- [[opencivil.nachweis.resistenzlinie]]
- [[opencivil.nachweis.schubwandnachweis]]
- [[opencivil.projekt]]
- [[opencivil.querschnitt.platte]]
- [[opencivil.querschnitt.werkstoffgesetz]]
- [[opencivil.spannungsanalyse]]

## Gebraucht von

- [[opencivil.web.api]]
- [[opencivil.web.dienst]]
