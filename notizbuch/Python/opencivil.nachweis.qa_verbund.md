---
erzeugt: 1327150ab7ad
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/qa_verbund.py
> die Lastfaelle eines Verbundquerschnitts nach SIA 264:2014.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/qa_verbund.py)

## VERANTWORTUNG

Die Nachweise je Lastfall, mit ihrer Herleitung – gerechnet wird in
[[opencivil.verbund.widerstand]] und [[opencivil.verbund.duebel]]:

* **Biegung und Normalkraft** ([[opencivil.nachweis.qa_verbund#VerbundBiegungQA|VerbundBiegungQA]]): der plastische
  Zustand bei `N_Ed` in der Richtung des Moments, mit dem, was grosse
  Querkraft den Blechen nimmt. Er gilt, wo jedes Blech in Klasse 1 oder 2
  liegt und gezogener Betonstahl in der Duktilitaetsklasse B oder C ist
  (5.1.2.3); mit `β` fuer S420 und S460 (5.1.2.2). Tragen die
  Kopfbolzenduebel weniger, als der gedrueckte Beton bei voller
  Verduebelung braucht, mit Teilverduebelung (6.1.1.6). Die Herleitung
  zeigt die Probe wie im Stahl ([[opencivil.nachweis.qa_stahl#probe|probe]]).
* **Verduebelung**, im selben Nachweis, wo Kopfbolzenduebel gewaehlt sind:
  der Verduebelungsgrad `η = N/N_f` gegen (29) – gegen eins im Bereich
  negativer Momente ([[opencivil.verbund.duebel#negativ|negativ]]) oder wo das
  Profil nicht doppelsymmetrisch ist. `P_Rd` steht in den Kennzahlen.
* **Querkraft** ([[opencivil.nachweis.qa_verbund#VerbundQuerkraftQA|VerbundQuerkraftQA]]): wie im Stahl, denn der Stahl
  traegt sie allein (4.3.2.2). `V_Rd` lesen beide aus den Kennzahlen
  ([[opencivil.nachweis.qa_verbund_kennzahlen]]).


## WAS FEHLT – GRAU

* Wo plastisch nicht gerechnet werden darf
  ([[opencivil.verbund.widerstand#Fall|grund]]): elastisch nach 5.1.2.4
  und 5.1.2.5 rechnet das Werkzeug noch nicht. Die Verduebelung folgt dem
  plastischen Zustand: wo er nicht gilt, steht sie nicht da.
* Einem Lastfall die Zahl seiner Duebel – Biegung und Normalkraft rechnen
  dann mit voller Verduebelung –, oder `L_e`, wo (29) es braucht.
* Torsion: ein `T_Ed` steht in der Einwirkung, nachgewiesen wird es nicht
  (nach Vorgabe, nicht nachgeschlagen).
* Knicken und Kippen gehoeren dem Traeger, ebenso der Laengsschub in der
  Platte (5.1.4) und die Regeln der Durchbildung (7.1).


## VORZEICHEN

N > 0 Zug; M_y > 0 zieht unten, M_z > 0 links – um den Schwerpunkt der
Analyse.

## Inhalt

### _bezuege

```python
def _bezuege(analyse: Querschnittsanalyse, kennzahlen: KennzahlenVerbundQA) -> List[Eingabebezug]
```

Schwerpunkt, Kennwerte der Materialien und was die Kennzahlen fuer die Faelle haben.

### VerbundBiegungQA

```python
class VerbundBiegungQA(Nachweis)
```

Biegung und Normalkraft eines Verbundquerschnitts, je Lastfall – siehe Dateikopf.

- `THEMA = 'Verbundquerschnitt'`
- `LANGNAME = 'Biegung und Normalkraft'`
- `ART = 'M-N'`

#### VerbundBiegungQA.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll)
```

#### VerbundBiegungQA._rechnen

```python
def _rechnen(self, e: Eingaben, werte: Verbundwerte, bezug: Tuple[float, float], fall: Lastfall) -> Optional[vw.Fall]
```

Der Lastfall am Querschnitt – `None` ohne Normalkraft und Moment.

#### VerbundBiegungQA._normalkraft

```python
def _normalkraft(self, p: Protokoll, zwischen: Zwischenwerte, x: vw.Fall, N_Ed: Wert, d_grad: WertDef, fall: Lastfall, text: str) -> NachweisUrteil
```

Ohne Moment, oder wo die Normalkraft allein nicht traegt: `N_Ed` gegen `N_pl,Rd`.

#### VerbundBiegungQA._verduebelung

```python
def _verduebelung(self, p: Protokoll, e: Eingaben, werte: Verbundwerte, zwischen: Zwischenwerte, x: vw.Fall, bezug: Tuple[float, float], fall: Lastfall, teile: Tuple[Starrplastisch, Starrplastisch]) -> Tuple[NachweisUrteil, Optional[Wert]]
```

`η` gegen (29) oder eins – und mit Teilverduebelung ihr
Momentenwiderstand (siehe Dateikopf). `teile`: Beton und Stahl je
auf ihrer Seite der Fuge.

#### VerbundBiegungQA._verlangt

```python
def _verlangt(self, p: Protokoll, werte: Verbundwerte, zwischen: Zwischenwerte, x: vw.Fall, abschnitt: vd.Abschnitt) -> Optional[Wert]
```

Der kleinste Verduebelungsgrad: nach (29) oder eins – `None`, wo `L_e` fehlt.

#### VerbundBiegungQA._teilverduebelt

```python
def _teilverduebelt(self, p: Protokoll, x: vw.Fall, bezug: Tuple[float, float], fall: Lastfall, N: Wert, P_Rd: Wert, teile: Tuple[Starrplastisch, Starrplastisch]) -> Wert
```

Der Momentenwiderstand mit Teilverduebelung, mit seiner Probe.

### VerbundQuerkraftQA

```python
class VerbundQuerkraftQA(StahlQuerkraftQA)
```

Die Querkraft eines Verbundquerschnitts, je Lastfall: wie im Stahl – siehe Dateikopf.

- `THEMA = 'Verbundquerschnitt'`
- `REFERENZ = vw.REFERENZ_SCHUB`


## Konstanten

- `OHNE_TORSION = 'Torsion weist das Werkzeug beim Verbundquerschnitt nicht nach (nach …` – Warum Torsion nicht nachgewiesen wird – siehe Dateikopf.
- `VOLL_ANGENOMMEN = 'Verdübelung voll angenommen, wie 5.1.2.1 es tut: Stahl und Beton tra…` – Wie die Verduebelung in die Lastfaelle eingeht – ohne Duebel und mit.
- `MIT_DUEBELN = 'Bis zum Momentennullpunkt tragen die N Dübel eines Lastfalls N · P_R…`
- `OHNE_ANZAHL = 'Für diesen Lastfall fehlt noch die Zahl der Dübel bis zum Momentennu…` – Was einem Lastfall fuer die Verduebelung fehlen kann – grau.
- `OHNE_L_E = 'Für (29) fehlt diesem Lastfall noch L_e, der Abstand der Momentennul…`
- `OHNE_MOMENT = 'Ohne Moment prüft das Werkzeug die Dübel nicht: (29) gilt dem Längss…`
- `NEGATIV = 'Im Bereich negativer Momente lässt 6.1.1.6 keine Teilverdübelung zu:…` – Warum volle Verduebelung verlangt ist, wo (29) nicht gilt.
- `KAMMER = 'Kammerbeton zählt zum Stahl: er ist mit dem Steg verbunden (5.2.1.2)…`
- `UNSYMMETRISCH = '(29) gilt für doppelsymmetrische Stahlprofile; für diesen Baustahl n…`
- `REFERENZ_TEIL = 'SIA 264:2014, 6.1.1.6; 5.1.2.1'`

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.nachweis]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.nachweis.qa_stahl]]
- [[opencivil.nachweis.qa_verbund_kennzahlen]]
- [[opencivil.nachweis.qa_verbund_werte]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.plastisch]]
- [[opencivil.stahlbau.widerstand]]
- [[opencivil.verbund.duebel]]
- [[opencivil.verbund.widerstand]]

## Gebraucht von

- [[opencivil.projekt.aufbau.querschnittsanalyse]]

## Formeln aus diesem Modul

- [[Dübel für volle Verdübelung]] · `VerbundBiegungQA._verduebelung`
- [[Erfüllungsgrad bei fester Normalkraft und fester Richtung]] · `VerbundBiegungQA._ansatz`
- [[Kleinster Verdübelungsgrad]] · `VerbundBiegungQA._verlangt`
- [[Kraft im Beton bei voller Verdübelung]] · `VerbundBiegungQA._verduebelung`
- [[Plastischer Biegewiderstand mit β]] · `VerbundBiegungQA._plastisch`
- [[Verdübelungsgrad]] · `VerbundBiegungQA._verduebelung`
- [[Was die Dübel tragen]] · `VerbundBiegungQA._teilverduebelt`
