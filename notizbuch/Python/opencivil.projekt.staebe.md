---
erzeugt: cf718c532c4f
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/staebe.py
> der Baukasten eines Stabwerks, eben und im Raum.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/staebe.py)

## VERANTWORTUNG

Was das 2D- und das 3D-Balkensystem gleich tun ([[opencivil.projekt.staebe#MitStaeben|MitStaeben]]):
Knoten an gleichen Koordinaten zusammenfuehren; Linien, Lager, Materialien,
Querschnitte, Lasten und Diagramme ohne Oberflaeche anlegen; eine Linie
finden, messen, teilen und umkehren. Welche Klassen die Teile haben und wie
die Achsen heissen, sagt die Beschreibung, die ihn nimmt
([[opencivil.projekt.balkensystem#BalkensystemEintrag|BalkensystemEintrag]],
[[opencivil.projekt.balkensystem3d#Balkensystem3dEintrag|Balkensystem3dEintrag]]). Bis
2026-11-15 stand er im 2D-Balkensystem allein.


## TEILEN UND UMKEHREN

Die Lasten gehen mit ihrer Linie. Beim Teilen liegt eine verteilte Last
danach auf beiden Haelften, mit dem Wert an der Schnittstelle; eine
Einzellast bleibt, wo sie steht. Beim Umkehren bleiben die Lasten, wo sie
wirken: ihre Stellen gespiegelt, Anfangs- und Endwert getauscht, und eine
Richtung, die an der Linie haengt, mit umgekehrtem Vorzeichen -- welche,
sagt die Beschreibung ([[opencivil.projekt.staebe#MitStaeben._kehrt_um|MitStaeben._kehrt_um]]).


## QUERSCHNITTE

Ein Querschnitt der Staebe ist in beiden Systemen nach Vorlage, ein
Stahlprofil aus der Tabelle oder mit Kennwerten von Hand
([[opencivil.projekt.staebe#StabquerschnittBasis|StabquerschnittBasis]]); welche Kennwerte, sagt das System. Aus
einer Platte oder Querschnittsanalyse nimmt ihn nur das 2D-Balkensystem.

## Inhalt

### Querschnittsart

```python
class Querschnittsart(Wahl)
```

Woher die Kennwerte eines Stabquerschnitts kommen. Aufgeloest wird die
Art einmal, im Aufbau: je Art eine Klasse
([[opencivil.stabwerk.stabquerschnitt]]).

- `VORLAGE = 'vorlage'`
- `PROFIL = 'profil'`
- `KENNWERTE = 'kennwerte'`
- `PLATTE = 'platte'`
- `ANALYSE = 'analyse'`

#### Querschnittsart.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Querschnittsart.kurz

```python
@property
def kurz(self) -> str
```

Fuer den Schalter -- der lange Name steht in seinem Titel.

#### Querschnittsart.aus_bauteil

```python
@property
def aus_bauteil(self) -> bool
```

Ob er ein Bauteil des Projekts nimmt, eine Platte oder eine
Querschnittsanalyse. Nur dann bringt er ein Material mit, den Beton
des Bauteils, und nur dann hat er ein E_eq -- eine
Momenten-Kruemmungs-Linie mit ihrer Bewehrung, bei einer Platte immer
in x-Richtung, Zug unten (Benutzer, 2026-10-24). Einer nach Vorlage
oder von Hand ist nur eine Form.

### _aufgezaehlt

```python
def _aufgezaehlt(namen: Sequence[str]) -> str
```

«A und I», «A, I_y, I_z und I_T».

### StabquerschnittBasis

```python
@dataclass
class StabquerschnittBasis(Beschreibung)
```

Ein Querschnitt der Staebe: nach Vorlage mit Massen in mm, ein
Stahlprofil aus der Tabelle (`profil`) oder mit Kennwerten von Hand in
`masse` -- `A` in mm², Traegheitsmomente in 10⁶ mm⁴; welche, sagt
[[opencivil.projekt.staebe#StabquerschnittBasis|KENNWERTE]]. E und G kommen vom Material des Stabs.

- `KENNWERTE: ClassVar[Tuple[str, ...]]` – Die Kennwerte von Hand, wie die Rechnung sie nimmt.
- `kennung: str = ''`
- `name: str = ''`
- `art: Querschnittsart = einer_von(tuple(Querschnittsart), Querschnittsart.VORLAGE)`
- `vorlage: str = einer_von((v.schluessel for v in qs.VORLAGEN), qs.RECHTECK.schluessel)`
- `masse: Dict[str, float] = field(default_factory=dict)`
- `profil: str = 'IPE 300'` – Der Name des Stahlprofils ([[opencivil.stabwerk.profiltabelle]]). Kein Wahlfeld, damit die Meldung nicht alle 666 Profile aufzaehlt: einen unbekannten Namen meldet der Aufbau, wie eine Platte, die es nicht gibt.

#### StabquerschnittBasis.neu

```python
@classmethod
def neu(cls) -> 'StabquerschnittBasis'
```

Ein frischer Querschnitt, wie die Oberflaeche ihn anlegt: ein Rechteck mit seinen Vorgaben.

#### StabquerschnittBasis.stabvorlage

```python
def stabvorlage(self) -> qs.Stabvorlage
```

#### StabquerschnittBasis.masse_mit_vorgaben

```python
def masse_mit_vorgaben(self) -> Dict[str, float]
```

Die Masse der Vorlage -- was fehlt, mit ihrer Vorgabe.

#### StabquerschnittBasis.fehler

```python
def fehler(self) -> Optional[str]
```

Was an Massen oder Kennwerten nicht geht -- `None`, wenn alles geht.
Ein Mass, das die Vorlage nicht kennt, ist ein Tippfehler: bis
2026-10-16 stand `B=500` still da, und gerechnet wurde mit b = 300.

### MitStaeben

```python
class MitStaeben
```

Der Baukasten eines Stabwerks -- fuer eine Beschreibung mit `knoten`,
`linien`, `lager`, `knotenlasten`, `stabmaterialien`,
`querschnitte` und `diagramme`. Die Klassen ihrer Teile, die Achsen
und die Arten der Lager stehen in ihr als Klassenattribute.

- `BEZEICHNUNG: str`
- `ACHSEN: Tuple[str, ...]` – Wie die Koordinaten eines Knotens heissen -- `("x", "z")` in der Ebene.
- `LAGERFELDER: Tuple[str, ...]` – Die Richtungen eines Lagers, in der Folge der Vorwahlen in [[opencivil.projekt.staebe#MitStaeben|LAGERARTEN]] -- Felder des Lagers wie des Lagers im Rechenkern.
- `LAGERARTEN: Mapping[str, Tuple[str, ...]]` – Die Vorwahlen eines Lagers -- je Richtung frei oder fest.
- `LINIENLAGER: Tuple[str, ...]` – Die Richtungen eines Linienlagers -- Felder der Linie wie des Stabs im Rechenkern.
- `EINHEIT_DER_FEDER: Mapping[str, Any]` – Die Einheit jeder Feder, nach ihrem Feld -- an Lager und Linie.
- `NEUE_DIAGRAMME: Tuple[str, ...]` – Was ein frisches System von der GZT zeigt -- dazu die Verschiebung der GZG.
- `KNOTEN: type`
- `LINIE: type`
- `LAGER: type`
- `STABLAST: type`
- `KNOTENLAST: type`
- `MATERIAL: type`
- `QUERSCHNITT: type`
- `DIAGRAMM: type`
- `name: str`
- `knoten: List[Any]`
- `linien: List[Any]`
- `lager: List[Any]`
- `knotenlasten: List[Any]`
- `stabmaterialien: List[Any]`
- `querschnitte: List[Any]`
- `diagramme: List[Any]`

#### MitStaeben.neu

```python
@classmethod
def neu(cls, kennung: str, name: str) -> Any
```

Ein frisches System, wie der Benutzer es angelegt bekommt: ohne
Knoten, Linie, Lager und Querschnitt (Benutzer, 2026-10-19), aber mit
den Lastfaellen Eigengewicht -- es kommt von selbst --, Auflast und
Nutzlast, die beiden ohne Last, und den Kombinationen GZT mit 1.35,
1.35 und 1.5 und GZG mit je 1.0 (Benutzer, 2026-10-23). Dazu die
Diagramme [[opencivil.projekt.staebe#MitStaeben|NEUE_DIAGRAMME]] der GZT und die Verschiebung der GZG.

#### MitStaeben.wo

```python
@property
def wo(self) -> str
```

Wie das System in einer Meldung heisst: «Balkensystem 'Rahmen'».

#### MitStaeben.materialien

```python
def materialien(self) -> List[str]
```

Jedes Material des Projekts, auf das ein Material des Systems zeigt --
auch eines, das gerade keinen Stab traegt: wer es loescht, liesse es
ins Leere zeigen, und spaetestens die naechste Aenderung machte
daraus einen Fehler beim Rechnen.

#### MitStaeben.alle_lasten

```python
def alle_lasten(self) -> List[Any]
```

Jede Last des Systems, auf den Linien und an den Knoten -- ihre Kennungen zaehlen zusammen.

#### MitStaeben.linie_von

```python
def linie_von(self, kennung: str) -> Any
```

#### MitStaeben.enden

```python
def enden(self, linie: Any) -> Tuple[Punkt, Punkt]
```

Anfang und Ende einer Linie, in m.

#### MitStaeben.laenge

```python
def laenge(self, linie: Any) -> float
```

#### MitStaeben.stelle_auf

```python
def stelle_auf(self, kennung: str, punkt: Sequence[float]) -> float
```

Wo ein Punkt auf einer Linie liegt, in m ab ihrem Anfang -- auf die Linie gelotet.

#### MitStaeben.netz

```python
def netz(self) -> Netz
```

#### MitStaeben.linie

```python
def linie(self, von: Ort, bis: Ort, *, querschnitt: Any=None, material: Any=None, **felder: Any) -> Any
```

Eine Linie von `von` nach `bis` -- ein Stab, sobald `querschnitt`
und `material` dastehen: ein Material des Systems ([[opencivil.projekt.staebe#MitStaeben.beton|beton]],
[[opencivil.projekt.staebe#MitStaeben.baustahl|baustahl]], [[opencivil.projekt.staebe#MitStaeben.eigenes_material|eigenes_material]]). Weitere Felder wie die
Klasse der Linien.

#### MitStaeben.lager_an

```python
def lager_an(self, ort: Ort, art: str='gelenkig', **felder: Any) -> Any
```

Ein Lager -- eine der [[opencivil.projekt.staebe#MitStaeben|LAGERARTEN]], einzelne Felder darueber.

#### MitStaeben.beton

```python
def beton(self, beton: Any) -> Any
```

Das Material des Systems aus einem Beton des Projekts (Eintrag oder
Kennung) -- das schon da ist, sonst ein neues.

#### MitStaeben.baustahl

```python
def baustahl(self, stahl: Any) -> Any
```

Das Material des Systems aus einem Baustahl des Projekts -- siehe [[opencivil.projekt.staebe#MitStaeben.beton|beton]].

#### MitStaeben.eigenes_material

```python
def eigenes_material(self, name: str, **werte: float) -> Any
```

Ein eigenes Material des Systems -- E in N/mm², die Dichte in kg/m³, Felder wie seine Klasse.

#### MitStaeben.querschnitt

```python
def querschnitt(self, name: str, vorlage: str=qs.RECHTECK.schluessel, **masse: float) -> Any
```

Ein Querschnitt nach Vorlage -- Masse in mm, was fehlt nach ihrer Vorgabe.

#### MitStaeben.stahlprofil

```python
def stahlprofil(self, name: str, profil: str, **felder: Any) -> Any
```

Ein Stahlprofil aus der Tabelle, «HEB 300» -- Felder wie die Klasse der Querschnitte.

#### MitStaeben.querschnitt_mit_kennwerten

```python
def querschnitt_mit_kennwerten(self, name: str, **kennwerte: float) -> Any
```

Ein Querschnitt mit Kennwerten von Hand -- A in mm², Traegheitsmomente in 10⁶ mm⁴.

#### MitStaeben.diagramm

```python
def diagramm(self, fall: Any, groesse: str) -> Any
```

Ein Diagramm der Statik-Analyse -- `fall` ein Lastfall oder eine Kombination.

#### MitStaeben.stablast

```python
def stablast(self, lastfall: Any, linie: Any, art: Lastart=Lastart.LINIENLAST, wert: float=10.0, **felder: Any) -> Any
```

Eine Last auf einer Linie -- `wert` ist `wert_a`; Felder wie die Klasse der Stablasten.

#### MitStaeben.knotenlast

```python
def knotenlast(self, lastfall: Any, ort: Ort, wert: float=10.0, *, art: str='kraft', **felder: Any) -> Any
```

Eine Last an einem Knoten -- eine Kraft oder ein Moment; Felder wie ihre Klasse.

#### MitStaeben.teilen

```python
def teilen(self, kennung: str, stelle: float) -> Any
```

Teilt eine Linie bei `stelle` m ab ihrem Anfang: sie endet dort, und
eine neue laeuft weiter zum alten Ende -- mit ihren Eigenschaften. Die
Lasten gehen mit: eine verteilte liegt danach auf beiden Haelften, mit
dem Wert an der Schnittstelle, die auf der zweiten mit einer eigenen
Kennung; eine Einzellast bleibt dort, wo sie steht, ihre Stelle in %
der neuen Haelfte. Das Gelenk am Ende wandert mit ans neue Ende; an der
Schnittstelle ist die Linie durchlaufend.

#### MitStaeben.umkehren

```python
def umkehren(self, kennung: str) -> None
```

Tauscht Anfang und Ende einer Linie, mit ihren Gelenken. Die Lasten
bleiben, wo sie wirken: ihre Stellen gespiegelt, Anfangs- und Endwert
getauscht, und mit umgekehrtem Vorzeichen, wo ihre Richtung an der
Linie haengt ([[opencivil.projekt.staebe#MitStaeben._kehrt_um|_kehrt_um]]).

#### MitStaeben._kehrt_um

```python
def _kehrt_um(self, last: Any) -> bool
```

Ob eine Last ihr Vorzeichen wechselt, wenn ihre Linie umgekehrt wird.


## Konstanten

- `Ort = Union[str, Sequence[float]]` – Ein Punkt in m -- oder die Kennung eines Knotens, der dort liegt.
- `Punkt = Tuple[float, ...]` – Ein Punkt in m, mit so vielen Koordinaten, wie das System Achsen hat.

## Braucht

- [[opencivil.core.wahl]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.faelle]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.netz]]
- [[opencivil.stabwerk.modell]]
- [[opencivil.stabwerk.profiltabelle]]
- [[opencivil.stabwerk.querschnitte]]

## Gebraucht von

- [[opencivil.projekt.aufbau.balkensystem]]
- [[opencivil.projekt.balkensystem]]
- [[opencivil.projekt.balkensystem3d]]
- [[opencivil.web.dienst]]
