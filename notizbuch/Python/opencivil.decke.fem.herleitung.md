---
erzeugt: d349fc61a0d9
art: modul
tags: [modul]
---
> [!abstract] opencivil/decke/fem/herleitung.py
> wie die FEM einer Decke ihre Rechnung aufschreibt.
> Paket [[opencivil.decke.fem]] · [Quelltext](../../opencivil/decke/fem/herleitung.py)

## VERANTWORTUNG

Die Herleitung der FEM, so dass man sieht, was gerechnet ist: die Decke in
Tabellen – Platten mit ihrer Steifigkeit, Linienlager, Stützen, Träger
mit ihrer Biegesteifigkeit, Lasten je Lastfall und die Kombinationen –,
das Netz, je Fall die Last und was die Lager davon tragen, und die
Meldungen. Dann die Ansätze – die Momente der Platte nach Kirchhoff, die
Querkräfte aus ihnen, der Träger in der Platte, die Fliessbedingung – und
je Lastfall und Kombination: was jedes Lager trägt, die grössten
Schnittkräfte und die grösste Durchbiegung, die Biegewiderstände, die die
Platte verlangt, und Moment und Querkraft jedes Trägers.

Die Tabellen, die beide Verfahren gleich haben, schreibt
[[opencivil.decke.herleitung]]. Die grössten Werte kommen von den
Knoten ([[opencivil.decke.fem.auswertung#proben|proben]]), wie im Bild.


## EINHEITEN

wie in der Streifenmethode; dazu `D` in MNm, `EI` in MNm² und die
Durchbiegung in mm.

## Inhalt

### schreiben

```python
def schreiben(p: Protokoll, system: 'Deckensystem', befund: 'Deckenbefund') -> None
```

Die ganze Herleitung einer Decke nach der FEM – nichts davon geht in den Befund ein, also still gar keine.

### _lager

```python
def _lager(p: Protokoll, decke: Decke, e: Optional[Femergebnis]) -> None
```

Stützen als Punkte, Träger mit der Biegesteifigkeit ihres Balkens – wie das System sie rechnet.

### _ansaetze

```python
def _ansaetze(p: Protokoll, e: Femergebnis) -> None
```

Die Platte, ihre Querkräfte, die Träger und die Fliessbedingung – je einmal, was die Decke braucht.

### _fall

```python
def _fall(p: Protokoll, e: Femergebnis, f: Femfall) -> None
```

Ein Lastfall oder eine Kombination: Lager, Platte, Biegewiderstände, Träger.

### _traeger

```python
def _traeger(p: Protokoll, e: Femergebnis, f: Femfall) -> None
```

Je Träger das kleinste und das grösste Moment und die grösste Querkraft, über seine ganze Breite.

### _stelle

```python
def _stelle(u: float, wert: float) -> str
```

Wo ein Wert eines Trägers liegt – ausser er steht als null da.


## Konstanten

- `ANNAHME = 'FEM: die ganze Platte linear elastisch und ungerissen, mit E_cm und …` – Was die FEM annimmt.
- `PLATTE = '\\begin{aligned} & D = \\frac{E_{cm} \\cdot h^3}{12 \\cdot (1 - \\nu…` – Die Momente der Platte aus ihrer Krümmung ([[opencivil.decke.fem.element|element]]).
- `QUERKRAEFTE = 'v_x = \\frac{\\partial m_x}{\\partial x} + \\frac{\\partial m_{xy}}{…` – Die Querkräfte aus dem Gefälle der Momente ([[opencivil.decke.fem.rechnung|rechnung]]).
- `TRAEGER = '\\begin{aligned} & EI = E_{cm} \\cdot b \\cdot \\frac{(h + h_T)^3 - …` – Ein Träger in der Platte ([[opencivil.decke.fem.system|system]], [[opencivil.decke.fem.auswertung|auswertung]]).
- `LAENGS = 'Längs eines Linienlagers gehört zu jedem Knoten das Stück bis zur Mi…` – Wie die Kraft längs eines Linienlagers verteilt ist, in der FEM ([[opencivil.decke.fem.rechnung|rechnung]]).
- `WO = 'Gesucht an jedem Knoten des Netzes: über ein Dreieck ist jede Grösse…` – Wo die grössten Werte gesucht sind.
- `GROESSEN = (*SCHNITTKRAEFTE, ('w', 'w', 'mm', 1000.0))` – Die Grössen der Platte im Bericht, mit der Durchbiegung.

## Braucht

- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.decke.fem.auswertung]]
- [[opencivil.decke.fem.element]]
- [[opencivil.decke.fem.rechnung]]
- [[opencivil.decke.geometrie]]
- [[opencivil.decke.herleitung]]
- [[opencivil.decke.modell]]
- [[opencivil.decke.werk]]

## Gebraucht von

- [[opencivil.decke.werk]]

## Formeln aus diesem Modul

- [[Linearisierte Fliessbedingung]] · `_ansaetze`
- [[Momente der Platte nach Kirchhoff]] · `_ansaetze`
- [[Querkräfte aus den Momenten der Platte]] · `_ansaetze`
- [[Träger in der Platte]] · `_ansaetze`
