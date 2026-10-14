---
erzeugt: 71c069e3244d
art: modul
tags: [modul]
---
> [!abstract] opencivil/notizbuch/formelseiten.py
> die Formelsammlung als Seiten.
> Paket [[opencivil.notizbuch]] · [Quelltext](../../opencivil/notizbuch/formelseiten.py)

## VERANTWORTUNG

Je Formel eine Seite, je Thema eine, dazu die Uebersicht -- aus denselben
Laeufen wie die Formelsammlung ([[opencivil.bericht.formelsammlung#laeufe|opencivil.bericht.formelsammlung.laeufe]]),
die zusammen jede Formel des Werkzeugs schreiben. Welche Formel hineingehoert
und wie sie heisst, sagt die Formelsammlung; hier wird nur gesetzt.


## WAS EINE FORMELSEITE ZEIGT

Die Formel ohne Zahlen -- in jeder Fassung, wenn es mehrere gibt --, ihre
Normstelle oder dass sie fehlt, die Groessen samt Herkunft, dieselbe Formel
mit den Zahlen eines Projekts, welche Formeln sie brauchen, wo sie im Code
steht und zu welchen Themen sie gehoert. Darunter, von Hand, die Theorie.


## WOHER EINE GROESSE KOMMT

Aus der Rechnung selbst: je Lauf merkt sich [[opencivil.notizbuch.formelseiten#sammeln|sammeln]], welche Formel
einen Wert zuletzt geschrieben hat. Braucht eine spaetere Formel ihn, ist
das ihre Herkunft -- als Link. Schrieb ihn keine Formel der Sammlung, sagt
der Wert selbst, woher er kommt: Eingabe, Vorgabe oder Zwischenwert.
Die Laeufe bleiben getrennt: `querschnitt.q1` meint in jedem Projekt eine
andere Platte.

## Inhalt

### Groessenzeile

```python
@dataclass
class Groessenzeile
```

Eine Zeile der Tabelle «Groessen».

- `zeichen: str`
- `bedeutung: str = ''`
- `einheit: str = ''`
- `woher: Dict[Tuple[str, str], None] = field(default_factory=dict)` – Geordnete Menge: `("seite", Name)` oder `("angabe", Text)`.

### Fassung

```python
@dataclass
class Fassung
```

Eine Formel, wie sie zum ersten Mal dasteht -- mit allem, was ihre Vorkommen sagen.

- `block: GleichungBlock`
- `projekt: str`
- `groessen: Dict[str, Groessenzeile] = field(default_factory=dict)` – Je Platzhalter der Vorlage.

### Formel

```python
@dataclass
class Formel
```

Alles zu einem Formelnamen, ueber alle Laeufe.

- `name: str`
- `fassungen: Dict[tuple, Fassung] = field(default_factory=dict)`
- `themen: Dict[str, None] = field(default_factory=dict)`
- `codestellen: Dict[str, None] = field(default_factory=dict)`
- `gebraucht_von: Dict[str, None] = field(default_factory=dict)`

#### Formel.referenzen

```python
@property
def referenzen(self) -> List[str]
```

#### Formel.zeichen

```python
@property
def zeichen(self) -> List[str]
```

### Thema

```python
@dataclass
class Thema
```

- `name: str`
- `bereich: str`
- `formeln: Dict[str, None] = field(default_factory=dict)`
- `erklaerungen: List[str] = field(default_factory=list)`

### sammeln

```python
def sammeln() -> Tuple[Dict[str, Formel], Dict[str, Thema]]
```

Jede Formel und jedes Thema der Sammlung, in der Folge ihres ersten Auftretens.

### seiten

```python
def seiten(formeln: Optional[Dict[str, Formel]]=None, themen: Optional[Dict[str, Thema]]=None, codestelle: Optional[Callable[[str], str]]=None) -> List[Seite]
```

Die Uebersicht, je Thema eine Seite und je Formel eine. `codestelle`
macht aus `modul:Funktion` einen Link auf die Seite des Moduls -- ohne
steht die Stelle als Code da.

### _groessen

```python
def _groessen(fassungen: List[Fassung]) -> List[str]
```

Die Zeilen der Tabelle -- dieselbe Groessenzeile in mehreren Fassungen einmal.


## Konstanten

- `FORMELN = 'Formelsammlung/Formeln'`
- `THEMEN = 'Formelsammlung/Themen'`
- `UEBERSICHT = 'Formelsammlung/Formelsammlung.md'`
- `BEREICHE = {'beton': 'Baustoffe', 'betonstahl': 'Baustoffe', **{art.raum: art.be…` – Wie die Uebersicht die Themen gruppiert -- nach dem Bestandteil, zu dem sie gehoeren (`Thema.art` der Formelsammlung: der Anfang des Namensraums). Die Bauteile nennen ihren Abschnitt im Steckbrief.
- `ANGABEN = {Quelle.EINGABE: 'Eingabe', Quelle.UEBERSCHRIEBEN: 'Eingabe', Quelle.…` – Woher ein Wert kommt, den keine Formel der Sammlung geschrieben hat.

## Braucht

- [[opencivil.bericht.formelsammlung]]
- [[opencivil.bericht.markdown]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.notizbuch.namen]]
- [[opencivil.notizbuch.tresor]]
- [[opencivil.projekt.aufbau]]

## Gebraucht von

- [[opencivil.notizbuch.erzeugen]]
