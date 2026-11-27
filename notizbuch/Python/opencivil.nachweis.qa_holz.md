---
erzeugt: 53e2e4b767d4
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/qa_holz.py
> die Lastfaelle eines Holzquerschnitts nach SIA 265:2012.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/qa_holz.py)

## VERANTWORTUNG

Zwei Nachweise je Lastfall, mit ihrer Herleitung – gerechnet wird in
[[opencivil.holzbau.gleichungen]]:

* **Biegung und Normalkraft** ([[opencivil.nachweis.qa_holz#HolzBiegungQA|HolzBiegungQA]]): (6) oder (10) mit
  Normalkraft allein, (14) mit Biegung allein, (21) mit Zug und Biegung,
  (22) mit Druck und Biegung (4.2.1 bis 4.2.4).
* **Schub und Torsion** ([[opencivil.nachweis.qa_holz#HolzSchubQA|HolzSchubQA]]): (23) mit Querkraft allein,
  (24) mit Torsion allein, (25) mit beiden (4.2.5).

Linear, am Bruttoquerschnitt (4.1.2), mit den Werten aus
[[opencivil.nachweis.qa_holz_werte#HolzwerteQA|HolzwerteQA]]: die Biegespannung an
der weitesten Faser, die Schubspannung nach Jourawski, die Torsion am
Rechteck. Die Bemessungswerte der Tabellen 6 und 7 gelten mit
`η = η_w·η_t`: η_w der Feuchteklasse der Analyse, η_t = 1.4 in einem
Lastfall, der stossartig ist (2.2.6), sonst 1.


## DER ERFUELLUNGSGRAD

Wie beim Stahl – die Normalkraft bleibt, die Momente wachsen um `λ`, bis
die Gleichung aufgeht: `α = λ`. Ohne Moment, oder wo schon die
Normalkraft allein nicht traegt, steht die Normalkraft gegen ihren
Widerstand. In (25) wachsen Querkraft und Torsion zusammen.


## QUERKRAFT IN BEIDEN RICHTUNGEN

`τ_d = √(τ_y² + τ_z²)` – die beiden groessten Schubspannungen, als laegen
sie an derselben Stelle: auf der sicheren Seite (nach Vorgabe, nicht
nachgeschlagen).


## WAS FEHLT – GRAU

Torsion an einem Querschnitt, der kein Rechteck ist
([[opencivil.nachweis.qa_holz_werte#Konstanten|TORSION_NUR_RECHTECK]]).


## VORZEICHEN

N > 0 Zug; M_y > 0 zieht unten, M_z > 0 links. Die Gleichungen nehmen
Betraege.

## Inhalt

### bezuege

```python
def bezuege(analyse: Querschnittsanalyse, werte: HolzwerteQA) -> List[Eingabebezug]
```

`A`, die Werte des Holzquerschnitts und die Kennwerte des Holzes.

### einwirkung

```python
def einwirkung(p: Protokoll, analyse: Querschnittsanalyse, fall: Lastfall, groessen: Sequence[str]) -> None
```

Die Einwirkung als Tabelle – je Groesse, die zaehlt, eine Zeile; einachsig ohne M_z, V_y.

### ansaetze

```python
def ansaetze(p: Protokoll, gleichungen: AbstractSet[str]) -> None
```

Die Gleichungen, die die Faelle brauchen, ohne Zahlen – in der Folge der Norm.

### bemessungswerte

```python
def bemessungswerte(p: Protokoll) -> None
```

Wie die Bemessungswerte der Tabellen in die Gleichungen kommen.

### _bruch

```python
def _bruch(oben: str, *unten: float) -> str
```

`\frac{oben}{η · … · f}` mit Zahlen: η mit zwei Stellen, die Festigkeit einer.

### _Fall

```python
@dataclass
class _Fall
```

Ein Lastfall am Querschnitt, in N/mm² – was Gleichung und Herleitung teilen.

- `N: float` – In N, positiv Zug.
- `M: Dict[str, float]` – Je Achse das Moment in Nm, das zaehlt – auch null.
- `eta: float`
- `sigma_N: float` – Positiv Zug.
- `sigma_m: Dict[str, float] = field(default_factory=dict)` – Je Achse der Betrag an der weitesten Faser.
- `f_m: Dict[str, float] = field(default_factory=dict)` – Je Achse `k_h·f_m,d` – ohne η.
- `biegung: Optional[gl.Biegung] = None`

### HolzBiegungQA

```python
class HolzBiegungQA(Nachweis)
```

Biegung und Normalkraft eines Holzquerschnitts, je Lastfall – siehe Dateikopf.

- `THEMA = 'Holzquerschnitt'`
- `LANGNAME = 'Biegung und Normalkraft'`
- `ART = 'M-N'`

#### HolzBiegungQA.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll)
```

#### HolzBiegungQA._rechnen

```python
def _rechnen(self, e: Eingaben, fall: Lastfall) -> _Fall
```

Spannungen und Gleichung eines Lastfalls – ohne Herleitung.

#### HolzBiegungQA._normalspannung

```python
def _normalspannung(self, p: Protokoll, e: Eingaben, werte: Zwischenwerte, x: _Fall, zug: bool) -> str
```

σ = \|N\|/A in die Herleitung – und ihr Glied mit Zahlen, in (22) im Quadrat.

#### HolzBiegungQA._biegespannung

```python
def _biegespannung(self, p: Protokoll, e: Eingaben, werte: Zwischenwerte, x: _Fall, a: str) -> str
```

σ_m = \|M\|/W um `a` in die Herleitung – und ihr Glied, mit Zahlen.

#### HolzBiegungQA._normalkraftwiderstand

```python
def _normalkraftwiderstand(self, p: Protokoll, e: Eingaben, werte: Zwischenwerte, eta: Wert, zug: bool) -> Wert
```

`η f A` – mit dem Zeichen der Normalkraft, wie die Kennzahlen.

### HolzSchubQA

```python
class HolzSchubQA(Nachweis)
```

Schub aus Querkraft und Torsion eines Holzquerschnitts, je Lastfall – siehe Dateikopf.

- `THEMA = 'Holzquerschnitt'`
- `LANGNAME = 'Schub und Torsion'`
- `ART = 'V+T'`

#### HolzSchubQA._schub

```python
def _schub(self, fall: Lastfall) -> Dict[str, float]
```

Je Richtung die Querkraft in N, die zaehlt – einachsig nur z.

#### HolzSchubQA.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll)
```

#### HolzSchubQA._querkraft

```python
def _querkraft(self, p: Protokoll, e: Eingaben, werte: Zwischenwerte, V: Dict[str, float]) -> Optional[Wert]
```

τ je Richtung, mit beiden ihre Resultierende – `None` ohne Querkraft.


## Konstanten

- `REFERENZ_BIEGUNG = 'SIA 265:2012, 4.2.1–4.2.4'`
- `REFERENZ_SCHUB = 'SIA 265:2012, 4.2.5'`
- `ERFUELLUNGSGRAD = '\\alpha_{eff} = \\frac{M_{Rd}}{M_{Ed}} \\qquad M = \\sqrt{M_y^2 + M_…` – Der Erfuellungsgrad – derselbe Ansatz wie beim Stahl, eine Seite in der Formelsammlung.
- `_MOMENTE = '\\frac{\\sigma_{m,y,d}}{f_{m,y,d}} + \\frac{\\sigma_{m,z,d}}{f_{m,z,…` – Die Gleichungen ohne Zahlen, je mit ihrem Titel und ihrem Namen in der Formelsammlung – f_d steht fuer η·f_d der Tabelle.
- `ANSAETZE = {'(6)': ('\\sigma_{t,0,d} \\le f_{t,0,d}', 'Zug allein', 'Zug im Holz…`
- `_EINWIRKUNG = {'N': ('N_Ed', 'kN'), 'M_y': ('M_y,Ed', 'kNm'), 'M_z': ('M_z,Ed', 'kN…` – Die Zeilen der Einwirkung: je Groesse des Lastfalls ihr Name und ihre Einheit.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.latex]]
- [[opencivil.core.nachweis]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.holzbau.gleichungen]]
- [[opencivil.material.holz]]
- [[opencivil.nachweis.qa_holz_werte]]
- [[opencivil.querschnitt.analyse]]

## Gebraucht von

- [[opencivil.nachweis.qa_holz_stabilitaet]]
- [[opencivil.projekt.aufbau.querschnittsanalyse]]

## Formeln aus diesem Modul

- [[Bemessungswerte des Holzes]] · `bemessungswerte`
- [[Biegespannung im Holz]] · `HolzBiegungQA._biegespannung`
- [[Biegung im Holz]] · `ansaetze`
- [[Biegung und Druck im Holz]] · `ansaetze`
- [[Biegung und Zug im Holz]] · `ansaetze`
- [[Druck im Holz, ohne Knicken]] · `ansaetze`
- [[Druckwiderstand eines Holzquerschnitts]] · `HolzBiegungQA._normalkraftwiderstand`
- [[Erfüllungsgrad bei fester Normalkraft und fester Richtung]] · `HolzBiegungQA.pruefe`
- [[Kippen eines Holzträgers]] · `ansaetze`
- [[Knicken eines Holzstabs unter Druck]] · `ansaetze`
- [[Knicken und Biegung eines Holzstabs]] · `ansaetze`
- [[Normalspannung im Holz]] · `HolzBiegungQA._normalspannung`
- [[Schub aus Querkraft im Holz]] · `ansaetze`
- [[Schub aus Querkraft und Torsion im Holz]] · `ansaetze`
- [[Schub aus Torsion im Holz]] · `ansaetze`
- [[Schubfestigkeit des Holzes im Lastfall]] · `HolzSchubQA._ein_fall`
- [[Schubspannung aus Querkraft im Holz]] · `HolzSchubQA._querkraft`
- [[Schubspannung aus Torsion im Holz]] · `HolzSchubQA._torsion`
- [[Schubspannung aus zwei Querkräften]] · `HolzSchubQA._querkraft`
- [[Schubwiderstand neben Torsion im Holz]] · `HolzSchubQA._ein_fall`
- [[Widerstand in der Richtung der Einwirkung]] · `HolzBiegungQA._ein_fall`
- [[Zug im Holz]] · `ansaetze`
- [[Zugwiderstand eines Holzquerschnitts]] · `HolzBiegungQA._normalkraftwiderstand`
