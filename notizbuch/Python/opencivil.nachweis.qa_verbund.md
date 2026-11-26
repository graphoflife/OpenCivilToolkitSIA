---
erzeugt: ed461001683e
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/qa_verbund.py
> die Lastfaelle eines Verbundquerschnitts nach SIA 264:2014.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/qa_verbund.py)

## VERANTWORTUNG

Zwei Nachweise je Lastfall, mit ihrer Herleitung -- gerechnet wird in
[[opencivil.verbund.widerstand]]:

* **Biegung und Normalkraft** ([[opencivil.nachweis.qa_verbund#VerbundBiegungQA|VerbundBiegungQA]]): der plastische
  Zustand bei `N_Ed` in der Richtung des Moments, mit dem, was grosse
  Querkraft den Blechen nimmt. Er gilt, wo jedes Blech in Klasse 1 oder 2
  liegt und gezogener Betonstahl in der Duktilitaetsklasse B oder C ist
  (5.1.2.3); mit `β` fuer S420 und S460 (5.1.2.2). Die Herleitung zeigt
  die Probe wie im Stahl ([[opencivil.nachweis.qa_stahl#probe|probe]]).
* **Querkraft** ([[opencivil.nachweis.qa_verbund#VerbundQuerkraftQA|VerbundQuerkraftQA]]): wie im Stahl, denn der Stahl
  traegt sie allein (4.3.2.2). `V_Rd` lesen beide aus den Kennzahlen
  ([[opencivil.nachweis.qa_verbund_kennzahlen]]).


## WAS FEHLT -- GRAU

* Wo plastisch nicht gerechnet werden darf
  ([[opencivil.verbund.widerstand#Fall|grund]]): elastisch nach 5.1.2.4
  und 5.1.2.5 rechnet das Werkzeug noch nicht.
* Torsion: ein `T_Ed` steht in der Einwirkung, nachgewiesen wird es nicht
  (nach Vorgabe, nicht nachgeschlagen).
* Die Verduebelung, Knicken und Kippen gehoeren dem Traeger.


## VORZEICHEN

N > 0 Zug; M_y > 0 zieht unten, M_z > 0 links -- um den Schwerpunkt der
Analyse.

## Inhalt

### _bezuege

```python
def _bezuege(analyse: Querschnittsanalyse, kennzahlen: KennzahlenVerbundQA) -> List[Eingabebezug]
```

Schwerpunkt, Kennwerte der Materialien und die Querkraftwiderstaende der Kennzahlen.

### VerbundBiegungQA

```python
class VerbundBiegungQA(Nachweis)
```

Biegung und Normalkraft eines Verbundquerschnitts, je Lastfall -- siehe Dateikopf.

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

Der Lastfall am Querschnitt -- `None` ohne Normalkraft und Moment.

#### VerbundBiegungQA._normalkraft

```python
def _normalkraft(self, p: Protokoll, zwischen: Zwischenwerte, x: vw.Fall, N_Ed: Wert, d_grad: WertDef, fall: Lastfall, text: str) -> NachweisUrteil
```

Ohne Moment, oder wo die Normalkraft allein nicht traegt: `N_Ed` gegen `N_pl,Rd`.

### VerbundQuerkraftQA

```python
class VerbundQuerkraftQA(StahlQuerkraftQA)
```

Die Querkraft eines Verbundquerschnitts, je Lastfall: wie im Stahl -- siehe Dateikopf.

- `THEMA = 'Verbundquerschnitt'`
- `REFERENZ = vw.REFERENZ_SCHUB`


## Konstanten

- `OHNE_TORSION = 'Torsion weist das Werkzeug beim Verbundquerschnitt nicht nach (nach …` – Warum Torsion nicht nachgewiesen wird -- siehe Dateikopf.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.latex]]
- [[opencivil.core.nachweis]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.nachweis.qa_stahl]]
- [[opencivil.nachweis.qa_verbund_kennzahlen]]
- [[opencivil.nachweis.qa_verbund_werte]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.stahlbau.widerstand]]
- [[opencivil.verbund.widerstand]]

## Gebraucht von

- [[opencivil.projekt.aufbau.querschnittsanalyse]]

## Formeln aus diesem Modul

- [[Erfüllungsgrad bei fester Normalkraft und fester Richtung]] · `VerbundBiegungQA._ansatz`
- [[Plastischer Biegewiderstand mit β]] · `VerbundBiegungQA._plastisch`
