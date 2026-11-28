---
erzeugt: ca62e798d4aa
art: modul
tags: [modul]
---
> [!abstract] opencivil/material/arten.py
> die Materialarten des Projekts, je eine Zeile.
> Paket [[opencivil.material]] · [Quelltext](../../opencivil/material/arten.py)

## VERANTWORTUNG

Was Projekt, Aufbau und Oberflaeche ueber eine Materialart wissen muessen:
ihre Sorten und Kennwerte, wie ein Material entsteht, womit seine Kennung
und der Name eines eigenen beginnen, worauf die Kennwerte stehen, ob sie
einen Wertesatz hat und wie ein Satz sie nennt. Die Oberflaeche liest
dasselbe aus dem Katalog (`materialarten`).

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
- `kennung: str` – Womit die Kennung beginnt: b1, s1, st1, sp1, h1, pb1, fl1, mw1.
- `eigene: str` – Womit der Name eines eigenen Materials beginnt: BE1, S1, ST1 (Benutzer, 2026-10-16), SP1 beim Spannstahl, H1 beim Holz, PB1 beim Profilblechstahl, FL1 bei einer Fluessigkeit, MW1 beim Mauerwerk.
- `grundlage: str` – Worauf die Kennwerte einer Normsorte stehen – so steht es in der Oberflaeche.
- `grundlagen: Mapping[str, str] = field(default_factory=dict)` – Je Sorte, deren Kennwerte anderswo stehen, worauf – beim Betonstahl der «Stahl II» aus SIA 269/2:2011 ([[opencivil.material.betonstahl#Konstanten|STAHL_II]]).
- `erzeugnisse: Mapping[str, Tuple[Erzeugnis, ...]] = field(default_factory=dict)` – Je Sorte, in welchen Erzeugnissen es sie gibt – beim Spannstahl Draehte, Litzen und Staebe nach Tabelle 7; die anderen Arten haben keine Liste.
- `erzeugnisquelle: str = ''` – Wo die Erzeugnisse stehen.
- `mit_satz: bool = True` – Ob ein Material dieser Art mit Bemessungswerten oder charakteristischen rechnen kann – ob die Rechenwahl ihm einen Wertesatz gibt ([[opencivil.querschnitt.gesetzwahl#Werkstoffsatz|Werkstoffsatz]]). Das Holz hat keinen: SIA 265:2012 nennt nur Bemessungswerte. Eine Fluessigkeit traegt nichts. Bis 2026-11-27 nahmen zwei Stellen je von Hand das Holz aus.
- `aus_norm: bool = True` – Ob die festen Sorten dieser Art in einer Norm stehen: dann heissen sie in der Oberflaeche «Normsorte nach SIA», mit der Marke «SIA». Das Wasser steht in keiner ([[opencivil.material.fluessigkeit]]) – es bleibt, wie es ist, ist aber keine Normsorte.
- `geschlecht: str = 'm'` – Wie die Art heisst – «m», «f» oder «n»: «Neuer Beton», «Neue Flüssigkeit», «Neues Holz». Bis 2026-11-26 stand «Neuer» und «einen» fest im Text, bis 2026-11-27 kannte die Art nur maennlich und saechlich.

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

#### Materialart._wort

```python
def _wort(self, maennlich: str, weiblich: str, saechlich: str) -> str
```

Das Wort vor dem Titel, nach dem Geschlecht der Art.

#### Materialart.neu

```python
@property
def neu(self) -> str
```

«Neuer Beton», «Neue Flüssigkeit», «Neues Holz».

#### Materialart.eigen

```python
@property
def eigen(self) -> str
```

«Eigener Beton», «Eigene Flüssigkeit», «Eigenes Holz».

#### Materialart.einen

```python
@property
def einen(self) -> str
```

Im Akkusativ: «einen Beton», «eine Flüssigkeit», «ein Holz».

#### Materialart.keinen

```python
@property
def keinen(self) -> str
```

Im Akkusativ: «keinen Beton», «keine Flüssigkeit», «kein Holz».

#### Materialart.kein_wort

```python
@property
def kein_wort(self) -> str
```

«kein» oder «keine», im Nominativ.

#### Materialart.kein

```python
@property
def kein(self) -> str
```

Im Nominativ: «kein Beton», «keine Flüssigkeit», «kein Holz».

### keines

```python
def keines(arten: Sequence[str]) -> str
```

Was fehlt oder nicht passt, im Nominativ: «keine Flüssigkeit», «kein Beton,
Baustahl oder Holz». Haben die Arten verschiedene Geschlechter, steht vor
jeder ihr eigenes Wort: «kein Beton oder keine Flüssigkeit». Die
Oberflaeche setzt es ebenso zusammen (`keines` in web/js/bausteine.js);
beide nehmen das Wort der Art, `kein_wort` im Katalog.


## Konstanten

- `MATERIALARTEN = {a.art.value: a for a in (Materialart(Baustoffart.BETON, BETONSORTEN,…`

## Braucht

- [[opencivil.core.sprache]]
- [[opencivil.material.basis]]
- [[opencivil.material.baustahl]]
- [[opencivil.material.beton]]
- [[opencivil.material.betonstahl]]
- [[opencivil.material.fluessigkeit]]
- [[opencivil.material.holz]]
- [[opencivil.material.mauerwerk]]
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
