---
erzeugt: 75d26476ae0c
art: modul
tags: [modul]
---
> [!abstract] opencivil/mauerwerk/herleitung.py
> wie eine Mauerwerkswand ihre Rechnung aufschreibt.
> Paket [[opencivil.mauerwerk]] · [Quelltext](../../opencivil/mauerwerk/herleitung.py)

## VERANTWORTUNG

Die Wand in Zahlen: ihre Masse und ihr Mauerwerk, wie sie gemauert und
gehalten ist, die Bemessungswerte, mit denen sie rechnet, ihre Öffnungen
mit den Stürzen darüber und die Pfeiler dazwischen. Zuletzt die
Meldungen: rot, was falsch ist, sonst als Hinweis.


## EINHEITEN

Masse der Wand und Orte in m, die Masse eines Sturzes in mm – wie in der
Maske; Festigkeiten und Moduln in N/mm², wie im Material. Die Dicke der
Wand steht im Kasten ihrer Vorgaben.

## Inhalt

### schreiben

```python
def schreiben(p: Protokoll, befund: 'Wandbefund') -> None
```

Die ganze Herleitung – nichts davon geht in den Befund ein, also still gar keine.

### _gemauert

```python
def _gemauert(w: Wand) -> str
```

Wie die Wand gemauert ist, als Satz.

### _gehalten

```python
def _gehalten(w: Wand) -> str
```

Wie ihre Ränder gehalten sind, als Satz.

### _werte

```python
def _werte(p: Protokoll, befund: 'Wandbefund') -> None
```

Die Bemessungswerte des Mauerwerks und die der Wand, im Verband mit dem Faktor.

### _wertzeile

```python
def _wertzeile(kurz: str, symbol: str, stellen: int, material: dict, werte: Wandwerte, vollfugig: bool) -> List[Zelle]
```

Eine Zeile: der Wert des Mauerwerks, der der Wand – im Verband mit dem Faktor davor.

### _oeffnungen

```python
def _oeffnungen(p: Protokoll, w: Wand) -> None
```

Je Öffnung ihr Ort, ihre Masse und der Sturz darüber.

### _von_bis

```python
def _von_bis(von: float, bis: float) -> str
```

Zwei Masse in m, als Spanne: «1.00 – 2.00».

### _pfeiler

```python
def _pfeiler(p: Protokoll, pfeiler: List[Pfeiler]) -> None
```

Je Pfeiler, wo er steht, wie breit er ist und zwischen welchen Öffnungen.


## Konstanten

- `ANNAHME = 'Eine Wand aus unbewehrtem Mauerwerk nach SIA 266:2015, gezeichnet in…` – Was die Wand annimmt – in eigenen Worten nach SIA 266:2015, 4.1.2 und 4.1.4.
- `ZEILEN = (('f_xd', 'f_{xd}', 2), ('f_yd', 'f_{yd}', 2), ('E_xd', 'E_{xd}', 0),…` – Je Wert der Tabelle: Kurzname, Zeichen, Stellen.

## Braucht

- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.sprache]]
- [[opencivil.mauerwerk.kennwerte]]
- [[opencivil.mauerwerk.modell]]
- [[opencivil.mauerwerk.werk]]

## Gebraucht von

- [[opencivil.mauerwerk.werk]]
