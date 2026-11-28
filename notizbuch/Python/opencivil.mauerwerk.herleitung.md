---
erzeugt: f895f27fe3bf
art: modul
tags: [modul]
---
> [!abstract] opencivil/mauerwerk/herleitung.py
> wie eine Mauerwerkswand ihre Rechnung aufschreibt.
> Paket [[opencivil.mauerwerk]] · [Quelltext](../../opencivil/mauerwerk/herleitung.py)

## VERANTWORTUNG

Die Wand in Zahlen: ihre Masse und ihr Mauerwerk, wie sie gemauert und
gehalten ist, die Bemessungswerte, mit denen sie rechnet, ihre Öffnungen
mit den Stürzen darüber, die Pfeiler dazwischen und was die Lastfälle und
Kombinationen ihnen geben ([[opencivil.mauerwerk.lasten|lasten]]) – schiebt
eine Last waagrecht, auch in der Ebene der Wand
([[opencivil.mauerwerk.scheibe|scheibe]]), und mit Querlasten, was quer zu ihr
wirkt, die Ersatzkraft des Erdbebens hergeleitet
([[opencivil.mauerwerk.querlast|querlast]]). Zuletzt die Meldungen: rot, was
falsch ist, sonst als Hinweis.


## EINHEITEN

Masse der Wand und Orte in m, die Masse eines Sturzes in mm – wie in der
Maske; Festigkeiten und Moduln in N/mm², wie im Material; Kräfte in kN,
Momente in kNm. Die Dicke der Wand steht im Kasten ihrer Vorgaben.

## Inhalt

### schreiben

```python
def schreiben(p: Protokoll, befund: 'Wandbefund', e: Eingaben, basis: str) -> None
```

Die ganze Herleitung – nichts davon geht in den Befund ein, also still
gar keine. `e` sind die Eingaben der Wand, `basis` der Anfang der
Kennungen ihrer Zwischenwerte.

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

### _lasten

```python
def _lasten(p: Protokoll, befund: 'Wandbefund', e: Eingaben, basis: str) -> None
```

Das Eigengewicht je m², dann je Lastfall und Kombination, was Pfeiler
und Stürze tragen: die Normalkraft am Fuss jedes Pfeilers, an seinem
Kopf die der Lasten allein und das Moment ihrer Ausmitten, und die
Kräfte der Sturzauflager.

### _scheibe

```python
def _scheibe(p: Protokoll, befund: 'Wandbefund', kopf: List[str], faelle: Dict[str, Abtrag]) -> None
```

Was die waagrechten Lasten den Pfeilern geben: Querkraft, Normalkraft und Moment am Fuss.

### _tabelle

```python
def _tabelle(p: Protokoll, kopf: List[str], faelle: Dict[str, Abtrag], zeilen: Sequence[Tuple[str, Callable[[Abtrag], float]]], faktor: float, stellen: int, titel: str) -> None
```

Je Zeile ihr Name und je Fall die Zahl, die `lesen` aus seinem Abtrag liest, in SI.


## Konstanten

- `ANNAHME = 'Eine Wand aus unbewehrtem Mauerwerk nach SIA 266:2015, gezeichnet in…` – Was die Wand annimmt – in eigenen Worten nach SIA 266:2015, 4.1.2 und 4.1.4.
- `ABTRAG = 'Die Lasten gehen lotrecht nach unten. Was über einem Pfeiler liegt, …` – Wie die Lasten zu den Pfeilern kommen, in eigenen Worten ([[opencivil.mauerwerk.lasten|.lasten]]).
- `ABTRAG_ANNAHME = 'Den Lastabtrag in der Wand regelt die Norm nicht; so verteilt das We…` – Woher die Regeln des Lastabtrags kommen.
- `SCHEIBE = 'Die waagrechten Lasten nimmt die Wand als Scheibe auf. Über den Öffn…` – Wie die waagrechten Lasten zu den Pfeilern kommen, in eigenen Worten ([[opencivil.mauerwerk.scheibe|.scheibe]]).
- `SCHEIBE_ANNAHME = 'Wie die Wand als Scheibe trägt, regelt die Norm nicht; so verteilt d…` – Woher die Regeln der Scheibe kommen.
- `QUER = 'Eine Querlast wirkt gleichmässig über die ganze Wand, je m² Ansicht.…` – Wie die Querlasten wirken, in eigenen Worten.
- `ZEILEN = (('f_xd', 'f_{xd}', 2), ('f_yd', 'f_{yd}', 2), ('E_xd', 'E_{xd}', 0),…` – Je Wert der Tabelle: Kurzname, Zeichen, Stellen.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.sprache]]
- [[opencivil.mauerwerk.kennwerte]]
- [[opencivil.mauerwerk.lasten]]
- [[opencivil.mauerwerk.modell]]
- [[opencivil.mauerwerk.querlast]]
- [[opencivil.mauerwerk.scheibe]]
- [[opencivil.mauerwerk.werk]]

## Gebraucht von

- [[opencivil.mauerwerk.werk]]

## Formeln aus diesem Modul

- [[Eigengewicht der Wand je m² Ansicht, aus der Dichte ihres Mauerwerks]] · `_lasten`
