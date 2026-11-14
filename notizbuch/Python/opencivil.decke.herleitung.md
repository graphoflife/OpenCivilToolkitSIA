---
erzeugt: 31f93680dfa2
art: modul
tags: [modul]
---
> [!abstract] opencivil/decke/herleitung.py
> wie eine Decke ihre Rechnung aufschreibt.
> Paket [[opencivil.decke]] · [Quelltext](../../opencivil/decke/herleitung.py)

## VERANTWORTUNG

Die Herleitung der Streifenmethode, so dass man sie von Hand nachvollziehen
kann: die Decke in Tabellen -- Platten, Linienlager, Stützen, Unterzüge,
Lasten je Lastfall und die Kombinationen --, die Streifen je Richtung, in
welcher Reihenfolge die Träger rechnen, wie die Last auf die Richtungen
geht, je Fall die Last und was die Lager davon tragen, und die Meldungen.
Dann die Ansätze und je Lastfall und Kombination: jeder Träger mit Last,
Lagerkräften und Momenten, was jedes Lager trägt, die grössten
Schnittkräfte der Platte, die Biegewiderstände, die sie verlangt, und die
Lastverteilelemente.


## DIESELBEN ZAHLEN WIE IM BILD

Die grössten Schnittkräfte und Biegewiderstände kommen von den Proben des
Falls ([[opencivil.decke.feld#proben|proben]]), wie in den Bildern.


## GLEICHE TRÄGER IN EINER ZEILE

Tragen nebeneinander liegende Träger dasselbe -- im Kolloquium 4 achtzehn
Feldstreifen in x --, stehen sie in einer Zeile, «x1 … x18». Was sie
unterscheidet, ist nur ihr Ort quer; `s` misst längs.


## EINHEITEN

Längen in m, Dicken und Stützen in mm, Winkel in Grad gegen x, E in N/mm²,
Gewichte und Flächenlasten in kN/m², Linienlasten in kN/m, Kräfte in kN.
Die Träger je Meter ihrer Breite: Lasten und Lagerkräfte in kN/m, Momente
in kNm/m, wie die Schnittkräfte der Platte.

## Inhalt

### schreiben

```python
def schreiben(p: Protokoll, system: 'Deckensystem', befund: 'Deckenbefund') -> None
```

Die ganze Herleitung einer Decke -- nichts davon geht in den Befund ein, also still gar keine.

### _lasten

```python
def _lasten(p: Protokoll, decke: Decke) -> None
```

Die Lasten je Lastfall, wie sie beschrieben sind, und die Beiwerte der Kombinationen.

### _last

```python
def _last(last: Last) -> list
```

Name, Ort und Wert einer Last für die Tabelle.

### _faelle

```python
def _faelle(p: Protokoll, e: Ergebnis) -> None
```

Je Lastfall und Kombination die Last und was die Lager tragen -- die Probe --, und die Meldungen des Falls.

### _ansaetze

```python
def _ansaetze(p: Protokoll, e: Ergebnis) -> None
```

Wie aus den Trägern die Platte wird -- je einmal, was die Decke braucht.

### _fall

```python
def _fall(p: Protokoll, e: Ergebnis, f: Fallergebnis, zellen: Sequence[Sequence[geo.Punkt]]) -> None
```

Ein Lastfall oder eine Kombination: Träger, Lager, Platte, Biegewiderstände, Lastverteilelemente.

### _traeger

```python
def _traeger(p: Protokoll, e: Ergebnis, f: Fallergebnis) -> None
```

Jeder Träger, je Meter seiner Breite -- gleiche Feldstreifen nebeneinander in einer Zeile.

### _reihe

```python
def _reihe(z: Zerlegung) -> List[Tuple[Streifen, int, Traeger]]
```

Die Träger in der Reihe der Zerlegung, je mit der Nummer ihres Stücks
im Streifen -- nur je Richtung der Feldstreifen erst alle ersten Stücke,
dann alle zweiten: so steht x1.2 neben x2.2 statt hinter x1.1.

### _mit_stelle

```python
def _mit_stelle(m: float, s: float) -> Tuple[str, str]
```

Ein Moment in kNm/m und wo es liegt -- ausser es steht als null da.

### _zahl

```python
def _zahl(text: str)
```

Eine Zahl als Formel, damit ihr Minus eines ist; der Strich bleibt Text.

### _lagerkraefte

```python
def _lagerkraefte(p: Protokoll, e: Ergebnis, f: Fallergebnis) -> None
```

Was jedes Lager trägt; längs eines Linienlagers die Spitze und, eingespannt, das grösste Moment.

### _schnittkraefte

```python
def _schnittkraefte(p: Protokoll, proben: Sequence[feld.Probe]) -> None
```

Die grössten und kleinsten Schnittkräfte der Platte, mit Ort.

### _widerstaende

```python
def _widerstaende(p: Protokoll, proben: Sequence[feld.Probe]) -> None
```

Die grössten erforderlichen Biegewiderstände, mit Ort.

### _ort_von

```python
def _ort_von(ort: geo.Punkt, wert: float) -> str
```

Wo ein Wert liegt -- ausser er steht als null da: das ist er an vielen Orten.

### _lastverteilelemente

```python
def _lastverteilelemente(p: Protokoll, e: Ergebnis, f: Fallergebnis) -> None
```

Je Stütze und Einzellast, was ihr Bereich zusätzlich braucht.


## Konstanten

- `ANNAHME = 'Streifenmethode (Stahlbeton II, 7.2 Platten, Folien 27 bis 39): jede…` – Was die Streifenmethode annimmt.
- `AUTOMATISCH = 'Automatisch, nach Folie 31 verallgemeinert: je Zelle zweier Feldstre…` – Die automatische Aufteilung in Worten -- die Regel steht in [[opencivil.decke.aufteilung|aufteilung]].
- `STREIFEN_IN_XY = '\\begin{aligned} & m = \\frac{M}{b} \\qquad m_x = m \\cdot \\cos^2\\…` – Vom Streifen zur Platte -- die Transformation der Folie 14, rückwärts gelesen ([[opencivil.decke.feld|feld]]).
- `FLAECHENLAGER = 'p_{\\mathrm{Lager}} = \\frac{R}{l}'` – Ein Flächenlager drückt gleichmässig über seine Breite (Folie 33).
- `FLIESSBEDINGUNG = "\\begin{aligned} & m_{xu} \\ge m_x + |m_{xy}| \\qquad m_{yu} \\ge m_…` – Die linearisierte Fliessbedingung, `k = k' = 1` ([[opencivil.decke.feld#widerstaende|widerstaende]]).
- `LASTVERTEILELEMENT = "\\begin{aligned} & m'_{xu} \\ge \\frac{Q}{8} \\cdot \\frac{l_x}{l_y}…` – Was ein Lastverteilelement zusätzlich braucht ([[opencivil.decke.feld#Lastverteilelement|Lastverteilelement]]).
- `SCHNITTKRAEFTE = (('m_x', 'm_x', 'kNm/m'), ('m_y', 'm_y', 'kNm/m'), ('m_xy', 'm_{xy}',…` – Die Schnittkräfte der Platte im Bericht: je Grösse ihr Zeichen und ihre Einheit.
- `WIDERSTAENDE = (('mxu', 'm_{xu}', 'unten, in x'), ('myu', 'm_{yu}', 'unten, in y'), …` – Die Biegewiderstände: Feld von [[opencivil.decke.feld#Widerstaende|Widerstaende]], Zeichen, Bedeutung.

## Braucht

- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.decke.feld]]
- [[opencivil.decke.geometrie]]
- [[opencivil.decke.modell]]
- [[opencivil.decke.rechnung]]
- [[opencivil.decke.streifen]]
- [[opencivil.decke.traeger]]
- [[opencivil.decke.werk]]

## Gebraucht von

- [[opencivil.decke.werk]]

## Formeln aus diesem Modul

- [[Lastverteilelement]] · `_ansaetze`
- [[Linearisierte Fliessbedingung]] · `_ansaetze`
- [[Pressung eines Flächenlagers]] · `_ansaetze`
- [[Schnittkräfte eines Streifens in x und y]] · `_ansaetze`
