---
erzeugt: c34fdef6ab33
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/decke.py
> eine Stahlbetondecke, wie die Oberflaeche sie beschreibt.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/decke.py)

## VERANTWORTUNG

Der [[opencivil.projekt.decke#DeckeEintrag|DeckeEintrag]]: Platten, Linienlager, Stuetzen, versteckte
Unterzuege und Zonen der Lastaufteilung, gezeichnet aus Knoten im Grundriss
-- als speicherbare Datenklasse wie das Balkensystem
([[opencivil.projekt.balkensystem]]). Dazu der Baukasten, der ohne
Oberflaeche zeichnet. Gerechnet wird nach der Streifenmethode, in
[[opencivil.decke]].


## ALLES HAENGT AN KNOTEN

Eine Platte und eine Zone sind Umrisse aus Knoten, ein Linienlager und ein
Unterzug laufen von einem Knoten zum anderen, eine Stuetze steht an einem.
Wo zwei Platten oder eine Platte und eine Wand sich eine Ecke teilen,
teilen sie den Knoten -- wer ihn verschiebt, verschiebt sie beide, und es
entsteht keine Fuge, die niemand gezeichnet hat.


## KOORDINATEN UND EINHEITEN

x nach rechts, y nach oben, in m -- ebenso die Breite eines Unterzugs, der
Stuetzenbereich und die Streifenbreite. Die Dicke einer Platte und der
Querschnitt einer Stuetze in mm, Anteile in %, die Richtungen der Streifen
in Grad gegen x, im Gegenuhrzeigersinn. Umgerechnet wird beim Bauen.

## Inhalt

### DeckenknotenEintrag

```python
@dataclass
class DeckenknotenEintrag(Beschreibung)
```

Ein Punkt des Grundrisses, in m.

- `kennung: str = ''`
- `x: float = 0.0`
- `y: float = 0.0`

### DeckenplatteEintrag

```python
@dataclass
class DeckenplatteEintrag(Beschreibung)
```

Eine Platte: ihr Umriss, ihre Dicke und ihr Beton -- E_cm und die Dichte
des Stahlbetons von ihm, wie bei einem Stab des Balkensystems -- und die
zwei Richtungen, in denen ihre Streifen tragen.

- `kennung: str = ''`
- `knoten: List[str] = field(default_factory=list)`
- `h: float = bereich(240.0, heisst='Dicke h', einheit=MM, ueber=0.0)`
- `beton: str = ''` – Die Kennung des Betons im Projekt (`b1`).
- `richtung_1: float = bereich(0.0, heisst='Richtung 1', einheit=GRAD, ab=-180.0, bis=180.0)`
- `richtung_2: float = bereich(90.0, heisst='Richtung 2', einheit=GRAD, ab=-180.0, bis=180.0)`

### LinienlagerEintrag

```python
@dataclass
class LinienlagerEintrag(Beschreibung)
```

Ein Linienlager -- eine Wand, ein Rand auf einem Träger: vertikal
gehalten oder nicht, eingespannt oder nicht. Eingespannt ohne vertikalen
Halt hält es nur die Drehung, wie an einer Symmetrieachse.

- `kennung: str = ''`
- `von: str = ''`
- `bis: str = ''`
- `vertikal: bool = True`
- `eingespannt: bool = False`

### StuetzeEintrag

```python
@dataclass
class StuetzeEintrag(Beschreibung)
```

Eine Stütze unter der Decke, `b_x × b_y`. Die Streifen geben ihre
Last über den Stützenbereich `l_x × l_y` ab (Folie 39) -- von Hand
oder, ohne Angabe, so gross wie die Stütze oder der breiteste Unterzug
über ihr ([[opencivil.decke.streifen#stuetzenbereich|opencivil.decke.streifen.stuetzenbereich]]).

- `kennung: str = ''`
- `knoten: str = ''`
- `b_x: float = bereich(300.0, heisst='Breite b_x', einheit=MM, ueber=0.0)`
- `b_y: float = bereich(300.0, heisst='Breite b_y', einheit=MM, ueber=0.0)`
- `bereich_von_hand: bool = False`
- `l_x: float = bereich(1.0, heisst='Stützenbereich l_x', einheit=M, ueber=0.0)` – Nur mit `bereich_von_hand`.
- `l_y: float = bereich(1.0, heisst='Stützenbereich l_y', einheit=M, ueber=0.0)`

### UnterzugEintrag

```python
@dataclass
class UnterzugEintrag(Beschreibung)
```

Ein versteckter Unterzug, ein starker Streifen in der Platte (Folie 33):
so breit wie `breite`, liegend auf Linienlagern, Stützen und den
Unterzügen höherer `stufe`, die ihn kreuzen.

- `kennung: str = ''`
- `von: str = ''`
- `bis: str = ''`
- `breite: float = bereich(1.0, heisst='Breite b', einheit=M, ueber=0.0)`
- `stufe: int = bereich(1, heisst='Stufe', ab=1)`

### ZoneEintrag

```python
@dataclass
class ZoneEintrag(Beschreibung)
```

Eine Zone der Lastaufteilung: in ihrem Umriss geht `anteil` der Last
in die Richtung 1 der Platte, der Rest in die Richtung 2 -- statt der
Aufteilung der Decke.

- `kennung: str = ''`
- `knoten: List[str] = field(default_factory=list)`
- `anteil: float = bereich(50.0, heisst='Anteil in Richtung 1', einheit=PROZENT, ab=0.0,…`

### DeckeEintrag

```python
@dataclass
class DeckeEintrag(BauteilEintrag)
```

Eine Decke aus Platten auf Linienlagern und Stützen, mit versteckten
Unterzügen und Zonen. Wie die Last aufgeteilt wird, gilt für die ganze
Decke: automatisch nach Folie 31 oder `anteil` in die Richtung 1 --
in einer Zone deren Anteil.

Ohne Regeln, die das ganze Projekt aufhielten: was an einer Decke nicht
stimmt, steht in ihren Meldungen, und die anderen Bauteile rechnen weiter.

- `BEZEICHNUNG = 'Decke'`
- `kennung: str`
- `name: str`
- `knoten: List[DeckenknotenEintrag] = field(default_factory=list)`
- `platten: List[DeckenplatteEintrag] = field(default_factory=list)`
- `linienlager: List[LinienlagerEintrag] = field(default_factory=list)`
- `stuetzen: List[StuetzeEintrag] = field(default_factory=list)`
- `unterzuege: List[UnterzugEintrag] = field(default_factory=list)`
- `zonen: List[ZoneEintrag] = field(default_factory=list)`
- `streifenbreite: float = bereich(0.25, heisst='Streifenbreite', einheit=M, ueber=0.0)`
- `aufteilung: Aufteilung = Aufteilung.AUTOMATISCH`
- `anteil: float = bereich(50.0, heisst='Anteil in Richtung 1', einheit=PROZENT, ab=0.0,…` – Nur bei fester Aufteilung.
- `beschreibung: str = ''` – Freier Text -- geht in keine Rechnung ein.

#### DeckeEintrag.materialien

```python
def materialien(self) -> List[str]
```

Jeder Beton des Projekts, auf den eine Platte zeigt -- jeder einmal.

#### DeckeEintrag.lagen

```python
def lagen(self) -> dict
```

Kennung -> `(x, y)` jedes Knotens, in m.

#### DeckeEintrag.netz

```python
def netz(self) -> Netz
```

#### DeckeEintrag.platte

```python
def platte(self, ecken: Sequence[Ort], *, beton: Any, **felder: Any) -> DeckenplatteEintrag
```

Eine Platte mit diesen Ecken und dem Beton `beton` (Eintrag oder Kennung).

#### DeckeEintrag.lager

```python
def lager(self, von: Ort, bis: Ort, **felder: Any) -> LinienlagerEintrag
```

Ein Linienlager von `von` nach `bis` -- heisst so, weil die Liste `linienlager` heisst.

#### DeckeEintrag.stuetze

```python
def stuetze(self, ort: Ort, **felder: Any) -> StuetzeEintrag
```

#### DeckeEintrag.unterzug

```python
def unterzug(self, von: Ort, bis: Ort, **felder: Any) -> UnterzugEintrag
```

#### DeckeEintrag.zone

```python
def zone(self, ecken: Sequence[Ort], **felder: Any) -> ZoneEintrag
```

#### DeckeEintrag.neu

```python
@classmethod
def neu(cls, kennung: str, name: str) -> 'DeckeEintrag'
```

Eine leere Decke, wie der Benutzer sie angelegt bekommt.


## Konstanten

- `Ort = Union[str, Sequence[float]]` – Ein Ort im Baukasten: die Kennung eines Knotens oder `(x, y)` in m.
- `VORSILBEN = {'platten': 'P', 'linienlager': 'L', 'stuetzen': 'S', 'unterzuege': '…` – Womit die Kennungen der Teile einer Decke beginnen.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.decke.modell]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.netz]]

## Gebraucht von

- [[opencivil.projekt]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.decke]]
- [[opencivil.projekt.projekt]]
- [[opencivil.web.api]]
