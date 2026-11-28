---
erzeugt: 04969b5fcc7e
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


## DAS GEFUNDENE FACHWERK

Was die Suche zuletzt fand, steht im Eintrag ([[opencivil.projekt.fachwerkmodell#GefundenesFachwerk|GefundenesFachwerk]]):
die Seite fragt sie Runde um Runde an und legt hier ab, was die letzte
gab – fertig oder angehalten. Geschrieben vom Kern, nicht von Hand; die
Rechnung glaubt ihm nur, was sie nicht nachrechnen kann, und erkennt am
Abdruck, ob es noch zu Modell und Verfahren gehört
([[opencivil.fachwerkmodell.suche]]).

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

### FachwerkpunktEintrag

```python
@dataclass
class FachwerkpunktEintrag(Beschreibung)
```

Ein Knoten des gefundenen Fachwerks, in m.

- `IM_ORT = 'Knoten des Fachwerks'`
- `x: float = bereich(0.0, heisst='x', einheit=M)`
- `y: float = bereich(0.0, heisst='y', einheit=M)`

### FachwerkstabEintrag

```python
@dataclass
class FachwerkstabEintrag(Beschreibung)
```

Ein Stab des gefundenen Fachwerks: von Knoten zu Knoten, gezählt ab null, mit seiner Kraft.

- `IM_ORT = 'Stab des Fachwerks'`
- `von: int = bereich(0, heisst='von', ab=0)`
- `bis: int = bereich(0, heisst='bis', ab=0)`
- `N: float = bereich(0.0, heisst='N', einheit=KN)` – Zug positiv.

### GefundenesFachwerk

```python
@dataclass
class GefundenesFachwerk(Beschreibung)
```

Was die Suche zuletzt fand – siehe Dateikopf.

- `abdruck: str = ''` – Woran es Modell und Verfahren erkennt, zu denen es gehört.
- `runden: int = bereich(0, heisst='Runden', ab=0)`
- `fertig: bool = False` – Ob die Suche zu Ende kam – sonst wurde sie angehalten.
- `moeglich: int = bereich(0, heisst='Mögliche Stäbe', ab=0)` – Wie viele Stäbe die Grundstruktur hatte.
- `im_modell: int = bereich(0, heisst='Stäbe im Modell', ab=0)` – Wie viele davon in der letzten Runde im Modell waren.
- `knoten: List[FachwerkpunktEintrag] = field(default_factory=list)`
- `staebe: List[FachwerkstabEintrag] = field(default_factory=list)`

#### GefundenesFachwerk.aus

```python
@classmethod
def aus(cls, ergebnis: Suchergebnis) -> 'GefundenesFachwerk'
```

Das Ergebnis einer Runde, wie es im Projekt steht: Kräfte in kN.

#### GefundenesFachwerk.ergebnis

```python
def ergebnis(self) -> Optional[Suchergebnis]
```

Zurück in SI – `None`, wenn ein Stab auf einen Knoten zeigt, den es
nicht gibt: dann ist es keines, das die Suche schrieb.

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
- `rasterweite: float = bereich(0.5, heisst='Rasterweite', einheit=M, ueber=0.0)` – Wie weit die Knoten der Grundstruktur auseinander liegen.
- `w_Z: float = bereich(1.0, heisst='w_Z', ab=0.1, bis=10.0)` – Wie schwer Zug gegenüber Druck zählt – 1: gleich (Plan vom 2026-11-27, Entscheid 11).
- `N_min: float = bereich(1.0, heisst='N_min', einheit=PROZENT, ab=0.0, bis=50.0)` – Die kleinste Stabkraft, die stehen bleibt, bezogen auf die grösste.
- `zug_achsparallel: bool = False` – Ob nur waagrechte und senkrechte Stäbe Zug tragen – geneigte dann nur Druck ([[opencivil.fachwerkmodell.suche#Konstanten|ZUG_ACHSPARALLEL]]).
- `fachwerk: Optional[GefundenesFachwerk] = teil(lambda: None, heisst='Gefundenes Fachwerk')` – Was die Suche zuletzt fand – siehe Dateikopf.
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

#### FachwerkmodellEintrag.suchen

```python
def suchen(self) -> GefundenesFachwerk
```

Sucht das Fachwerk bis zum Ende, wie «Fachwerk suchen» auf der Seite,
und legt es ab. Fehlt dem Modell etwas, sagt ein [[opencivil.projekt.lesen#ProjektFehler|ProjektFehler]],
was; ein zu feines Raster meldet
[[opencivil.fachwerkmodell.grundstruktur#ZuVieleKnoten|ZuVieleKnoten]].


## Konstanten

- `Ort = Union[str, Sequence[float]]` – Ein Ort im Baukasten: die Kennung eines Knotens oder `(x, y)` in m.
- `VORSILBEN = {'scheiben': 'S', 'loecher': 'L', 'lager': 'A', 'lasten': 'F'}` – Womit die Kennungen der Teile eines Fachwerkmodells beginnen – «A» wie Auflager.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.fachwerkmodell.modell]]
- [[opencivil.fachwerkmodell.pruefen]]
- [[opencivil.fachwerkmodell.suche]]
- [[opencivil.projekt.aufbau.fachwerkmodell]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.netz]]

## Gebraucht von

- [[opencivil.projekt]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.fachwerkmodell]]
- [[opencivil.projekt.beispiele]]
- [[opencivil.projekt.projekt]]
- [[opencivil.web.api]]
- [[opencivil.web.fachwerkdaten]]
