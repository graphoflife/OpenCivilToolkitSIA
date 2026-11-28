---
erzeugt: 8feb9e2cccf1
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/mauerwerk.py
> eine Mauerwerkswand, wie die Oberfläche sie beschreibt.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/mauerwerk.py)

## VERANTWORTUNG

Der [[opencivil.projekt.mauerwerk#MauerwerkEintrag|MauerwerkEintrag]]: eine Wand in der Ansicht, gezeichnet aus
Knoten – ihr Umriss, Türen und Fenster mit dem Sturz darüber, ihre Linien-
und Punktlasten –, ihre Querlasten, dazu ihr Mauerwerk, ihre Dicke, wie sie
gemauert ist und
wie ihre Ränder gehalten sind, und ihre Lastfälle und Kombinationen wie in
der Decke ([[opencivil.projekt.faelle]]). Als speicherbare Datenklasse
wie das Fachwerkmodell ([[opencivil.projekt.fachwerkmodell]]), mit dem
Baukasten, der ohne Oberfläche zeichnet. Gerechnet wird in
[[opencivil.mauerwerk]].


## ALLES HÄNGT AN KNOTEN

Der Umriss der Wand und jede Öffnung sind Umrisse aus Knoten. Liegen zwei
Ecken genau aufeinander, teilen sie einen Knoten
([[opencivil.projekt.netz]]): wer ihn verschiebt, verschiebt beide.


## KOORDINATEN UND EINHEITEN

x nach rechts, y nach oben, in m – wie in der Decke. Die Dicke der Wand,
die Masse eines Sturzes und die Ausmitten in mm, wie man sie auf dem Plan
liest; Lasten in kN/m und kN, nach unten positiv, eine Punktlast auch
waagrecht in der Ebene der Wand, nach rechts positiv. Eine Ausmitte ist
positiv zur Seite, von der aus man die Ansicht sieht, ebenso eine Querlast
von Hand, in kN/m². Umgerechnet wird beim Bauen.

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

### WandlinienlastEintrag

```python
@dataclass
class WandlinienlastEintrag(Beschreibung)
```

Eine waagrechte Linienlast von Knoten zu Knoten, in einem Lastfall: eine Decke darauf.

- `kennung: str = ''`
- `lastfall: str = ''`
- `von: str = ''`
- `bis: str = ''`
- `wert: float = bereich(10.0, heisst='q', einheit=KN_PRO_M)`
- `e: float = bereich(0.0, heisst='Ausmitte e', einheit=MM)`

### WandpunktlastEintrag

```python
@dataclass
class WandpunktlastEintrag(Beschreibung)
```

Eine Einzellast an einem Knoten, in einem Lastfall – ein Träger, der
aufliegt, etwa, oder eine Decke, die die Wand waagrecht schiebt.

- `kennung: str = ''`
- `lastfall: str = ''`
- `knoten: str = ''`
- `wert: float = bereich(50.0, heisst='Q', einheit=KN)`
- `e: float = bereich(0.0, heisst='Ausmitte e', einheit=MM)`
- `H: float = bereich(0.0, heisst='H', einheit=KN)` – Waagrecht in der Ebene der Wand, nach rechts positiv.

### WandquerlastEintrag

```python
@dataclass
class WandquerlastEintrag(Beschreibung)
```

Eine Last quer zur Wand, gleichmässig über ihre ganze Ansicht, in einem
Lastfall: von Hand je m², etwa Wind, oder die Ersatzkraft des Erdbebens
– dann mit dem, was diese braucht.

- `kennung: str = ''`
- `lastfall: str = ''`
- `art: Querlastart = Querlastart.VON_HAND`
- `wert: float = bereich(1.0, heisst='Querlast p', einheit=KN_PRO_M2, zeichen='p')` – Von Hand: positiv zur Seite, von der aus man die Ansicht sieht.
- `zone: Erdbebenzone = Erdbebenzone.Z1B`
- `baugrund: Baugrundklasse = Baugrundklasse.C`
- `bauwerksklasse: Bauwerksklasse = Bauwerksklasse.I`
- `q: Verhaltensbeiwert = Verhaltensbeiwert.Q_15` – Mit welchem q das Gebäude im Erdbeben rechnet.
- `z_a: float = bereich(1.5, heisst='Höhe über dem Fundament z_a', einheit=M, ab=0.0,…` – Bis zur Mitte der Wand, wo die Ersatzkraft angreift.
- `h: float = bereich(3.0, heisst='Höhe des Gebäudes h', einheit=M, ueber=0.0, zeic…`

### MauerwerkEintrag

```python
@dataclass
class MauerwerkEintrag(MitFaellen, BauteilEintrag)
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
- `e_u: float = bereich(0.0, heisst='Ausmitte am Fuss e_u', einheit=MM)` – Nur bei gelenkigem Fuss.
- `knoten: List[WandknotenEintrag] = field(default_factory=list)`
- `waende: List[WandEintrag] = field(default_factory=list)`
- `oeffnungen: List[OeffnungEintrag] = field(default_factory=list)`
- `linienlasten: List[WandlinienlastEintrag] = field(default_factory=list)`
- `punktlasten: List[WandpunktlastEintrag] = field(default_factory=list)`
- `querlasten: List[WandquerlastEintrag] = field(default_factory=list)`
- `lastfaelle: List[LastfallEintrag] = field(default_factory=list)`
- `kombinationen: List[LastkombinationEintrag] = field(default_factory=list)`
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

#### MauerwerkEintrag.linienlast

```python
def linienlast(self, lastfall: Any, von: Ort, bis: Ort, **felder: Any) -> WandlinienlastEintrag
```

Eine waagrechte Linienlast im Lastfall `lastfall` (Eintrag oder
Kennung) – `wert` in kN/m und `e` in mm als Stichwort.

#### MauerwerkEintrag.punktlast

```python
def punktlast(self, lastfall: Any, ort: Ort, **felder: Any) -> WandpunktlastEintrag
```

Eine Punktlast im Lastfall `lastfall` – `wert` und `H` in kN,
`e` in mm als Stichwort.

#### MauerwerkEintrag.querlast

```python
def querlast(self, lastfall: Any, **felder: Any) -> WandquerlastEintrag
```

Eine Querlast im Lastfall `lastfall` – `art`, von Hand `wert`
in kN/m², aus dem Erdbeben `zone`, `baugrund`,
`bauwerksklasse`, `q`, `z_a` und `h` in m als Stichwort.

#### MauerwerkEintrag.neu

```python
@classmethod
def neu(cls, kennung: str, name: str) -> 'MauerwerkEintrag'
```

Eine frische Wand, wie der Benutzer sie angelegt bekommt: ohne
Zeichnung, mit den Lastfällen und Kombinationen einer frischen Decke –
das Eigengewicht kommt von selbst.

### rechteck

```python
def rechteck(x0: float, y0: float, x1: float, y1: float) -> List[Sequence[float]]
```

Die vier Ecken eines Rechtecks, wie die Werkzeuge «Wand» und «Öffnung» sie setzen.


## Konstanten

- `Ort = Union[str, Sequence[float]]` – Ein Ort im Baukasten: die Kennung eines Knotens oder `(x, y)` in m.
- `VORSILBEN = {'waende': 'W', 'oeffnungen': 'O', 'linienlasten': 'LL', 'punktlasten…` – Womit die Kennungen der Teile einer Wand beginnen – die Lasten wie in der Decke.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.erdbeben.ersatzkraft]]
- [[opencivil.mauerwerk.modell]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.faelle]]
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
