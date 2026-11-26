---
erzeugt: dabb87284717
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/qa_holz_stabilitaet.py
> Knicken und Kippen eines Holzstabs nach SIA 265:2012.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/qa_holz_stabilitaet.py)

## VERANTWORTUNG

Je Stabilitaetsfall der Querschnittsanalyse ein Nachweis mit seiner
Herleitung, je Hauptachse fuer sich (4.2.8.5) -- gerechnet wird in
[[opencivil.holzbau.gleichungen]]:

* Knicken um eine Achse, wo der Stab gedrueckt ist und um sie eine
  Knicklaenge hat: die Schlankheit `λ = L_K/i`, die relative nach (34) mit
  `f_c,0,k` und `E_0,05` aus Anhang B, `k_c` nach (30) und (31);
* Kippen um die starke Achse, wo ein Moment um sie wirkt und die Kipplaenge
  `L_D` nicht null ist: `σ_m,crit` nach (41), `λ_rel,m` nach (40),
  `k_m` nach (39);
* je Achse (29) mit Druck allein, (37) mit Druck und Biegung, (38) mit
  Biegung allein.

Der Erfuellungsgrad wie in der Tragsicherheit
([[opencivil.nachweis.qa_holz]]): die Normalkraft bleibt, die Momente
wachsen um `λ`; massgebend ist die Achse mit dem kleineren. Ohne Moment
steht die Druckkraft gegen den Knickwiderstand.


## NACH VORGABE, NICHT NACHGESCHLAGEN

* `λ_rel` und `σ_m,crit` mit den Werten aus Anhang B, ohne η_w: die
  Feuchteklasse mindert die Steifigkeit dort nicht.
* `k_h` gilt beim Brettschichtholz auch in (37) und (38), wie im
  Querschnitt.
* ψ zaehlt nicht: (37) und (38) nehmen das groesste Moment im Stab, wie es
  eingegeben ist.


## WAS GRAU STEHT

Kippen eines Querschnitts, der kein Rechteck ist: (41) gilt fuer das
Rechteck `b × h` ([[opencivil.nachweis.qa_holz_stabilitaet#Konstanten|KIPPEN_NUR_RECHTECK]]).


## VORZEICHEN

N \< 0 Druck; M_y > 0 zieht unten, M_z > 0 links. Die Gleichungen nehmen
Betraege.

## Inhalt

### HolzStabilitaetQA

```python
class HolzStabilitaetQA(Nachweis)
```

Knicken und Kippen eines Holzstabs, je Fall -- siehe Dateikopf.

- `THEMA = 'Knicken und Kippen eines Holzstabs'`
- `LANGNAME = 'Knicken und Kippen'`
- `ART = 'Stab'`

#### HolzStabilitaetQA.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll)
```

#### HolzStabilitaetQA._gleichungen

```python
def _gleichungen(self, e: Eingaben) -> set
```

Welche Gleichungen die Faelle brauchen -- fuer die Ansaetze vorweg.

#### HolzStabilitaetQA._kippachse

```python
def _kippachse(self, e: Eingaben) -> str
```

Um welche Achse der Stab kippen kann: die starke.

#### HolzStabilitaetQA._momente

```python
def _momente(self, fall: Stabfall) -> Dict[str, float]
```

Je Achse das Moment in Nm, das zaehlt -- einachsig ohne M_z.

#### HolzStabilitaetQA._urteil

```python
def _urteil(self, p: Protokoll, werte: Zwischenwerte, r: '_Herleitung', d_grad: WertDef, fall: Stabfall, massgebend: Tuple[str, gl.Stabachse]) -> NachweisUrteil
```

Der Vergleich der massgebenden Achse: die Momente gegen ihren Widerstand, ohne Druck.

### _einwirkung

```python
def _einwirkung(p: Protokoll, biegung: Biegung, fall: Stabfall) -> None
```

Die Einwirkung und der Stab als Tabelle -- einachsig ohne M_z.

### _Herleitung

```python
class _Herleitung
```

Die Herleitung eines Falls, Achse fuer Achse -- mit den Werten, die die Achsen teilen.

#### _Herleitung.kennwert

```python
def kennwert(self, kurz: str) -> Wert
```

#### _Herleitung.zahl

```python
def zahl(self, kurz: str) -> float
```

Ein Kennwert des Holzes in N/mm².

#### _Herleitung.achse

```python
def achse(self, a: str, knickt: bool, kippt: bool) -> Tuple[str, gl.Stabachse]
```

Knicken, Kippen und die Gleichung um `a` -- ihr Ergebnis mit der Achse.

#### _Herleitung._biegespannung

```python
def _biegespannung(self, a: str) -> float
```

σ_m um `a` in N/mm², in die Herleitung -- null ohne Moment.

#### _Herleitung._gleichung

```python
def _gleichung(self, a: str, x: gl.Stabachse, sigma_c: float, sigma_m: float, k_c: float, k_m: float) -> None
```

(37) oder (38) um `a` mit Zahlen -- und wie weit die Momente wachsen duerfen.

#### _Herleitung.knickwiderstand

```python
def knickwiderstand(self, a: str, si: float) -> Wert
```

`N_K,Rd = -k_c η f_c,0,d A` um `a`, mit dem Zeichen der Druckkraft
-- `si` ist dasselbe, aus dem Erfuellungsgrad der Achse.


## Konstanten

- `KIPPEN_NUR_RECHTECK = 'Kippen weist das Werkzeug beim Holz nur für ein Rechteck nach, mit (…` – Warum ein Querschnitt, der kein Rechteck ist, beim Kippen grau steht.
- `NICHTS_ZU_PRUEFEN = 'Kein Knicken und kein Kippen: der Stab ist nicht gedrückt, wo er ein…` – Was ein Fall sagt, in dem weder Knicken noch Kippen zaehlt.
- `REFERENZ = 'SIA 265:2012, 4.2.8; 4.2.9'`

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.latex]]
- [[opencivil.core.nachweis]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.holzbau.gleichungen]]
- [[opencivil.holzbau.querschnitt]]
- [[opencivil.material.holz]]
- [[opencivil.nachweis.qa_holz]]
- [[opencivil.nachweis.qa_holz_werte]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.biegung]]
- [[opencivil.stahlbau.stabilitaet]]

## Gebraucht von

- [[opencivil.projekt.aufbau.querschnittsanalyse]]

## Formeln aus diesem Modul

- [[Biegespannung im Holz]] · `_Herleitung._biegespannung`
- [[Erfüllungsgrad bei fester Normalkraft und fester Richtung]] · `HolzStabilitaetQA.pruefe`
- [[Hilfswert beim Knicken von Holz]] · `_Herleitung._knicken`
- [[Kippbeiwert des Holzes]] · `_Herleitung._kippen`
- [[Kippspannung eines Rechtecks aus Holz]] · `_Herleitung._kippen`
- [[Knickbeiwert des Holzes]] · `_Herleitung._knicken`
- [[Knickwiderstand eines Holzstabs]] · `_Herleitung.knickwiderstand`
- [[Normalspannung im Holz]] · `_Herleitung.__init__`
- [[Relative Schlankheit beim Kippen von Holz]] · `_Herleitung._kippen`
- [[Relative Schlankheit beim Knicken von Holz]] · `_Herleitung._knicken`
- [[Schlankheit eines Holzstabs]] · `_Herleitung._knicken`
- [[Trägheitsradius]] · `_Herleitung._knicken`
- [[Widerstand in der Richtung der Einwirkung]] · `HolzStabilitaetQA._urteil`
