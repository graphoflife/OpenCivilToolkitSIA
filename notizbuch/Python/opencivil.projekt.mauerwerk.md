---
erzeugt: f8a1f0dd77be
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/mauerwerk.py
> eine Mauerwerkswand, wie die Oberfläche sie beschreibt.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/mauerwerk.py)

## VERANTWORTUNG

Der [[opencivil.projekt.mauerwerk#MauerwerkEintrag|MauerwerkEintrag]]: eine Wand in der Ansicht, gezeichnet aus
Knoten – ihr Umriss, Türen und Fenster mit dem Sturz darüber –, dazu ihr
Mauerwerk, ihre Dicke, wie sie gemauert ist und wie ihre Ränder gehalten
sind. Als speicherbare Datenklasse wie das Fachwerkmodell
([[opencivil.projekt.fachwerkmodell]]), mit dem Baukasten, der ohne
Oberfläche zeichnet. Gerechnet wird in [[opencivil.mauerwerk]].


## ALLES HÄNGT AN KNOTEN

Der Umriss der Wand und jede Öffnung sind Umrisse aus Knoten. Liegen zwei
Ecken genau aufeinander, teilen sie einen Knoten
([[opencivil.projekt.netz]]): wer ihn verschiebt, verschiebt beide.


## KOORDINATEN UND EINHEITEN

x nach rechts, y nach oben, in m – wie in der Decke. Die Dicke der Wand
und die Masse eines Sturzes in mm, wie man sie auf dem Plan liest.
Umgerechnet wird beim Bauen.

## Inhalt

### WandknotenEintrag

```python
@dataclass
class WandknotenEintrag(Beschreibung)
```

Ein Punkt der Wand, in m.

- `kennung: str = ''`
- `x: float = bereich(0.0, heisst='x', einheit=M)`
- `y: float = bereich(0.0, heisst='y', einheit=M)`

### WandEintrag

```python
@dataclass
class WandEintrag(Beschreibung)
```

Der Umriss der Wand in der Ansicht.

- `kennung: str = ''`
- `knoten: List[str] = field(default_factory=list)`

### OeffnungEintrag

```python
@dataclass
class OeffnungEintrag(Beschreibung)
```

Eine Türe oder ein Fenster, mit dem Sturz darüber.

- `kennung: str = ''`
- `knoten: List[str] = field(default_factory=list)`
- `sturz: Sturzart = Sturzart.BETON`
- `h_St: float = bereich(200.0, heisst='Sturzhöhe h_St', einheit=MM, ueber=0.0)`
- `a: float = bereich(150.0, heisst='Auflagerlänge a', einheit=MM, ueber=0.0)` – Wie weit der Sturz auf jeder Seite auf dem Mauerwerk liegt.

### MauerwerkEintrag

```python
@dataclass
class MauerwerkEintrag(BauteilEintrag)
```

Eine Wand aus Mauerwerk. Ohne Regeln, die das ganze Projekt aufhielten:
was ihrer Zeichnung fehlt, steht in ihren Meldungen, und die anderen
Bauteile rechnen weiter.

- `BEZEICHNUNG = 'Mauerwerk'`
- `STAMM = 'Wand'`
- `ERSTE_MATERIALIEN = {'material': 'mauerwerk'}`
- `kennung: str`
- `name: str`
- `material: str = materialfeld('mauerwerk')`
- `t: float = bereich(150.0, heisst='Dicke t_w', einheit=MM, ueber=0.0)`
- `mauerung: Mauerung = Mauerung.EINSTEIN`
- `stossfugen: Stossfugen = Stossfugen.NICHT_VOLLFUGIG`
- `kopf: Halterung = Halterung.GELENKIG`
- `fuss: Halterung = Halterung.GELENKIG`
- `links: Seitenrand = Seitenrand.FREI`
- `rechts: Seitenrand = Seitenrand.FREI`
- `knoten: List[WandknotenEintrag] = field(default_factory=list)`
- `waende: List[WandEintrag] = field(default_factory=list)`
- `oeffnungen: List[OeffnungEintrag] = field(default_factory=list)`
- `beschreibung: str = ''` – Freier Text – geht in keine Rechnung ein.

#### MauerwerkEintrag.materialien

```python
def materialien(self) -> List[str]
```

#### MauerwerkEintrag.lagen

```python
def lagen(self) -> dict
```

Kennung -> `(x, y)` jedes Knotens, in m.

#### MauerwerkEintrag.netz

```python
def netz(self) -> Netz
```

#### MauerwerkEintrag.wand

```python
def wand(self, ecken: Sequence[Ort]) -> WandEintrag
```

Der Umriss der Wand mit diesen Ecken.

#### MauerwerkEintrag.oeffnung

```python
def oeffnung(self, ecken: Sequence[Ort], **felder: Any) -> OeffnungEintrag
```

Eine Öffnung mit diesen Ecken – `sturz`, `h_St` und `a` in mm als Stichwort.

### rechteck

```python
def rechteck(x0: float, y0: float, x1: float, y1: float) -> List[Sequence[float]]
```

Die vier Ecken eines Rechtecks, wie die Werkzeuge «Wand» und «Öffnung» sie setzen.


## Konstanten

- `Ort = Union[str, Sequence[float]]` – Ein Ort im Baukasten: die Kennung eines Knotens oder `(x, y)` in m.
- `VORSILBEN = {'waende': 'W', 'oeffnungen': 'O'}` – Womit die Kennungen der Teile einer Wand beginnen.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.mauerwerk.modell]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.netz]]

## Gebraucht von

- [[opencivil.projekt]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.mauerwerk]]
- [[opencivil.projekt.beispiele]]
- [[opencivil.projekt.projekt]]
- [[opencivil.web.api]]
- [[opencivil.web.mauerwerkdaten]]
