---
erzeugt: bf863053f06a
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/fachwerkmodell.py
> ein Fachwerkmodell, wie die Oberfläche es beschreibt.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/fachwerkmodell.py)

## VERANTWORTUNG

Der [[opencivil.projekt.fachwerkmodell#FachwerkmodellEintrag|FachwerkmodellEintrag]]: eine Scheibe aus Umrissen und Löchern,
Lager und Punktlasten, gezeichnet aus Knoten in der Ebene – als
speicherbare Datenklasse wie die Decke ([[opencivil.projekt.decke]]).
Dazu der Baukasten, der ohne Oberfläche zeichnet. Gerechnet wird in
[[opencivil.fachwerkmodell]].


## ALLES HÄNGT AN KNOTEN

Eine Scheibe und ein Loch sind Umrisse aus Knoten, ein Lager und eine
Last stehen an einem. Wo ein Lager an einer Ecke steht, teilt es ihren
Knoten: wer ihn verschiebt, verschiebt beide.


## KEIN MATERIAL, KEINE LASTFÄLLE

Ohne Bemessung hängen Fachwerk und Kräfte nur von Form, Lagern und Lasten
ab. Ein Satz Lasten je Modell; für einen zweiten Lastfall kopiert man es
(Plan vom 2026-11-27, Entscheid 11).


## KOORDINATEN UND EINHEITEN

x nach rechts, y nach oben, in m. Eine Last in kN, `F_h` nach rechts,
`F_v` nach unten positiv – wie im Balkensystem. Umgerechnet wird beim
Bauen.

## Inhalt

### ScheibenknotenEintrag

```python
@dataclass
class ScheibenknotenEintrag(Beschreibung)
```

Ein Punkt der Scheibe, in m.

- `kennung: str = ''`
- `x: float = bereich(0.0, heisst='x', einheit=M)`
- `y: float = bereich(0.0, heisst='y', einheit=M)`

### ScheibeEintrag

```python
@dataclass
class ScheibeEintrag(Beschreibung)
```

Ein Umriss der Scheibe – liegen mehrere da, ist Material, wo eine von ihnen ist.

- `kennung: str = ''`
- `knoten: List[str] = field(default_factory=list)`

### LochEintrag

```python
@dataclass
class LochEintrag(Beschreibung)
```

Ein Loch: in seinem Innern ist kein Material, auf seinem Rand schon.

- `kennung: str = ''`
- `knoten: List[str] = field(default_factory=list)`

### ScheibenlagerEintrag

```python
@dataclass
class ScheibenlagerEintrag(Beschreibung)
```

Ein Lager an einem Knoten, fest in x, in y oder in beiden.

- `kennung: str = ''`
- `knoten: str = ''`
- `halt: Halt = Halt.XY`

### ScheibenlastEintrag

```python
@dataclass
class ScheibenlastEintrag(Beschreibung)
```

Eine Punktlast an einem Knoten, in jeder Richtung.

- `kennung: str = ''`
- `knoten: str = ''`
- `F_h: float = bereich(0.0, heisst='F_h', einheit=KN)` – Waagrecht, nach rechts positiv.
- `F_v: float = bereich(100.0, heisst='F_v', einheit=KN)` – Senkrecht, nach unten positiv.

### FachwerkmodellEintrag

```python
@dataclass
class FachwerkmodellEintrag(BauteilEintrag)
```

Ein Fachwerkmodell: eine Scheibe aus Umrissen und Löchern an Lagern,
mit Punktlasten. Ohne Regeln, die das ganze Projekt aufhielten: was
ihm fehlt, steht in seinen Meldungen, und die anderen Bauteile rechnen
weiter.

- `BEZEICHNUNG = 'Fachwerkmodell'`
- `STAMM = 'Fachwerkmodell'`
- `kennung: str`
- `name: str`
- `knoten: List[ScheibenknotenEintrag] = field(default_factory=list)`
- `scheiben: List[ScheibeEintrag] = field(default_factory=list)`
- `loecher: List[LochEintrag] = field(default_factory=list)`
- `lager: List[ScheibenlagerEintrag] = field(default_factory=list)`
- `lasten: List[ScheibenlastEintrag] = field(default_factory=list)`
- `beschreibung: str = ''` – Freier Text – geht in keine Rechnung ein.

#### FachwerkmodellEintrag.lagen

```python
def lagen(self) -> dict
```

Kennung -> `(x, y)` jedes Knotens, in m.

#### FachwerkmodellEintrag.netz

```python
def netz(self) -> Netz
```

#### FachwerkmodellEintrag.scheibe

```python
def scheibe(self, ecken: Sequence[Ort]) -> ScheibeEintrag
```

Ein Umriss der Scheibe mit diesen Ecken.

#### FachwerkmodellEintrag.loch

```python
def loch(self, ecken: Sequence[Ort]) -> LochEintrag
```

#### FachwerkmodellEintrag.lager_setzen

```python
def lager_setzen(self, ort: Ort, halt: str='xy') -> ScheibenlagerEintrag
```

Ein Lager bei `ort` – heisst nicht `lager`, weil die Liste so heisst.

#### FachwerkmodellEintrag.last

```python
def last(self, ort: Ort, **felder: Any) -> ScheibenlastEintrag
```

Eine Punktlast bei `ort` – `F_h` nach rechts, `F_v` nach unten, in kN.


## Konstanten

- `Ort = Union[str, Sequence[float]]` – Ein Ort im Baukasten: die Kennung eines Knotens oder `(x, y)` in m.
- `VORSILBEN = {'scheiben': 'S', 'loecher': 'L', 'lager': 'A', 'lasten': 'F'}` – Womit die Kennungen der Teile eines Fachwerkmodells beginnen – «A» wie Auflager.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.fachwerkmodell.modell]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.netz]]

## Gebraucht von

- [[opencivil.projekt]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.fachwerkmodell]]
- [[opencivil.projekt.projekt]]
- [[opencivil.web.fachwerkdaten]]
