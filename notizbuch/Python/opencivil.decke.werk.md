---
erzeugt: d2681c58dd67
art: modul
tags: [modul]
---
> [!abstract] opencivil/decke/werk.py
> die Decke im Rechenwerk.
> Paket [[opencivil.decke]] · [Quelltext](../../opencivil/decke/werk.py)

## VERANTWORTUNG

Was eine Decke im Rechenwerk anmeldet: eine Prozedur, die sie nach ihrem
Verfahren rechnet und ihre Herleitung schreibt – nach der Streifenmethode
([[opencivil.decke.rechnung|rechnung]], [[opencivil.decke.herleitung|herleitung]]) oder
der FEM ([[opencivil.decke.fem|fem]]) –, samt dem, was sie von aussen
liest. Welches Verfahren, steht einmal fest, wenn die Decke angemeldet
wird ([[opencivil.decke.werk#Konstanten|VERFAHREN]]).


## E UND GEWICHT

nimmt jede Platte von ihrem Beton, wie ein Stab des Balkensystems
([[opencivil.stabwerk.rechnung#Konstanten|STABKENNWERTE]]): `E_cm` am
ungerissenen Querschnitt (SIA 262:2025, 4.1.4.1.3) und die Dichte des
Stahlbetons, mit
`g = 10 m/s²` ([[opencivil.material.basis#Konstanten|ERDBESCHLEUNIGUNG]],
Benutzer, 2026-10-23) ihr Gewicht je m³. Die Regel steht dort; hier wird
sie nur gelesen. Die FEM nimmt dazu `ν_c` (SIA 262:2025, 3.1.2.3.5).


## DAS ERGEBNIS

kommt als Befund in die Loesung ([[opencivil.decke.werk#Deckenbefund|Deckenbefund]]); Bilder und
Zusammenfassung lesen es dort. Eine Decke, die nicht rechnet, ist ein
Befund mit Meldung und keine Ausnahme: der Rest des Projekts rechnet weiter.

## Inhalt

### Art

```python
@dataclass(frozen=True)
class Art
```

Ein Verfahren, eine Decke zu rechnen: Thema der Formelsammlung, Titel,
Rechnung und Herleitung – und ob es die Querdehnungszahl des Betons braucht.

- `thema: str`
- `titel: str`
- `rechnen: Callable[[Decke], Any]`
- `schreiben: Callable[..., None]`
- `querdehnung: bool = False`

### Deckenbefund

```python
@dataclass
class Deckenbefund
```

Was die Rechnung im Lauf fand: die Decke, wie sie gerechnet wurde –
mit E, ν und Gewicht jeder Platte und in der Streifenmethode den
Richtungen, die sie selbst wählt –, die Meldungen und das Ergebnis.

- `gerechnet: Decke`
- `meldungen: List[Meldung]` – Die der Beschreibung und die der Rechnung, in dieser Reihenfolge.
- `ergebnis: Optional[Union[Ergebnis, Femergebnis]] = None` – `None`, wenn eine Meldung der Beschreibung die Rechnung aufhielt.

### DeckenProzedur

```python
class DeckenProzedur(Prozedur)
```

Die ganze Decke, gerechnet und aufgeschrieben – ihr Thema ist das ihres Verfahrens.

#### DeckenProzedur.rechne

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

E, ν und Gewicht in die Platten, die Decke gerechnet, die Herleitung
geschrieben. Hält eine Meldung der Beschreibung die Rechnung auf,
bleibt es bei ihr.


## Konstanten

- `VERFAHREN = {Verfahren.STREIFEN: Art('Streifenmethode', 'Streifenmethode', rechnu…` – Je Verfahren, wie es rechnet und schreibt.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.rechenobjekt]]
- [[opencivil.core.wert]]
- [[opencivil.decke.fem.herleitung]]
- [[opencivil.decke.fem.rechnung]]
- [[opencivil.decke.herleitung]]
- [[opencivil.decke.modell]]
- [[opencivil.decke.rechnung]]
- [[opencivil.material.basis]]
- [[opencivil.stabwerk.rechnung]]
- [[opencivil.stabwerk.system]]

## Gebraucht von

- [[opencivil.decke.fem.herleitung]]
- [[opencivil.decke.herleitung]]
- [[opencivil.projekt.aufbau.decke]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.web.deckendaten]]
