---
erzeugt: 9d9603878aed
art: modul
tags: [modul]
---
> [!abstract] opencivil/decke/werk.py
> die Decke im Rechenwerk.
> Paket [[opencivil.decke]] · [Quelltext](../../opencivil/decke/werk.py)

## VERANTWORTUNG

Was eine Decke im Rechenwerk anmeldet: eine Prozedur, die sie nach der
Streifenmethode rechnet ([[opencivil.decke.rechnung#rechnen|rechnen]]) und ihre
Herleitung schreibt ([[opencivil.decke.herleitung|herleitung]]), samt dem, was sie
von aussen liest.


## E UND GEWICHT

nimmt jede Platte von ihrem Beton, wie ein Stab des Balkensystems
([[opencivil.stabwerk.rechnung#Konstanten|BETONKENNWERTE]]): `E_cm` -- nach
Vorgabe, nicht nachgeschlagen -- und die Dichte des Stahlbetons, mit
`g = 10 m/s²` ([[opencivil.stabwerk.rechnung#Konstanten|ERDBESCHLEUNIGUNG]],
Benutzer, 2026-10-23) ihr Gewicht je m³. Die Regel steht dort; hier wird
sie nur gelesen.


## DAS ERGEBNIS

kommt als Befund in die Loesung ([[opencivil.decke.werk#Deckenbefund|Deckenbefund]]); Bilder und
Zusammenfassung lesen es dort. Eine Decke, die nicht rechnet, ist ein
Befund mit Meldung und keine Ausnahme: der Rest des Projekts rechnet weiter.

## Inhalt

### Deckenbefund

```python
@dataclass
class Deckenbefund
```

Was die Streifenmethode im Lauf fand: die Decke, wie sie gerechnet wurde
-- mit E und Gewicht jeder Platte --, die Meldungen und das Ergebnis.

- `gerechnet: Decke`
- `meldungen: List[Meldung]` – Die der Beschreibung und die der Rechnung, in dieser Reihenfolge.
- `ergebnis: Optional[Ergebnis] = None` – `None`, wenn eine Meldung der Beschreibung die Rechnung aufhielt.

### StreifenmethodeProzedur

```python
class StreifenmethodeProzedur(Prozedur)
```

Die ganze Decke, gerechnet und aufgeschrieben.

- `THEMA = STREIFENMETHODE`

#### StreifenmethodeProzedur.rechne

```python
def rechne(self, e: Eingaben, p: Protokoll) -> Ausfuehrung
```

### Deckensystem

```python
class Deckensystem(Rechenobjekt)
```

Eine Decke, fertig fuer das Rechenwerk.

- `WAS = 'Decke'`

#### Deckensystem.abschnitt

```python
def abschnitt(self) -> Abschnitt
```

#### Deckensystem.baustoffe

```python
@property
def baustoffe(self) -> List[Baustoff]
```

Die Betone der Platten, jeder einmal.

#### Deckensystem.ziele

```python
def ziele(self) -> List[str]
```

Was ein Lauf rechnen muss: die Decke.

#### Deckensystem.rechnen_und_schreiben

```python
def rechnen_und_schreiben(self, e: Eingaben, p: Protokoll) -> Ausfuehrung
```

E und Gewicht in die Platten, die Decke gerechnet, die Herleitung
geschrieben. Hält eine Meldung der Beschreibung die Rechnung auf,
bleibt es bei ihr.


## Konstanten

- `STREIFENMETHODE = 'Streifenmethode'` – Das Thema der Formelsammlung.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.rechenobjekt]]
- [[opencivil.core.wert]]
- [[opencivil.decke.herleitung]]
- [[opencivil.decke.modell]]
- [[opencivil.decke.rechnung]]
- [[opencivil.material.basis]]
- [[opencivil.stabwerk.rechnung]]
- [[opencivil.stabwerk.system]]

## Gebraucht von

- [[opencivil.decke.herleitung]]
- [[opencivil.projekt.aufbau.decke]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.web.deckendaten]]
