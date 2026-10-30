---
erzeugt: 4793c9a6a29b
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/durchstanzen.py
> ein Durchstanznachweis, wie die Oberflaeche ihn beschreibt.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/durchstanzen.py)

## VERANTWORTUNG

Der [[opencivil.projekt.durchstanzen#DurchstanzEintrag|DurchstanzEintrag]]: Decke oder Bodenplatte, Plattendicke,
Überdeckung, Grösstkorn, die Biegebewehrung über der Stütze, Form, Masse und
Lage der gestützten Fläche, die Spannweiten für die Plattenrotation, die
Einwirkung und die Aussparungen -- als speicherbare Datenklasse. Gerechnet
wird in [[opencivil.durchstanzen]].


## KNOTEN UND AUSSPARUNGEN

Wie im gezeichneten Querschnitt tragen die Aussparungen keine eigenen
Koordinaten, sie verweisen auf Knoten ([[opencivil.projekt.durchstanzen#GrundrissknotenEintrag|GrundrissknotenEintrag]]). Im
Grundriss, in mm, mit der Achse der Stütze im Ursprung: x nach rechts, y
nach oben. Der Plattenrand einer Randstütze liegt unten, an der Ecke dazu
links ([[opencivil.durchstanzen.stelle]]).


## DIE VORGABEN

Eine neue Stelle bringt keine Einwirkung mit, wie ein neuer Lastfall
(Benutzer, 2026-10-19). Platte, Bewehrung und Stütze sind gesetzt, damit
sich gleich etwas rechnen lässt: 280 mm Decke, ⌀16 @ 150 in beiden
Richtungen, Stütze 300 × 300 mm, Spannweiten 7 m -- nicht vom Benutzer.

## Inhalt

### GrundrissknotenEintrag

```python
@dataclass
class GrundrissknotenEintrag(Beschreibung)
```

Ein Knoten im Grundriss, in mm, die Achse der Stütze im Ursprung.

- `kennung: str = ''`
- `x: float = 0.0`
- `y: float = 0.0`

### AussparungEintrag

```python
@dataclass
class AussparungEintrag(Beschreibung)
```

Eine Aussparung in der Platte: ihre Ecken als Kennungen von Knoten, der Reihe nach.

- `kennung: str = ''`
- `knoten: List[str] = field(default_factory=list)`

### DurchstanzEintrag

```python
@dataclass
class DurchstanzEintrag(Beschreibung)
```

Eine Durchstanzstelle -- siehe Dateikopf.

- `BEZEICHNUNG = 'Durchstanzen'`
- `kennung: str`
- `name: str`
- `plattenart: Plattenart = Plattenart.DECKE` – Decke: Zugbewehrung oben; Bodenplatte: unten, gegen die Bodenpressung.
- `beton: str = ''` – Kennung des Betons.
- `stahl: str = ''` – Kennung des Betonstahls der Biegebewehrung.
- `h: float = bereich(280.0, heisst='Plattendicke h', einheit=MM, ueber=0.0)`
- `c: float = bereich(30.0, heisst='Überdeckung c_nom', einheit=MM, ab=0.0)` – Die Überdeckung auf der Zugseite: oben bei der Decke, unten bei der Bodenplatte.
- `D_max: float = bereich(32.0, heisst='Grösstkorn D_max', einheit=MM, ueber=0.0)`
- `phi_x: float = bereich(16.0, heisst='Stabdurchmesser ⌀_x', einheit=MM, ueber=0.0)`
- `s_x: float = bereich(150.0, heisst='Stababstand s_x', einheit=MM, ueber=0.0)`
- `phi_y: float = bereich(16.0, heisst='Stabdurchmesser ⌀_y', einheit=MM, ueber=0.0)`
- `s_y: float = bereich(150.0, heisst='Stababstand s_y', einheit=MM, ueber=0.0)`
- `aussen: Richtung = Richtung.X` – Welche Lage der Zugbewehrung aussen liegt, näher am Plattenrand.
- `form: Stuetzenform = Stuetzenform.RECHTECK`
- `lage: Lage = Lage.INNEN`
- `b_x: float = bereich(300.0, heisst='Stütze b_x', einheit=MM, ueber=0.0)`
- `b_y: float = bereich(300.0, heisst='Stütze b_y', einheit=MM, ueber=0.0)`
- `D: float = bereich(300.0, heisst='Durchmesser D', einheit=MM, ueber=0.0)`
- `t: float = bereich(250.0, heisst='Wanddicke t', einheit=MM, ueber=0.0)`
- `a_x: float = bereich(0.0, heisst='Randabstand a_x', einheit=MM, ab=0.0)` – Von der Stütze zum linken Plattenrand -- nur an der Ecke.
- `a_y: float = bereich(0.0, heisst='Randabstand a_y', einheit=MM, ab=0.0)` – Von der Stütze zum unteren Plattenrand -- am Rand und an der Ecke.
- `stufe: Naeherungsstufe = Naeherungsstufe.ZWEI`
- `l_x: float = bereich(7.0, heisst='Spannweite l_x', einheit=M, ueber=0.0)`
- `l_y: float = bereich(7.0, heisst='Spannweite l_y', einheit=M, ueber=0.0)` – Die grössere der angrenzenden Spannweiten je Richtung (4.3.6.4.4).
- `r_sx: float = bereich(1.5, heisst='r_sx', einheit=M, ueber=0.0)`
- `r_sy: float = bereich(1.5, heisst='r_sy', einheit=M, ueber=0.0)`
- `m_sdx: float = bereich(0.0, heisst='m_sd,x', einheit=KNM_PRO_M, ab=0.0)`
- `m_sdy: float = bereich(0.0, heisst='m_sd,y', einheit=KNM_PRO_M, ab=0.0)` – r_s und m_sd von Hand -- nur in Näherungsstufe 3.
- `V_d: float = bereich(0.0, heisst='Auflagerkraft V_d', einheit=KN, ab=0.0)`
- `q_d: float = bereich(0.0, heisst='Flächenlast q_d', einheit=KN_PRO_M2, ab=0.0)` – Was innerhalb des Nachweisschnitts abgezogen wird: Eigengewicht und Nutzlast, bei der Bodenplatte die Bodenpressung -- je als Bemessungswert.
- `ke: KeArt = KeArt.NAEHERUNG`
- `e_x: float = bereich(0.0, heisst='Exzentrizität e_x', einheit=MM)`
- `e_y: float = bereich(0.0, heisst='Exzentrizität e_y', einheit=MM)` – Wie weit die Auflagerkraft neben der Stützenachse angreift.
- `beschreibung: str = ''` – Freier Text -- geht in keine Rechnung ein.
- `knoten: List[GrundrissknotenEintrag] = field(default_factory=list)`
- `aussparungen: List[AussparungEintrag] = field(default_factory=list)`

#### DurchstanzEintrag.neu

```python
@classmethod
def neu(cls, kennung: str, name: str) -> 'DurchstanzEintrag'
```

Eine frische Stelle, wie die Oberflaeche sie anlegt -- die Materialien setzt sie.

#### DurchstanzEintrag.materialien

```python
def materialien(self) -> List[str]
```

Die Materialien, auf die die Stelle zeigt: Beton und Betonstahl.

#### DurchstanzEintrag.bezuege

```python
def bezuege(self) -> List[str]
```

Die Bauteile, deren Querschnitt die Stelle nimmt -- keine.

#### DurchstanzEintrag.netz

```python
def netz(self) -> Netz
```

Die Knoten, mit dem Zusammenführen gleicher Koordinaten -- wie im Zeichenfenster.

#### DurchstanzEintrag.aussparung

```python
def aussparung(self, punkte: Sequence[Sequence[float]]) -> AussparungEintrag
```

Eine Aussparung aus ihren Ecken `[x, y]` in mm.


## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.durchstanzen.stelle]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.netz]]
- [[opencivil.querschnitt.platte]]

## Gebraucht von

- [[opencivil.projekt]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.durchstanzen]]
- [[opencivil.projekt.projekt]]
