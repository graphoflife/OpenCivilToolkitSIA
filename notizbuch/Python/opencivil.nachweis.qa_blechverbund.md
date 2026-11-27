---
erzeugt: 1521cd0902a3
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/qa_blechverbund.py
> eine Blechverbunddecke nach SIA 264:2014, 5.4.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/qa_blechverbund.py)

## VERANTWORTUNG

Was eine Querschnittsanalyse mit einer Blechverbunddecke rechnet – ihr
Beton, ihr Profilblech, Betonstahl darin –, mit Herleitung; gerechnet wird
in [[opencivil.verbund.blechdecke]], die Form des Blechs kennt
[[opencivil.querschnitt.profilblech]]:

* die Kennzahlen ([[opencivil.nachweis.qa_blechverbund#KennzahlenBlechQA|KennzahlenBlechQA]]): die Festigkeiten, die Form
  des Blechs mit `d_p` und `b_0` (Figur 18), Zug- und Druckwiderstand,
  der plastische Momentenwiderstand bei Zug unten und bei Zug oben
  (5.4.3.2), der Querkraftwiderstand (26) und der Laengsschubwiderstand nach
  der m-k-Methode (28) und die Schlankheit `L/d_p` (5.4.4.3);
* je Lastfall Biegung und Normalkraft ([[opencivil.nachweis.qa_blechverbund#BlechBiegungQA|BlechBiegungQA]]): der
  plastische Zustand bei `N_Ed`, dessen Moment die Seite von `M_y,Ed`
  zieht;
* je Lastfall Querkraft und Laengsschub ([[opencivil.nachweis.qa_blechverbund#BlechSchubQA|BlechSchubQA]]): `V_z,Ed`
  gegen die Widerstaende der Kennzahlen.


## DIE DECKE TRAEGT IN EINER RICHTUNG (5.4.1.1)

entlang ihrer Rippen. Gerechnet wird einachsig um y, mit `N`, `M_y` und
`V_z` fuer die ganze gezeichnete Breite `b = n·b_s`; `M_z`, `V_y` und
`T` eines Lastfalls weist das Werkzeug nicht nach.


## WAS FEHLT – GRAU

`d_p` ueber 150 mm, wo (26) auf SIA 262 verweist; eine Angabe zum
Laengsschub; die Durchbiegung, wo `L/d_p` ueber 26 liegt. Was das Werkzeug
an der Decke gar nicht rechnet, nennt die Herleitung der Kennzahlen
([[opencivil.nachweis.qa_blechverbund#Konstanten|NICHT_GERECHNET]]).


## VORZEICHEN

N > 0 Zug; M_y > 0 zieht unten – um den Schwerpunkt der Analyse.

## Inhalt

### _stellen

```python
def _stellen(zahl: float, hoechstens: int=4) -> int
```

So viele Stellen, wie die eingegebene Zahl hat – sie wird nicht gerundet gezeigt.

### _bezug

```python
def _bezug(e: Eingaben) -> Tuple[float, float]
```

Der Schwerpunkt der Analyse in mm – der Bezugspunkt der Momente.

### KennzahlenBlechQA

```python
class KennzahlenBlechQA(Kennzahlprozedur)
```

Die Kennzahlen einer Blechverbunddecke – siehe Dateikopf.

- `THEMA = 'Blechverbunddecke'`

#### KennzahlenBlechQA.rechne

```python
def rechne(self, e: Eingaben, p: Protokoll) -> Dict[str, Groesse]
```

#### KennzahlenBlechQA._form

```python
def _form(self, p: Protokoll) -> Dict[str, Wert]
```

Die Form des Blechs als Tabelle, `d_p` und `b_0` als Formeln – siehe Dateikopf.

### _zieht

```python
def _zieht(bloecke: Sequence[Block]) -> bool
```

Ob im plastischen Zustand etwas Zug traegt – ohne Zug gibt es kein Moment.

### BlechBiegungQA

```python
class BlechBiegungQA(Nachweis)
```

Biegung und Normalkraft einer Blechverbunddecke, je Lastfall – siehe Dateikopf.

- `THEMA = 'Blechverbunddecke'`
- `LANGNAME = 'Biegung und Normalkraft'`
- `ART = 'M-N'`

#### BlechBiegungQA.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll)
```

#### BlechBiegungQA._normalkraft

```python
def _normalkraft(self, p: Protokoll, zwischen: Zwischenwerte, starr: Starrplastisch, d_grad: WertDef, fall: Lastfall, text: str) -> NachweisUrteil
```

Ohne Moment, oder wo die Normalkraft allein nicht traegt: `N_Ed` gegen `N_pl,Rd`.

### BlechSchubQA

```python
class BlechSchubQA(Nachweis)
```

Querkraft und Laengsschub einer Blechverbunddecke, je Lastfall – siehe Dateikopf.

- `THEMA = 'Blechverbunddecke'`
- `LANGNAME = 'Querkraft und Längsschub'`
- `ART = 'V'`

#### BlechSchubQA.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll)
```


## Konstanten

- `EINE_RICHTUNG = 'Eine Blechverbunddecke trägt in Richtung ihrer Rippen (5.4.1.1): nac…` – Was eine Blechverbunddecke traegt – siehe Dateikopf.
- `OHNE_TORSION = 'Torsion weist das Werkzeug bei der Blechverbunddecke nicht nach: sie…`
- `NICHT_GERECHNET = 'Nicht gerechnet: das Durchstanzen unter Einzellasten (27), die Endve…` – Was das Werkzeug an der Decke nicht rechnet.
- `OHNE_BLECH = 'Bei negativem Moment zählt das Blech nicht, auch gezogen nicht (5.4.…` – Warum bei negativem Moment das Blech fehlt – und was folgt, wo dann nichts Zug traegt.
- `OHNE_ZUG = 'Nichts trägt hier Zug: der Beton nicht, das Blech zählt bei negative…`
- `GEGENRICHTUNG = 'Bei dieser Normalkraft zeigt selbst das grösste Moment, das die Deck…`
- `DICKE = 'Das Blech ist gleich dick, seine Fläche gleichmässig über die Abwick…` – Die Dicke des Blechs ([[opencivil.querschnitt.profilblech]]).
- `TAU_BEMESSUNG = 'τ_cd bleibt ein Bemessungswert, auch wo die Tragsicherheit den Beton…` – (26) mit charakteristischen Werten.
- `KACHEL = 'in der Kachel «Längsschub»'` – Wo die Angaben zum Laengsschub stehen.
- `RIPPENBREITE = 'Rippenbreite einer Blechverbunddecke'` – Die Namen der Formeln in der Formelsammlung – in jeder Fassung derselbe.
- `SCHUBLAENGE = 'Schublänge einer Blechverbunddecke'`
- `SEITEN = (Zugseite.UNTEN, Zugseite.OBEN)` – Die Seiten, die ein Moment der Decke zieht – unten mit dem Blech, oben ohne (5.4.3.2).

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.nachweis]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.material.basis]]
- [[opencivil.nachweis.qa_stahl]]
- [[opencivil.nachweis.qa_verbund_kennzahlen]]
- [[opencivil.nachweis.qa_verbund_werte]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.biegung]]
- [[opencivil.querschnitt.gesetzwahl]]
- [[opencivil.querschnitt.plastisch]]
- [[opencivil.querschnitt.profilblech]]
- [[opencivil.querschnitt.zugseite]]
- [[opencivil.stahlbau.widerstand]]
- [[opencivil.verbund.blechdecke]]
- [[opencivil.verbund.duebel]]

## Gebraucht von

- [[opencivil.projekt.aufbau.querschnittsanalyse]]
- [[opencivil.web.api]]

## Formeln aus diesem Modul

- [[Erfüllungsgrad bei fester Normalkraft – einachsig um y]] · `BlechBiegungQA.pruefe`
- [[Kennwerte eines Profilblechs]] · `KennzahlenBlechQA._form`
- [[Längsschubwiderstand nach der m-k-Methode]] · `KennzahlenBlechQA._laengsschub`
- [[Probe – Moment um y]] · `KennzahlenBlechQA._biegung`
- [[Querkraftwiderstand einer Blechverbunddecke]] · `KennzahlenBlechQA._querkraft`
- [[Rippenbreite einer Blechverbunddecke]] · `KennzahlenBlechQA._form`
- [[Schlankheit einer Blechverbunddecke]] · `KennzahlenBlechQA._schlankheit`
- [[Schublänge einer Blechverbunddecke]] · `KennzahlenBlechQA._laengsschub`
- [[Statische Höhe einer Blechverbunddecke]] · `KennzahlenBlechQA._form`
