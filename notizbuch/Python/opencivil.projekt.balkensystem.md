---
erzeugt: 7bee6c1d55f6
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/balkensystem.py
> ein 2D-Balkensystem, wie die Oberflaeche es beschreibt.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/balkensystem.py)

## VERANTWORTUNG

Der [[opencivil.projekt.balkensystem#BalkensystemEintrag|BalkensystemEintrag]]: ein ebener Rahmen aus Knoten und Linien,
Lagern und Lasten, mit seinen Querschnitten, Lastfaellen und Kombinationen
-- als speicherbare Datenklasse wie die Querschnittsanalyse
([[opencivil.projekt.querschnittsanalyse]]). Dazu der Baukasten, der ohne
Oberflaeche zeichnet, und was beim Teilen und Umkehren einer Linie mit ihren
Lasten geschieht. Gerechnet wird in [[opencivil.stabwerk]].


## ZUERST GEOMETRIE

Gezeichnet werden Knoten und Linien. Eine Linie wird zum Stab, sobald sie
Querschnitt und Material hat (`stab`); sie kann daneben -- oder statt dessen
-- ein Linienlager sein, quer und laengs je frei, fest oder federnd. Ein
Knoten wird zum Lager durch ein [[opencivil.projekt.balkensystem#LagerEintrag|LagerEintrag]] an ihm, nicht durch ein
Feld am Knoten: das Zeichenfenster fuehrt Knoten zusammen und legt neue an,
und ein Feld daran ginge dabei verloren.


## LASTEN AN IHREN ELEMENTEN

Eine Last auf einem Stab steht an seiner Linie (`lasten`), mit dem
Lastfall, zu dem sie gehoert. So bleibt sie bei der Linie, wenn diese
kopiert, geloescht oder rueckgaengig gemacht wird. Eine Last an einem Knoten
ist -- wie ein Lager -- ein eigener Eintrag an ihm.


## KOORDINATEN UND EINHEITEN

x nach rechts, z nach oben, in m; Stellen auf einem Stab in m ab seinem
Anfang. Querschnittsmasse in mm, A in mm², I in 10⁶ mm⁴. Lasten in kN, kN/m,
kNm und kNm/m; Federn in kN/m und kNm/rad, Bettung in kN/m². Umgerechnet
wird beim Bauen.


## VORZEICHEN

Eine Kraftlast ist positiv in ihrer Richtung: «senkrecht» nach unten,
«waagrecht» nach rechts, «quer» zur gestrichelten Faser, «laengs» vom Anfang
zum Ende. Momente drehen im Gegenuhrzeigersinn ([[opencivil.stabwerk.modell]]).

## Inhalt

### SystemknotenEintrag

```python
@dataclass
class SystemknotenEintrag(Beschreibung)
```

Ein Punkt des Systems, in m.

- `kennung: str = ''`
- `x: float = 0.0`
- `z: float = 0.0`

### StablastEintrag

```python
@dataclass
class StablastEintrag(Beschreibung)
```

Eine Last auf einem Stab, in einem Lastfall -- in der Einheit ihrer Art
([[opencivil.projekt.balkensystem#Konstanten|EINHEIT_DER_LAST]]). `wert_b` gilt am Ende des belasteten
Bereichs, leer: wie `wert_a`. `bis` leer: bis zum Ende des Stabs.
Einzellast und Einzelmoment stehen bei `von`.

- `lastfall: str = ''`
- `art: str = einer_von(STABLASTEN, Lastart.LINIENLAST.value)`
- `richtung: str = einer_von(RICHTUNGEN, Lastrichtung.SENKRECHT.value)`
- `wert_a: float = 10.0`
- `wert_b: Optional[float] = None`
- `von: float = 0.0`
- `bis: Optional[float] = None`
- `projiziert: bool = False` – Senkrecht und waagrecht je Meter Projektion statt je Meter Stab.

#### StablastEintrag.verteilt

```python
@property
def verteilt(self) -> bool
```

### SystemlinieEintrag

```python
@dataclass
class SystemlinieEintrag(Beschreibung)
```

Eine Linie des Systems: ein Stab, wenn `stab`; dazu, oder ohne Stab,
ein Linienlager quer und laengs.

- `kennung: str = ''`
- `von: str = ''`
- `bis: str = ''`
- `stab: bool = False`
- `querschnitt: str = ''` – Kennung des Querschnitts im System (`Q1`).
- `material: str = ''` – Kennung des Materials im Projekt (`b1`).
- `gelenk_anfang: bool = False`
- `gelenk_ende: bool = False`
- `quer: str = einer_von(HALT, 'frei')`
- `k_quer: float = 0.0` – Bettung quer, kN/m².
- `laengs: str = einer_von(HALT, 'frei')`
- `k_laengs: float = 0.0`
- `lasten: List[StablastEintrag] = field(default_factory=list)`

### LagerEintrag

```python
@dataclass
class LagerEintrag(Beschreibung)
```

Ein Lager an einem Knoten: je Richtung frei, fest oder Feder.

- `kennung: str = ''`
- `knoten: str = ''`
- `x: str = einer_von(HALT, 'fest')`
- `k_x: float = 0.0` – kN/m.
- `z: str = einer_von(HALT, 'fest')`
- `k_z: float = 0.0`
- `phi: str = einer_von(HALT, 'frei')`
- `k_phi: float = 0.0` – kNm/rad.

### KnotenlastEintrag

```python
@dataclass
class KnotenlastEintrag(Beschreibung)
```

Eine Last an einem Knoten, in einem Lastfall: eine Kraft mit Richtung oder ein Moment.

- `kennung: str = ''`
- `knoten: str = ''`
- `lastfall: str = ''`
- `art: str = einer_von(KNOTENLASTEN, 'kraft')`
- `richtung: str = einer_von(KNOTENRICHTUNGEN, Lastrichtung.SENKRECHT.value)`
- `wert: float = 10.0` – kN oder kNm.

### StabquerschnittEintrag

```python
@dataclass
class StabquerschnittEintrag(Beschreibung)
```

Ein Querschnitt der Staebe: nach Vorlage mit Massen in mm, mit Kennwerten
von Hand (`A` in mm², `I` in 10⁶ mm⁴), oder aus einer Platte oder
einer Querschnittsanalyse des Projekts (`bezug`).

- `kennung: str = ''`
- `name: str = ''`
- `art: str = einer_von(QUERSCHNITTSARTEN, 'vorlage')`
- `vorlage: str = einer_von((v.schluessel for v in qs.VORLAGEN), qs.RECHTECK.schluessel)`
- `masse: Dict[str, float] = field(default_factory=dict)`
- `bezug: str = ''`

#### StabquerschnittEintrag.stabvorlage

```python
def stabvorlage(self) -> qs.Stabvorlage
```

#### StabquerschnittEintrag.masse_mit_vorgaben

```python
def masse_mit_vorgaben(self) -> Dict[str, float]
```

Die Masse der Vorlage -- was fehlt, mit ihrer Vorgabe.

#### StabquerschnittEintrag.fehler

```python
def fehler(self) -> Optional[str]
```

Was an Massen oder Kennwerten nicht geht -- `None`, wenn alles geht.
Ein Mass, das die Vorlage nicht kennt, ist ein Tippfehler: bis
2026-10-16 stand `B=500` still da, und gerechnet wurde mit b = 300.

### LastfallEintrag

```python
@dataclass
class LastfallEintrag(Beschreibung)
```

Ein Lastfall des Systems: eine Kennung, auf die die Lasten zeigen, und ein Name.

- `kennung: str = ''`
- `name: str = ''`

### LastkombinationEintrag

```python
@dataclass
class LastkombinationEintrag(Beschreibung)
```

Eine Kombination: je Lastfall (Kennung) ein Beiwert, von Hand.

- `kennung: str = ''`
- `name: str = ''`
- `faktoren: Dict[str, float] = field(default_factory=dict)`

### Modell

```python
@dataclass
class Modell
```

Das Stabwerk der Beschreibung, in N, m und rad -- noch ohne
Steifigkeiten: `EA` und `EI` jedes Stabs kommen aus dem Rechenwerk,
je Paar aus Querschnitt und Material (`paare`). Was sich nicht
uebersetzen laesst, steht in `meldungen`, wie die des Rechenkerns.

- `system: System`
- `paare: Dict[str, Tuple[str, str]] = field(default_factory=dict)` – Je tragenden Stab die Kennungen seines Querschnitts und seines Materials.
- `meldungen: List[Meldung] = field(default_factory=list)`

#### Modell.gueltig

```python
@property
def gueltig(self) -> bool
```

### BalkensystemEintrag

```python
@dataclass
class BalkensystemEintrag(Beschreibung)
```

Ein ebener Rahmen: Knoten, Linien, Lager, Lasten, Querschnitte, Lastfaelle, Kombinationen.

- `BEZEICHNUNG = 'Balkensystem'`
- `kennung: str`
- `name: str`
- `knoten: List[SystemknotenEintrag] = field(default_factory=list)`
- `linien: List[SystemlinieEintrag] = field(default_factory=list)`
- `lager: List[LagerEintrag] = field(default_factory=list)`
- `knotenlasten: List[KnotenlastEintrag] = field(default_factory=list)`
- `querschnitte: List[StabquerschnittEintrag] = field(default_factory=list)`
- `lastfaelle: List[LastfallEintrag] = field(default_factory=list)`
- `kombinationen: List[LastkombinationEintrag] = field(default_factory=list)`
- `beschreibung: str = ''` – Freier Text -- geht in keine Rechnung ein.

#### BalkensystemEintrag.pruefen

```python
def pruefen(self) -> None
```

Nichts, was das ganze Projekt aufhielte: was an einem System nicht
stimmt -- auch zwei Faelle gleichen Namens --, steht in seinen
Meldungen ([[opencivil.projekt.balkensystem#BalkensystemEintrag.modell|modell]]), und die anderen Bauteile rechnen weiter.

#### BalkensystemEintrag.materialien

```python
def materialien(self) -> List[str]
```

Die Materialien der Staebe -- fuer den Baum, der keines loeschen laesst, das gebraucht wird.

#### BalkensystemEintrag.bezuege

```python
def bezuege(self) -> List[str]
```

Die Platten und Querschnittsanalysen, deren Querschnitt ein Stab nimmt.

#### BalkensystemEintrag.linie_von

```python
def linie_von(self, kennung: str) -> SystemlinieEintrag
```

#### BalkensystemEintrag.enden

```python
def enden(self, linie: SystemlinieEintrag) -> Tuple[Tuple[float, float], Tuple[float, float]]
```

Anfang und Ende einer Linie, in m.

#### BalkensystemEintrag.laenge

```python
def laenge(self, linie: SystemlinieEintrag) -> float
```

#### BalkensystemEintrag.stelle_auf

```python
def stelle_auf(self, kennung: str, punkt: Sequence[float]) -> float
```

Wo ein Punkt auf einer Linie liegt, in m ab ihrem Anfang -- auf die Linie gelotet.

#### BalkensystemEintrag.modell

```python
def modell(self) -> Modell
```

Das Stabwerk zum Rechnen, in SI ([[opencivil.stabwerk.modell]]).

Ein Stab ohne Querschnitt oder Material, ein Querschnitt mit
unmoeglichen Massen und eine Feder ohne Steifigkeit sind Fehler, die
die Meldungen nennen: gerechnet wird dann nicht -- und nicht etwa mit
einem Stab weniger. Eine Last, deren Lastfall es nicht gibt, und ein
Beiwert dafuer bleiben mit einem Hinweis weg.

#### BalkensystemEintrag.netz

```python
def netz(self) -> Netz
```

#### BalkensystemEintrag.linie

```python
def linie(self, von: Ort, bis: Ort, *, querschnitt: Any=None, material: Any=None, **felder: Any) -> SystemlinieEintrag
```

Eine Linie von `von` nach `bis` -- ein Stab, sobald `querschnitt`
und `material` dastehen. Weitere Felder wie [[opencivil.projekt.balkensystem#SystemlinieEintrag|SystemlinieEintrag]].

#### BalkensystemEintrag.lager_an

```python
def lager_an(self, ort: Ort, art: str='gelenkig', **felder: Any) -> LagerEintrag
```

Ein Lager -- `gelenkig`, `verschieblich` oder `eingespannt`, Felder darueber.

#### BalkensystemEintrag.querschnitt

```python
def querschnitt(self, name: str, vorlage: str=qs.RECHTECK.schluessel, **masse: float) -> StabquerschnittEintrag
```

Ein Querschnitt nach Vorlage -- Masse in mm, was fehlt nach ihrer Vorgabe.

#### BalkensystemEintrag.querschnitt_aus

```python
def querschnitt_aus(self, name: str, art: str, bezug: Any) -> StabquerschnittEintrag
```

Ein Querschnitt aus einer Platte (`platte`) oder einer Querschnittsanalyse (`analyse`).

#### BalkensystemEintrag.querschnitt_mit_kennwerten

```python
def querschnitt_mit_kennwerten(self, name: str, *, A: float, I: float) -> StabquerschnittEintrag
```

Ein Querschnitt mit Kennwerten von Hand -- A in mm², I in 10⁶ mm⁴.

#### BalkensystemEintrag.lastfall

```python
def lastfall(self, name: str) -> LastfallEintrag
```

#### BalkensystemEintrag.kombination

```python
def kombination(self, name: str, *faktoren: Tuple[Any, float]) -> LastkombinationEintrag
```

Eine Kombination -- je Lastfall (Eintrag oder Kennung) ein Beiwert: `(g, 1.35), (w, 1.5)`.

#### BalkensystemEintrag.stablast

```python
def stablast(self, lastfall: Any, linie: Any, art: str=Lastart.LINIENLAST.value, wert: float=10.0, **felder: Any) -> StablastEintrag
```

Eine Last auf einer Linie -- `wert` ist `wert_a`; Felder wie [[opencivil.projekt.balkensystem#StablastEintrag|StablastEintrag]].

#### BalkensystemEintrag.knotenlast

```python
def knotenlast(self, lastfall: Any, ort: Ort, wert: float=10.0, *, art: str='kraft', richtung: str=Lastrichtung.SENKRECHT.value) -> KnotenlastEintrag
```

#### BalkensystemEintrag.teilen

```python
def teilen(self, kennung: str, stelle: float) -> SystemlinieEintrag
```

Teilt eine Linie bei `stelle` m ab ihrem Anfang: sie endet dort, und
eine neue laeuft weiter zum alten Ende -- mit ihren Eigenschaften. Die
Lasten gehen mit, je auf ihre Haelfte: eine Strecke ueber den Schnitt
wird zwei, mit dem Wert an der Schnittstelle; eine Einzellast bleibt
dort, wo sie steht. Das Gelenk am Ende wandert mit ans neue Ende; an
der Schnittstelle ist die Linie durchlaufend.

#### BalkensystemEintrag.umkehren

```python
def umkehren(self, kennung: str) -> None
```

Tauscht Anfang und Ende einer Linie. Die gestrichelte Faser liegt
danach auf der anderen Seite, die Lasten bleiben, wo sie wirken: ihre
Stellen gespiegelt, Anfangs- und Endwert getauscht, und quer und
laengs mit umgekehrtem Vorzeichen -- diese Richtungen haengen an der
Linie. Senkrecht, waagrecht und Momente aendern sich nicht.

#### BalkensystemEintrag.neu

```python
@classmethod
def neu(cls, kennung: str, name: str, material: str) -> 'BalkensystemEintrag'
```

Ein frisches System, wie der Benutzer es angelegt bekommt: ein
Einfeldtraeger von 6 m, Rechteck 300 × 600 mm, links gelenkig, rechts
verschieblich, ein Lastfall mit 10 kN/m. Zum Anfangen, nicht als
Vorgabe.


## Konstanten

- `HALT = ('frei', 'fest', 'feder')` – Wie ein Lager oder Linienlager je Richtung haelt.
- `EINHEIT_DER_LAST = {Lastart.LINIENLAST.value: KN_PRO_M, Lastart.EINZELLAST.value: KN, La…` – Die Einheit jeder Last in der Beschreibung, nach ihrer Art -- an einem Stab oder Knoten. Umgerechnet wird beim Bauen, mit diesen.
- `EINHEIT_DER_FEDER = {'k_x': KN_PRO_M, 'k_z': KN_PRO_M, 'k_phi': KNM_PRO_RAD, 'k_quer': KN…` – Die Einheit jeder Feder, nach ihrem Feld: Lager in kN/m und kNm/rad, Bettung in kN/m je m Stab.
- `STABLASTEN = tuple((a.value for a in Lastart))` – Was fuer Lasten auf einem Stab liegen koennen -- und an einem Knoten.
- `KNOTENLASTEN = ('kraft', 'moment')`
- `RICHTUNGEN = tuple((r.value for r in Lastrichtung))` – Wohin eine Kraft zeigt -- an einem Knoten nur senkrecht oder waagrecht.
- `KNOTENRICHTUNGEN = (Lastrichtung.SENKRECHT.value, Lastrichtung.WAAGRECHT.value)`
- `QUERSCHNITTSARTEN = ('vorlage', 'kennwerte', 'platte', 'analyse')` – Woher ein Querschnitt kommt.
- `KENNWERTE = ('A', 'I')` – Die Kennwerte eines Querschnitts von Hand: A in mm², I in 10⁶ mm⁴.
- `LAGERARTEN = {'gelenkig': ('fest', 'fest', 'frei'), 'verschieblich': ('frei', 'fes…` – Die Vorwahlen eines Lagers -- je Richtung frei oder fest.
- `Ort = Union[str, Sequence[float]]` – Ein Punkt in m -- oder die Kennung eines Knotens, der dort liegt.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.netz]]
- [[opencivil.stabwerk.modell]]
- [[opencivil.stabwerk.querschnitte]]
- [[opencivil.stabwerk.system]]

## Gebraucht von

- [[opencivil.projekt]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.projekt]]
- [[opencivil.web.api]]
