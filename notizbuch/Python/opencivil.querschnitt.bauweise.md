---
erzeugt: a8e43004e86b
art: modul
tags: [modul]
---
> [!abstract] opencivil/querschnitt/bauweise.py
> woraus ein gezeichneter Querschnitt besteht.
> Paket [[opencivil.querschnitt]] · [Quelltext](../../opencivil/querschnitt/bauweise.py)

## VERANTWORTUNG

Die Bauweise eines gezeichneten Querschnitts aus den Arten seiner Baustoffe
([[opencivil.querschnitt.bauweise#bauweise|bauweise]]): Stahlbeton, Stahl, Verbund, Blechverbund oder Holz. Nach ihr richtet
sich, welche Nachweise er hat und nach welcher Norm. Eine Mischung, die
keine davon ist, rechnet das Werkzeug nicht; der Satz dazu nennt die
Materialien beim Namen.


## DIE REGEL (Benutzer, 2026-11-25)

* Beton, mit oder ohne Betonstahl und Spannstahl: Stahlbeton – auch ohne
  Bewehrung, wie bisher; seine Nachweise sagen dann, was ihnen fehlt.
* nur Baustahl: Stahl.
* Baustahl mit Beton, mit oder ohne Betonstahl: Verbund.
* nur Holz: Holz.
* Profilblechstahl mit Beton, mit oder ohne Betonstahl: Blechverbund – eine
  Blechverbunddecke nach SIA 264:2014, 5.4 (2026-11-27). Mit Baustahl dazu
  waere es ein Verbundtraeger mit Profilblech (6.1.3); den rechnet das
  Werkzeug noch nicht.

Holz mit einem anderen Baustoff ist keine davon, ebenso Spannstahl neben
Baustahl. Ohne Material hat ein Querschnitt keine Bauweise: es gibt nichts,
was traegt, und das sagt schon die Zeichnung
([[opencivil.querschnitt.analyse#Zeichnung|Zeichnung]]).

Welche Arten eine Flaeche nehmen darf, steht an ihrem Feld
([[opencivil.projekt.lesen#materialfeld|materialfeld]]), nicht hier; worin
Bewehrung liegt, in [[opencivil.querschnitt.bauweise#Konstanten|BEWEHRT]].

## Inhalt

### Bauweise

```python
class Bauweise(Wahl)
```

Woraus ein gezeichneter Querschnitt besteht – siehe Dateikopf.

- `STAHLBETON = 'stahlbeton'`
- `STAHL = 'stahl'`
- `VERBUND = 'verbund'`
- `BLECHVERBUND = 'blechverbund'`
- `HOLZ = 'holz'`

#### Bauweise.querschnitt

```python
@property
def querschnitt(self) -> str
```

Wie ein Satz einen Querschnitt dieser Bauweise nennt: «ein Holzquerschnitt».

#### Bauweise.norm

```python
@property
def norm(self) -> str
```

Die Norm, nach der ein Querschnitt dieser Bauweise nachgewiesen wird.

### Mischung

```python
class Mischung(ValueError)
```

Baustoffe, die zusammen keine Bauweise sind – der Text nennt sie.

### bauweise

```python
def bauweise(stoffe: Iterable[Tuple[Baustoffart, str]]) -> Optional[Bauweise]
```

Die Bauweise aus Art und Name jedes Baustoffs eines Querschnitts –
`None` ohne Baustoff. Ist die Mischung keine Bauweise, eine
[[opencivil.querschnitt.bauweise#Mischung|Mischung]], die jede Art mit ihren Materialien nennt: «Einen
Querschnitt aus Holz («C24») und Beton («C30/37») rechnet das Werkzeug
nicht.»


## Konstanten

- `BEWEHRT = Baustoffart.BETON` – Worin Bewehrung liegt – Stab, Stablinie, Schubwand und Spannglied: nur im Beton, nicht in Holz und nicht in Baustahl (Benutzer, 2026-11-25). Die Zeichnung prueft es ([[opencivil.querschnitt.analyse#Zeichnung|Zeichnung]]), und eine Vorlage aus anderem kommt ohne Bewehrung.
- `BLECHVERBUND = frozenset({Baustoffart.PROFILBLECH, Baustoffart.BETON, Baustoffart.BE…` – Woraus eine Blechverbunddecke sein darf – Beton muss dabei sein.

## Braucht

- [[opencivil.core.sprache]]
- [[opencivil.core.wahl]]
- [[opencivil.material.basis]]

## Gebraucht von

- [[opencivil.projekt.aufbau.erdbeben]]
- [[opencivil.projekt.aufbau.querschnittsanalyse]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.spannungsanalyse.analysen]]
- [[opencivil.spannungsanalyse.modul]]
- [[opencivil.web.api]]
- [[opencivil.web.zeichengeometrie]]
