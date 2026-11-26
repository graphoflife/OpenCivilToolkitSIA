---
erzeugt: 81f97f695cee
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/qa_stahl.py
> die Lastfaelle eines Stahlquerschnitts nach SIA 263:2013.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/qa_stahl.py)

## VERANTWORTUNG

Zwei Nachweise je Lastfall, mit ihrer Herleitung -- gerechnet wird in
[[opencivil.stahlbau.widerstand]]:

* **Biegung und Normalkraft** ([[opencivil.nachweis.qa_stahl#StahlBiegungQA|StahlBiegungQA]]): die Klasse im
  Lastfall, dann plastisch in den Klassen 1 und 2, nach (54) in Klasse 3 und
  am wirksamen Querschnitt nach (60) in Klasse 4 -- mit dem, was eine grosse
  Querkraft den Blechen nimmt.
* **Querkraft** ([[opencivil.nachweis.qa_stahl#StahlQuerkraftQA|StahlQuerkraftQA]]): je Richtung `V_Ed ≤ V_Rd`, in
  einem Querschnitt aus Rundrohren die Resultierende. `V_Rd` lesen beide
  aus den Kennzahlen ([[opencivil.nachweis.qa_stahl_kennzahlen]]).

Was in der Herleitung steht, ist im plastischen Fall die **Probe**, wie beim
Stahlbeton ([[opencivil.nachweis.schiefe_biegung]]): die Nulllinie, die
Kraft jedes Teils mit ihrem Angriffspunkt und die Summen `N`, `M_y` und
`M_z` -- sie gehen von Hand. In den Klassen 3 und 4 die lineare
Gleichung mit ihren Zahlen.


## WAS FEHLT -- GRAU

* Torsion: SIA 263 regelt in 5.1 bis 5.3 keinen Torsionswiderstand des
  Querschnitts. Ein `T_Ed` steht in der Einwirkung, nachgewiesen wird es
  nicht (nach Vorgabe, nicht nachgeschlagen).
* Querkraft ohne Profil: frei gezeichnete Flaechen tragen keine.
* Ein Rundrohr der Klasse 4: SIA 263 nennt dafuer keine mitwirkende Breite.
* Knicken und Kippen gehoeren dem Stab.


## VORZEICHEN

N > 0 Zug; M_y > 0 zieht unten, M_z > 0 links -- um den Schwerpunkt der
Analyse.

## Inhalt

### _bezuege

```python
def _bezuege(analyse: Querschnittsanalyse, stahl: Stahlquerschnitt, kennzahlen: KennzahlenStahlQA) -> List[Eingabebezug]
```

Schwerpunkt, Kennwerte der Staehle und die Querkraftwiderstaende der Kennzahlen.

### querkraefte

```python
def querkraefte(e: Eingaben, stahl: Stahlquerschnitt, kennzahlen: KennzahlenStahlQA, analyse: Querschnittsanalyse, fall: Lastfall) -> List[wd.Querkraft]
```

Die Querkraefte des Lastfalls mit ihren Widerstaenden, in N -- wie sie
zaehlen. `kennzahlen` traegt `V_Rd` je Richtung -- auch die des
Verbunds ([[opencivil.nachweis.qa_verbund_kennzahlen]]).

### einwirkung

```python
def einwirkung(p: Protokoll, analyse: Querschnittsanalyse, fall: Lastfall, *, torsion: str=OHNE_TORSION) -> None
```

Die Einwirkung als Tabelle -- je Groesse, die zaehlt, eine Zeile;
einachsig ohne M_z und V_y. Mit `T_Ed` der Satz `torsion`, warum es
nicht nachgewiesen wird.

### StahlBiegungQA

```python
class StahlBiegungQA(Nachweis)
```

Biegung und Normalkraft eines Stahlquerschnitts, je Lastfall -- siehe Dateikopf.

- `THEMA = 'Stahlquerschnitt'`
- `LANGNAME = 'Biegung und Normalkraft'`
- `ART = 'M-N'`

#### StahlBiegungQA.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll)
```

#### StahlBiegungQA._rechnen

```python
def _rechnen(self, e: Eingaben, sw: Stahlwerte, bezug: Tuple[float, float], fall: Lastfall) -> Optional[wd.Fall]
```

Der Lastfall am Querschnitt -- `None` ohne Normalkraft und Moment.

#### StahlBiegungQA._wirksam

```python
def _wirksam(self, p: Protokoll, werte: Zwischenwerte, sw: Stahlwerte, x: wd.Fall, bezug: Tuple[float, float]) -> None
```

Der wirksame Querschnitt der Klasse 4: bei Druck und zu jeder Seite, die zaehlt.

#### StahlBiegungQA._seiten

```python
def _seiten(self, x: wd.Fall) -> List[Zugseite]
```

Die Seiten, die die Momente bei `λ` ziehen -- ihr `W_eff` zaehlt in (60).

#### StahlBiegungQA._linear

```python
def _linear(self, p: Protokoll, werte: Zwischenwerte, x: wd.Fall, N_Ed: Wert, M_Ed: Wert, d_grad: WertDef, fall: Lastfall) -> NachweisUrteil
```

(54) in Klasse 3, (60) in Klasse 4 -- als Widerstaende geschrieben, mit `λ`.

### minderung

```python
def minderung(p: Protokoll, werte: Zwischenwerte, kraefte: Sequence[wd.Querkraft], abgemindert: wd.Abgemindert, stahl: Stahlquerschnitt, *, referenz: str) -> None
```

Was grosse Querkraft den Blechen nimmt, in denen sie steht -- im Stahl wie im Verbund.

### krafttabelle

```python
def krafttabelle(p: Protokoll, werte: Zwischenwerte, bloecke: Sequence[Block], namen: Sequence[str], linien: Sequence[Tuple[str, Linie]], *, titel: str) -> None
```

Die Nulllinie und je Teil und Zone die Kraft mit Angriffspunkt, dazu
ihre Summe `N` -- der Anfang der Probe eines plastischen Zustands, im
Stahl wie im Verbund. `namen` je Teil, auf den ein Block zeigt;
`linien` je Nulllinie, wo sie liegt -- im Verbund mit
Teilverduebelung zwei, mit derselben Zugrichtung.

### momentsummen

```python
def momentsummen(bloecke: Sequence[Block], bezug: Tuple[float, float]) -> Dict[str, float]
```

Je Achse das Moment der Bloecke um `bezug`, in Nm: `M_y = -Σ F (z - z_S)`.

### probe

```python
def probe(p: Protokoll, werte: Zwischenwerte, bloecke: Sequence[Block], namen: Sequence[str], bezug: Tuple[float, float], biegung: Biegung, pl: Plastisch, *, titel: str, referenz: str, symbol: str='M_{Rd}') -> Wert
```

Die Probe eines plastischen Zustands -- im Stahl wie im Verbund: die
Nulllinie, je Teil und Zone die Kraft mit Angriffspunkt, die Summen
`N`, `M_y` und `M_z`. Zurueck kommt der Widerstand `symbol` in
der Richtung der Einwirkung, einachsig `M_y`.

### glied_text

```python
def glied_text(g: wd.Glied, faktor: float, mit_lambda: bool) -> str
```

Ein Glied von (54) oder (60) -- und von (62) und (63) im Stab
([[opencivil.nachweis.qa_stahl_stabilitaet]]) -- als Bruch mit Zahlen:
ohne den Anteil mit `λ`, wo `mit_lambda` falsch ist; leer, wo nichts
bleibt.

### StahlQuerkraftQA

```python
class StahlQuerkraftQA(Nachweis)
```

Die Querkraft eines Stahlquerschnitts, je Lastfall -- siehe Dateikopf.

- `THEMA = 'Stahlquerschnitt'`
- `LANGNAME = 'Querkraft'`
- `ART = 'V'`
- `REFERENZ = schub.REFERENZ_SCHUB`

#### StahlQuerkraftQA.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll)
```


## Konstanten

- `JENSEITS = 'Die Normalkraft liegt jenseits dessen, was der Querschnitt ganz gezo…` – Warum es mit diesem N keinen plastischen Zustand gibt.
- `OHNE_TORSION = 'Torsion weist das Werkzeug beim Stahlquerschnitt nicht nach: SIA 263…` – Warum Torsion nicht nachgewiesen wird -- siehe Dateikopf.
- `OHNE_PROFIL = 'Querkraft tragen nur Profile – der Querschnitt hat keines.'` – Warum ohne Profil keine Querkraft getragen wird.
- `LINEAR = 'Lineares Zusammenwirken im Stahlquerschnitt'` – Der Name von (54) und (60) in der Formelsammlung: als Ansatz dieselbe Gleichung.
- `MOMENT_UM = {'y': '-\\sum F_i \\cdot (z_i - z_S)', 'z': '-\\sum F_i \\cdot (y_i -…` – Wie die Probe das Moment um eine Achse schreibt.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.nachweis]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.nachweis.qa_stahl_kennzahlen]]
- [[opencivil.nachweis.qa_stahl_werte]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.biegung]]
- [[opencivil.querschnitt.plastisch]]
- [[opencivil.querschnitt.zugseite]]
- [[opencivil.stahlbau.querschnitt]]
- [[opencivil.stahlbau.schub]]
- [[opencivil.stahlbau.widerstand]]

## Gebraucht von

- [[opencivil.nachweis.qa_stahl_stabilitaet]]
- [[opencivil.nachweis.qa_verbund]]
- [[opencivil.nachweis.qa_verbund_kennzahlen]]
- [[opencivil.projekt.aufbau.querschnittsanalyse]]

## Formeln aus diesem Modul

- [[Biegewiderstand bis zum ersten Fliessen]] · `StahlBiegungQA._wirksam`
- [[Erfüllungsgrad bei fester Normalkraft und fester Richtung]] · `StahlBiegungQA._ansatz`
- [[Lineares Zusammenwirken im Stahlquerschnitt]] · `StahlBiegungQA._ansatz`
- [[Minderung durch grosse Querkraft]] · `minderung`
- [[Probe – Moment um y]] · `probe`
- [[Probe – Moment um z]] · `probe`
- [[Probe – Normalkraft]] · `krafttabelle`
- [[Widerstand in der Richtung der Einwirkung]] · `StahlBiegungQA._linear`
- [[Widerstand in der Richtung der Einwirkung]] · `probe`
- [[Widerstandsmoment bis zur weitesten Faser]] · `StahlBiegungQA._wirksam`
