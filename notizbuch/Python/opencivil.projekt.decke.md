---
erzeugt: f0c2613b98be
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/decke.py
> eine Stahlbetondecke, wie die Oberflaeche sie beschreibt.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/decke.py)

## VERANTWORTUNG

Der [[opencivil.projekt.decke#DeckeEintrag|DeckeEintrag]]: Platten, Linienlager, Stuetzen, Traeger – ein
Unterzug oder ein Ueberzug – und Zonen der Lastaufteilung, gezeichnet aus
Knoten im Grundriss – als speicherbare Datenklasse wie das Balkensystem
([[opencivil.projekt.balkensystem]]). Dazu der Baukasten, der ohne
Oberflaeche zeichnet. Gerechnet wird nach der Streifenmethode, in
[[opencivil.decke]].


## ALLES HAENGT AN KNOTEN

Eine Platte und eine Zone sind Umrisse aus Knoten, ein Linienlager und ein
Traeger laufen von einem Knoten zum anderen, eine Stuetze steht an einem.
Wo zwei Platten oder eine Platte und eine Wand sich eine Ecke teilen,
teilen sie den Knoten – wer ihn verschiebt, verschiebt sie beide, und es
entsteht keine Fuge, die niemand gezeichnet hat.


## LASTEN

Jede Last gehoert zu einem Lastfall ([[opencivil.projekt.faelle]], wie
im Balkensystem). Eine Flaechenlast ist gezeichnet – ein Umriss aus
Knoten – oder liegt auf der ganzen Platte: dann steht sie an der Platte
(`lasten`) und geht mit ihr, wenn sie kopiert oder geloescht wird. Eine
Linienlast laeuft von Knoten zu Knoten, eine Punktlast steht an einem und
verteilt sich ueber `l_x × l_y`. Nach unten positiv.


## ERGEBNISBILDER

Welche Bilder rechts stehen, sagt die Liste `diagramme` – wie die
Statik-Analyse des Balkensystems je Zeile ein Fall und eine Groesse. Eine
frische Decke hat m_x, m_y, v_0 und die Lagerkraefte der GZT. Ein Bild
zeigt die ganze Platte oder einen Schnitt: eine Linie von Knoten zu
Knoten, laengs der die Groesse wie an einem Balken steht, mit den Lagern,
die sie kreuzt (Benutzer, 2026-11-16). Ein Schnitt geht in keine Rechnung
ein.


## KOORDINATEN UND EINHEITEN

x nach rechts, y nach oben, in m – ebenso die Breite eines Traegers, der
Stuetzenbereich und die Streifenbreite. Die Dicke einer Platte und der
Querschnitt einer Stuetze in mm, Anteile in %, die Richtungen der Streifen
in Grad gegen x, im Gegenuhrzeigersinn. Lasten in kN/m², kN/m und kN.
Umgerechnet wird beim Bauen.

## Inhalt

### DeckenknotenEintrag

```python
@dataclass
class DeckenknotenEintrag(Beschreibung)
```

Ein Punkt des Grundrisses, in m.

- `kennung: str = ''`
- `x: float = bereich(0.0, heisst='x', einheit=M)`
- `y: float = bereich(0.0, heisst='y', einheit=M)`

### PlattenlastEintrag

```python
@dataclass
class PlattenlastEintrag(Beschreibung)
```

Eine Flaechenlast auf der ganzen Platte, an der sie steht, in einem Lastfall.

- `IM_ORT = 'Last'`
- `lastfall: str = ''`
- `wert: float = bereich(2.0, heisst='q', einheit=KN_PRO_M2)`

### DeckenplatteEintrag

```python
@dataclass
class DeckenplatteEintrag(Beschreibung)
```

Eine Platte: ihr Umriss, ihre Dicke und ihr Beton – E_cm und die Dichte
des Stahlbetons von ihm, wie bei einem Stab des Balkensystems – und die
zwei Richtungen, in denen ihre Streifen tragen: von selbst entlang ihrer
Ränder ([[opencivil.decke.richtungen]]) oder von Hand. Von Hand liegen
sie mindestens 5° auseinander, sonst trügen sie kaum anders als eine –
das weist schon das Feld ab.

- `kennung: str = ''`
- `knoten: List[str] = field(default_factory=list)`
- `h: float = bereich(240.0, heisst='Dicke h', einheit=MM, ueber=0.0)`
- `beton: str = ''` – Die Kennung des Betons im Projekt (`b1`).
- `richtungen_von_hand: bool = False`
- `richtung_1: float = bereich(0.0, heisst='Richtung 1', einheit=GRAD, ab=-180.0, bis=180.0)` – Nur mit `richtungen_von_hand`, wie `richtung_2`.
- `richtung_2: float = bereich(90.0, heisst='Richtung 2', einheit=GRAD, ab=-180.0, bis=180.0…`
- `lasten: List[PlattenlastEintrag] = field(default_factory=list)`

#### DeckenplatteEintrag.ergaenzt

```python
@classmethod
def ergaenzt(cls, roh: Mapping[str, Any], basis: Optional[DeckenplatteEintrag]) -> Mapping[str, Any]
```

`roh` mit `richtungen_von_hand`, wo es fehlt, aber ein Winkel
dasteht – in einer Datei von vor dem 2026-11-26 stehen beide: mit
0° und 90°, der Vorgabe von damals, wählt die Platte ihre Richtungen
nun selbst, mit anderen Winkeln bleiben es die des Benutzers. Ebenso,
wer ohne Maske schreibt: wer einen anderen Winkel angibt, meint ihn.

### LinienlagerEintrag

```python
@dataclass
class LinienlagerEintrag(Beschreibung)
```

Ein Linienlager – eine Wand, ein Rand auf einem Träger: vertikal
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
Last über den Stützenbereich `l_x × l_y` ab (Folie 39) – von Hand
oder, ohne Angabe, so gross wie die Stütze oder der breiteste Träger
über ihr ([[opencivil.decke.streifen#stuetzenbereich|opencivil.decke.streifen.stuetzenbereich]]).

- `kennung: str = ''`
- `knoten: str = ''`
- `b_x: float = bereich(300.0, heisst='Breite b_x', einheit=MM, ueber=0.0)`
- `b_y: float = bereich(300.0, heisst='Breite b_y', einheit=MM, ueber=0.0)`
- `bereich_von_hand: bool = False`
- `l_x: float = bereich(1.0, heisst='Stützenbereich l_x', einheit=M, ueber=0.0)` – Nur mit `bereich_von_hand`.
- `l_y: float = bereich(1.0, heisst='Stützenbereich l_y', einheit=M, ueber=0.0)`

### TraegerEintrag

```python
@dataclass
class TraegerEintrag(Beschreibung)
```

Ein Träger, ein Unterzug oder ein Überzug: in der Streifenmethode ein
starker Streifen in der Platte (Folie 33), so breit wie `breite`,
liegend auf Linienlagern, Stützen und den Trägern höherer `stufe`,
die ihn kreuzen.

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
in die Richtung 1 der Platte, der Rest in die Richtung 2 – statt der
Aufteilung der Decke.

- `kennung: str = ''`
- `knoten: List[str] = field(default_factory=list)`
- `anteil: float = bereich(50.0, heisst='Anteil in Richtung 1', einheit=PROZENT, ab=0.0,…`

### FlaechenlastEintrag

```python
@dataclass
class FlaechenlastEintrag(Beschreibung)
```

Eine gleichmaessige Flaechenlast auf einem gezeichneten Umriss, in einem Lastfall.

- `kennung: str = ''`
- `lastfall: str = ''`
- `knoten: List[str] = field(default_factory=list)`
- `wert: float = bereich(2.0, heisst='q', einheit=KN_PRO_M2)`

### LinienlastEintrag

```python
@dataclass
class LinienlastEintrag(Beschreibung)
```

Eine gleichmaessige Linienlast von Knoten zu Knoten, in einem Lastfall – eine Wand darauf etwa.

- `kennung: str = ''`
- `lastfall: str = ''`
- `von: str = ''`
- `bis: str = ''`
- `wert: float = bereich(10.0, heisst='q', einheit=KN_PRO_M)`

### PunktlastEintrag

```python
@dataclass
class PunktlastEintrag(Beschreibung)
```

Eine Einzellast an einem Knoten, in einem Lastfall. Die Streifen tragen
sie gleichmaessig verteilt ueber `l_x × l_y` (nach Vorgabe; die Norm
sagt nichts dazu, und SIA 261:2020, Tabelle 8 stellt die Last selbst auf
50 × 50 mm); was das die Platte darueber hinaus kostet, sagt das
Lastverteilelement.

- `kennung: str = ''`
- `lastfall: str = ''`
- `knoten: str = ''`
- `wert: float = bereich(50.0, heisst='Q', einheit=KN)`
- `l_x: float = bereich(VERTEILBREITE, heisst='Verteilbreite l_x', einheit=M, ueber=0…`
- `l_y: float = bereich(VERTEILBREITE, heisst='Verteilbreite l_y', einheit=M, ueber=0…`

### DeckenschnittEintrag

```python
@dataclass
class DeckenschnittEintrag(Beschreibung)
```

Ein Schnitt von Knoten zu Knoten: längs ihm zeigt ein Ergebnisbild eine
Schnittkraft wie an einem Balken, mit den Lagern, die er kreuzt
([[opencivil.decke.schnitt]]). Er geht in keine Rechnung ein.

- `kennung: str = ''`
- `von: str = ''`
- `bis: str = ''`

### DeckendiagrammEintrag

```python
@dataclass
class DeckendiagrammEintrag(Beschreibung)
```

Ein Ergebnisbild der Decke: ein Fall und was es von ihm zeigt – über
die ganze Platte, längs eines Schnitts oder in einem Träger, dort M
und V über seine ganze Breite. Gerechnet wird damit nichts
– die Decke rechnet jeden Fall; die Liste sagt nur, welche Bilder
rechts stehen.

- `IM_ORT = 'Diagramm'`
- `fall: str = ''` – Die Kennung eines Lastfalls (`LF1`) oder einer Kombination (`LK1`).
- `groesse: str = einer_von(DIAGRAMMGROESSEN, 'm_x')`
- `schnitt: str = ''` – Wo das Bild schneidet: die Kennung eines Schnitts (`SN1`) oder eines Trägers (`T1`) – leer: die ganze Platte. Die Lagerkräfte zeigen immer die ganze; M und V gibt es nur in einem Träger, die Grössen der Platte nur ausserhalb. Der Name blieb, als der Träger dazukam: ein neuer machte heute gespeicherte Stände unlesbar.

### DeckeEintrag

```python
@dataclass
class DeckeEintrag(MitFaellen, BauteilEintrag)
```

Eine Decke aus Platten auf Linienlagern und Stützen, mit Trägern und
Zonen, und ihren Lasten, Lastfällen und Kombinationen.
Wie die Last aufgeteilt wird, gilt für die ganze Decke: automatisch
nach Folie 31 oder `anteil` in die Richtung 1 – in einer Zone deren
Anteil.

Ohne Regeln, die das ganze Projekt aufhielten: was an einer Decke nicht
stimmt, steht in ihren Meldungen, und die anderen Bauteile rechnen weiter.

- `BEZEICHNUNG = 'Decke'`
- `STAMM = 'Decke'`
- `kennung: str`
- `name: str`
- `knoten: List[DeckenknotenEintrag] = field(default_factory=list)`
- `platten: List[DeckenplatteEintrag] = field(default_factory=list)`
- `linienlager: List[LinienlagerEintrag] = field(default_factory=list)`
- `stuetzen: List[StuetzeEintrag] = field(default_factory=list)`
- `traeger: List[TraegerEintrag] = field(default_factory=list)`
- `zonen: List[ZoneEintrag] = field(default_factory=list)`
- `flaechenlasten: List[FlaechenlastEintrag] = field(default_factory=list)`
- `linienlasten: List[LinienlastEintrag] = field(default_factory=list)`
- `punktlasten: List[PunktlastEintrag] = field(default_factory=list)`
- `schnitte: List[DeckenschnittEintrag] = field(default_factory=list)`
- `lastfaelle: List[LastfallEintrag] = field(default_factory=list)`
- `kombinationen: List[LastkombinationEintrag] = field(default_factory=list)`
- `diagramme: List[DeckendiagrammEintrag] = field(default_factory=list)`
- `streifenbreite: float = bereich(0.25, heisst='Streifenbreite', einheit=M, ueber=0.0)`
- `aufteilung: Aufteilung = Aufteilung.AUTOMATISCH`
- `anteil: float = bereich(50.0, heisst='Anteil in Richtung 1', einheit=PROZENT, ab=0.0,…` – Nur bei fester Aufteilung.
- `bandbreite: float = bereich(BANDBREITE, heisst='Breite der Bänder', einheit=M, ueber=0.0)` – Nur bei automatischer Aufteilung ([[opencivil.decke.baender|baender]]).
- `beschreibung: str = ''` – Freier Text – geht in keine Rechnung ein.

#### DeckeEintrag.materialien

```python
def materialien(self) -> List[str]
```

Jeder Beton des Projekts, auf den eine Platte zeigt – jeder einmal.

#### DeckeEintrag.lagen

```python
def lagen(self) -> dict
```

Kennung -> `(x, y)` jedes Knotens, in m.

#### DeckeEintrag.schnittlinien

```python
def schnittlinien(self) -> List[Tuple[str, Punkt, Punkt]]
```

Je Schnitt seine Kennung und seine Enden, in m – einer, dem ein Knoten fehlt, nicht.

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

Ein Linienlager von `von` nach `bis` – heisst so, weil die Liste `linienlager` heisst.

#### DeckeEintrag.stuetze

```python
def stuetze(self, ort: Ort, **felder: Any) -> StuetzeEintrag
```

#### DeckeEintrag.traeger_legen

```python
def traeger_legen(self, von: Ort, bis: Ort, **felder: Any) -> TraegerEintrag
```

Ein Träger von `von` nach `bis` – heisst nicht `traeger`, weil die Liste so heisst.

#### DeckeEintrag.zone

```python
def zone(self, ecken: Sequence[Ort], **felder: Any) -> ZoneEintrag
```

#### DeckeEintrag.flaechenlast

```python
def flaechenlast(self, lastfall: Any, ecken: Sequence[Ort], **felder: Any) -> FlaechenlastEintrag
```

Eine Flächenlast auf diesem Umriss im Lastfall `lastfall` (Eintrag oder Kennung).

#### DeckeEintrag.linienlast

```python
def linienlast(self, lastfall: Any, von: Ort, bis: Ort, **felder: Any) -> LinienlastEintrag
```

#### DeckeEintrag.punktlast

```python
def punktlast(self, lastfall: Any, ort: Ort, **felder: Any) -> PunktlastEintrag
```

#### DeckeEintrag.schnitt

```python
def schnitt(self, von: Ort, bis: Ort) -> DeckenschnittEintrag
```

Ein Schnitt von `von` nach `bis` – längs ihm zeigt ein Ergebnisbild eine Schnittkraft.

#### DeckeEintrag.plattenlast

```python
def plattenlast(self, lastfall: Any, platte: Any, wert: float) -> PlattenlastEintrag
```

Die Flächenlast auf der ganzen Platte `platte` (Eintrag oder
Kennung) im Lastfall `lastfall`, in kN/m² – je Platte und Lastfall
eine, wie in der Oberfläche: eine zweite ersetzt die erste.

#### DeckeEintrag.diagramm

```python
def diagramm(self, fall: Any, groesse: str='m_x', schnitt: Any='') -> DeckendiagrammEintrag
```

Ein Ergebnisbild – `fall` ein Lastfall oder eine Kombination,
`schnitt` einer der Schnitte oder Träger (Eintrag oder
Kennung), ohne ihn die ganze Platte.

#### DeckeEintrag.neu

```python
@classmethod
def neu(cls, kennung: str, name: str) -> 'DeckeEintrag'
```

Eine frische Decke, wie der Benutzer sie angelegt bekommt: ohne
Platte, aber mit den Lastfällen eines frischen Balkensystems – das
Eigengewicht kommt von selbst – und nur den Kombinationen der
Tragsicherheit, GZT und «GZT günstig», ohne GZG: die Streifenmethode
gilt für die Tragsicherheit (Benutzer, 2026-11-14). Dazu die Bilder
m_x, m_y, v_0 und die Lagerkräfte der GZT.


## Konstanten

- `Ort = Union[str, Sequence[float]]` – Ein Ort im Baukasten: die Kennung eines Knotens oder `(x, y)` in m.
- `PLATTENGROESSEN = (*GROESSEN, 'lager')` – Was ein Ergebnisbild zeigt: eine Schnittkraft der Platte, die Lagerkraefte – oder Moment und Querkraft eines ganzen Trägers.
- `DIAGRAMMGROESSEN = (*PLATTENGROESSEN, *BALKENGROESSEN)`
- `VORSILBEN = {'platten': 'P', 'linienlager': 'L', 'stuetzen': 'S', 'traeger': 'T',…` – Womit die Kennungen der Teile einer Decke beginnen.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.decke.feld]]
- [[opencivil.decke.geometrie]]
- [[opencivil.decke.modell]]
- [[opencivil.decke.schnitt]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.faelle]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.netz]]

## Gebraucht von

- [[opencivil.projekt]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.decke]]
- [[opencivil.projekt.beispiele]]
- [[opencivil.projekt.projekt]]
- [[opencivil.web.api]]
