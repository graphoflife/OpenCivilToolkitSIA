---
erzeugt: d94fd3eeb692
art: modul
tags: [modul]
---
> [!abstract] opencivil/spannungsanalyse/art.py
> welche der sechs Fragen eine Analyse stellt.
> Paket [[opencivil.spannungsanalyse]] · [Quelltext](../../opencivil/spannungsanalyse/art.py)

## VERANTWORTUNG

Die Wahl einer Spannung-Dehnung-Analyse: aus Schnittgroessen, aus
Randdehnungen, die beiden Linien und der aequivalente Modul ueber jeder
([[opencivil.spannungsanalyse.art#Analyseart|Analyseart]]).

## Inhalt

### Analyseart

```python
class Analyseart(Wahl)
```

Welche der sechs Fragen gestellt wird.

- `SCHNITTGROESSEN = 'schnittgroessen'`
- `DEHNUNGEN = 'dehnungen'`
- `MOMENT_KRUEMMUNG = 'moment_kruemmung'`
- `NORMALKRAFT_DEHNUNG = 'normalkraft_dehnung'`
- `MOMENT_EMODUL = 'moment_emodul'`
- `NORMALKRAFT_EMODUL = 'normalkraft_emodul'`

#### Analyseart.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Analyseart.kurz

```python
@property
def kurz(self) -> str
```

Fuer die Auswahl in der Zeile.

#### Analyseart.linie

```python
@property
def linie(self) -> Optional['Analyseart']
```

Die Linie, auf der diese Frage laeuft: M-chi oder N-eps -- der Modul
ist dieselbe Linie, umgerechnet. `None` fuer die beiden Bilder.

#### Analyseart.modul

```python
@property
def modul(self) -> bool
```

Ob gefragt ist, welchen E-Modul ein reiner Betonquerschnitt braeuchte.


## Braucht

- [[opencivil.core.wahl]]

## Gebraucht von

- [[opencivil.spannungsanalyse]]
- [[opencivil.spannungsanalyse.analysen]]
- [[opencivil.spannungsanalyse.herleitung]]
- [[opencivil.spannungsanalyse.linie]]
- [[opencivil.spannungsanalyse.modul]]
- [[opencivil.spannungsanalyse.platte]]
- [[opencivil.spannungsanalyse.schnitt]]
