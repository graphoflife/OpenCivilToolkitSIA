---
erzeugt: 2eb06f7a0dbf
art: modul
tags: [modul]
---
> [!abstract] opencivil/material/arten.py
> die Materialarten des Projekts, je eine Zeile.
> Paket [[opencivil.material]] · [Quelltext](../../opencivil/material/arten.py)

## VERANTWORTUNG

Was Projekt, Aufbau und Oberflaeche ueber eine Materialart wissen muessen:
ihre Sorten und Kennwerte, wie ein Material entsteht, womit seine Kennung
und der Name eines eigenen beginnen, und worauf die Kennwerte stehen. Die
Oberflaeche liest dasselbe aus dem Katalog (`materialarten`).

Bis 2026-11-15 stand das an sieben Stellen je von Hand, als Zuordnung von
«beton» und «betonstahl» – der Baustahl haette an jeder dazukommen muessen,
und eine vergessene fiele erst beim Anlegen auf.

## Inhalt

### Materialart

```python
@dataclass(frozen=True)
class Materialart
```

- `art: Baustoffart`
- `sorten: Mapping[str, Any]`
- `vorlagen: Tuple[KennwertVorlage, ...]`
- `bauen: Callable[..., Baustoff]` – Wie [[opencivil.material.beton#beton|beton]]: Sorte, dann Name, Praefix, Abweichungen.
- `anlegen: Tuple[str, ...]` – Die Sorten in der Folge, in der das Fenster «Neues Material» sie anbietet.
- `kennung: str` – Womit die Kennung beginnt: b1, s1, st1, sp1, h1, pb1.
- `eigene: str` – Womit der Name eines eigenen Materials beginnt: BE1, S1, ST1 (Benutzer, 2026-10-16), SP1 beim Spannstahl, H1 beim Holz, PB1 beim Profilblechstahl.
- `grundlage: str` – Worauf die Kennwerte einer Normsorte stehen – so steht es in der Oberflaeche.
- `grundlagen: Mapping[str, str] = field(default_factory=dict)` – Je Sorte, deren Kennwerte anderswo stehen, worauf – beim Betonstahl der «Stahl II» aus SIA 269/2:2011 ([[opencivil.material.betonstahl#Konstanten|STAHL_II]]).
- `erzeugnisse: Mapping[str, Tuple[Erzeugnis, ...]] = field(default_factory=dict)` – Je Sorte, in welchen Erzeugnissen es sie gibt – beim Spannstahl Draehte, Litzen und Staebe nach Tabelle 7; die anderen Arten haben keine Liste.
- `erzeugnisquelle: str = ''` – Wo die Erzeugnisse stehen.
- `saechlich: bool = False` – Ob die Art «das» heisst: «Neues Holz», «ein Holz» – die anderen sind maennlich. Bis 2026-11-26 stand «Neuer» und «einen» fest im Text.

#### Materialart.titel

```python
@property
def titel(self) -> str
```

#### Materialart.grundlage_von

```python
def grundlage_von(self, sorte: str) -> str
```

Worauf die Kennwerte der Normsorte `sorte` stehen – ihre eigene oder die der Art.

#### Materialart.neu

```python
@property
def neu(self) -> str
```

«Neuer Beton», «Neues Holz».

#### Materialart.eigen

```python
@property
def eigen(self) -> str
```

«Eigener Beton», «Eigenes Holz».

#### Materialart.einen

```python
@property
def einen(self) -> str
```

Im Akkusativ: «einen Beton», «ein Holz».

#### Materialart.keinen

```python
@property
def keinen(self) -> str
```

Im Akkusativ: «keinen Beton», «kein Holz».


## Konstanten

- `MATERIALARTEN = {a.art.value: a for a in (Materialart(Baustoffart.BETON, BETONSORTEN,…`

## Braucht

- [[opencivil.material.basis]]
- [[opencivil.material.baustahl]]
- [[opencivil.material.beton]]
- [[opencivil.material.betonstahl]]
- [[opencivil.material.holz]]
- [[opencivil.material.profilblech]]
- [[opencivil.material.spannstahl]]

## Gebraucht von

- [[opencivil.mcp.ausgabe]]
- [[opencivil.mcp.werkzeuge]]
- [[opencivil.notizbuch.formelseiten]]
- [[opencivil.projekt.aufbau.balkensystem]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.projekt]]
- [[opencivil.web.api]]
