---
erzeugt: d93ea14a8954
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

Gezeichnet werden Knoten und Linien. Eine Linie ist ein Stab, sobald sie
einen Querschnitt hat; sie kann daneben -- oder statt dessen -- ein
Linienlager sein, quer und laengs je frei, fest oder federnd. Ein Knoten
wird zum Lager durch ein [[opencivil.projekt.balkensystem#LagerEintrag|LagerEintrag]] an ihm, nicht durch ein Feld
am Knoten: das Zeichenfenster fuehrt Knoten zusammen und legt neue an, und
ein Feld daran ginge dabei verloren.


## LASTEN AN IHREN ELEMENTEN

Eine Last auf einem Stab steht an seiner Linie (`lasten`), mit dem
Lastfall, zu dem sie gehoert. So bleibt sie bei der Linie, wenn diese
kopiert, geteilt, geloescht oder rueckgaengig gemacht wird. Eine Last an
einem Knoten ist -- wie ein Lager -- ein eigener Eintrag an ihm. Jede Last
hat eine eigene Kennung (`P1`): im Zeichenfenster laesst sie sich fuer sich
waehlen und loeschen (Benutzer, 2026-10-23). Eine verteilte Last liegt immer
auf der ganzen Linie, eine Einzellast und ein Einzelmoment an einer Stelle
in Prozent der Linie ab ihrem Anfang.


## KOORDINATEN UND EINHEITEN

x nach rechts, z nach oben, in m; Stellen auf einem Stab in % seiner Laenge
ab seinem Anfang. Querschnittsmasse in mm, A in mm², I in 10⁶ mm⁴. Lasten in kN, kN/m,
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
([[opencivil.projekt.balkensystem#Konstanten|EINHEIT_DER_LAST]]). Eine verteilte liegt auf der ganzen Linie:
`wert_a` am Anfang, `wert_b` am Ende, leer: wie `wert_a`.
Einzellast und Einzelmoment stehen bei `stelle`, in % der Linie ab
ihrem Anfang (Benutzer, 2026-10-23).

- `kennung: str = ''`
- `lastfall: str = ''`
- `art: Lastart = Lastart.LINIENLAST`
- `richtung: Lastrichtung = Lastrichtung.SENKRECHT`
- `wert_a: float = 10.0`
- `wert_b: Optional[float] = None`
- `stelle: float = bereich(50.0, heisst='Stelle', einheit=PROZENT, ab=0.0, bis=100.0)`
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

Eine Linie des Systems: ein Stab, wenn sie einen Querschnitt hat; dazu,
oder ohne Stab, ein Linienlager quer und laengs.

- `kennung: str = ''`
- `von: str = ''`
- `bis: str = ''`
- `querschnitt: str = ''` – Kennung des Querschnitts im System (`Q1`); leer: kein Stab, nur eine Linie.
- `material: str = ''` – Kennung des Materials im Projekt (`b1`) -- oder [[opencivil.projekt.balkensystem#Konstanten|MATERIAL_DES_QUERSCHNITTS]]: das Material, das eine Platte oder Querschnittsanalyse als Querschnitt mitbringt.
- `gelenk_anfang: bool = False`
- `gelenk_ende: bool = False`
- `quer: str = einer_von(HALT, 'frei')`
- `k_quer: float = 0.0` – Bettung quer, kN/m².
- `laengs: str = einer_von(HALT, 'frei')`
- `k_laengs: float = 0.0`
- `lasten: List[StablastEintrag] = field(default_factory=list)`

#### SystemlinieEintrag.stab

```python
@property
def stab(self) -> bool
```

Ob die Linie traegt -- sie hat einen Querschnitt.

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

Eine Last an einem Knoten, in einem Lastfall: eine Kraft mit Richtung
oder ein Moment. Ihre Kennung zaehlt mit denen der Stablasten (`P1`).

- `kennung: str = ''`
- `knoten: str = ''`
- `lastfall: str = ''`
- `art: str = einer_von(KNOTENLASTEN, 'kraft')`
- `richtung: Lastrichtung = einer_von(KNOTENRICHTUNGEN, Lastrichtung.SENKRECHT)`
- `wert: float = 10.0` – kN oder kNm.

### ModulEintrag

```python
@dataclass
class ModulEintrag(Beschreibung)
```

Wie das E_eq eines Querschnitts aus einer Querschnittsanalyse entsteht:
bei `N` und `M`, Zug positiv und `M > 0` mit Zug unten -- auf der
gestrichelten Faser des Stabs. Gerechnet wie eine Momenten-Kruemmungs-
Linie der Analyse, mit Kriechzahl, Wertesatz und Rechenart wie dort
(Benutzer, 2026-10-23).

- `N: float = bereich(0.0, heisst='N für E_eq', einheit=KN)`
- `M: float = bereich(0.0, heisst='M für E_eq', einheit=KNM)`
- `kriechzahl: float = bereich(0.0, heisst='Kriechzahl φ', ab=0.0)`
- `werkstoffsatz: Werkstoffsatz = Werkstoffsatz.BEMESSUNG`
- `rechenart: Rechenart = einer_von(FASERARTEN, Rechenart.PARABEL)`

#### ModulEintrag.wahl

```python
@property
def wahl(self) -> Rechenwahl
```

### StabquerschnittEintrag

```python
@dataclass
class StabquerschnittEintrag(Beschreibung)
```

Ein Querschnitt der Staebe: nach Vorlage mit Massen in mm, mit Kennwerten
von Hand (`A` in mm², `I` in 10⁶ mm⁴), oder aus einer Platte oder
einer Querschnittsanalyse des Projekts (`bezug`). Sein E-Modul kommt
vom Material des Stabs oder steht als Zahl da -- dann gilt er fuer jeden
Stab mit diesem Querschnitt, aus welchem Material auch immer.

- `kennung: str = ''`
- `name: str = ''`
- `art: str = einer_von(QUERSCHNITTSARTEN, 'vorlage')`
- `vorlage: str = einer_von((v.schluessel for v in qs.VORLAGEN), qs.RECHTECK.schluessel)`
- `masse: Dict[str, float] = field(default_factory=dict)`
- `bezug: str = ''`
- `e_modul: str = einer_von(E_MODULE, 'material')` – Woher E kommt: `material` -- vom Material des Stabs --, `zahl`, dann `E`, oder `e_eq`, dann wie `eq` sagt.
- `E: float = bereich(30000.0, heisst='E-Modul E', einheit=N_PRO_MM2, ueber=0.0)` – Der E-Modul von Hand, N/mm² -- er gilt nur bei `e_modul = "zahl"`.
- `eq: ModulEintrag = field(default_factory=ModulEintrag)` – Wie das E_eq entsteht -- es gilt nur bei `e_modul = "e_eq"`.

#### StabquerschnittEintrag.E_von_hand

```python
@property
def E_von_hand(self) -> Optional[float]
```

Der E-Modul von Hand in N/mm² -- `None`, wenn er vom Material kommt.

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
- `eigengewicht: bool = False` – Ob der Lastfall das Eigengewicht aller Staebe bekommt -- von selbst, aus Dichte und Flaeche (Benutzer, 2026-10-23). Ein System hat einen davon.

### LastkombinationEintrag

```python
@dataclass
class LastkombinationEintrag(Beschreibung)
```

Eine Kombination: je Lastfall (Kennung) ein Beiwert, von Hand.

- `kennung: str = ''`
- `name: str = ''`
- `faktoren: Dict[str, float] = field(default_factory=dict)`

### StatikdiagrammEintrag

```python
@dataclass
class StatikdiagrammEintrag(Beschreibung)
```

Ein Diagramm der Statik-Analyse (Benutzer, 2026-10-23): ein Fall und was
es von ihm zeigt. Gerechnet wird damit nichts -- das System rechnet jeden
Fall; die Liste sagt nur, welche Diagramme rechts stehen.

- `fall: str = ''` – Die Kennung eines Lastfalls (`LF1`) oder einer Kombination (`LK1`).
- `groesse: str = einer_von(DIAGRAMMGROESSEN, 'M')`

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
- `eigengewicht: Optional[str] = None` – Der Name des Lastfalls, der das Eigengewicht der Staebe bekommt -- oder keiner.

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

Ohne Regeln, die das ganze Projekt aufhielten: was an einem System nicht
stimmt -- auch zwei Faelle gleichen Namens --, steht in seinen Meldungen
([[opencivil.projekt.balkensystem#BalkensystemEintrag.modell|modell]]), und die anderen Bauteile rechnen weiter.

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
- `diagramme: List[StatikdiagrammEintrag] = field(default_factory=list)`
- `beschreibung: str = ''` – Freier Text -- geht in keine Rechnung ein.

#### BalkensystemEintrag.materialien

```python
def materialien(self) -> List[str]
```

Jedes Material, auf das eine Linie zeigt. Jeder Verweis zaehlt, auch einer, der gerade nichts traegt: wer das
Material loescht, liesse ihn ins Leere zeigen, und spaetestens die
naechste Aenderung machte daraus einen Fehler beim Rechnen.
Dazu gehoert eine Linie, die gerade kein Stab ist: wird sie wieder einer,
nimmt sie ihr Material mit.

#### BalkensystemEintrag.bezuege

```python
def bezuege(self) -> List[str]
```

Die Platten und Querschnittsanalysen, deren Querschnitt ein Stab nimmt.

#### BalkensystemEintrag.alle_lasten

```python
def alle_lasten(self) -> List[Any]
```

Jede Last des Systems, auf den Linien und an den Knoten -- ihre Kennungen zaehlen zusammen.

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
und `material` dastehen; als Material auch
[[opencivil.projekt.balkensystem#Konstanten|MATERIAL_DES_QUERSCHNITTS]]. Weitere Felder wie
[[opencivil.projekt.balkensystem#SystemlinieEintrag|SystemlinieEintrag]].

#### BalkensystemEintrag.lager_an

```python
def lager_an(self, ort: Ort, art: str='gelenkig', **felder: Any) -> LagerEintrag
```

Ein Lager -- `gelenkig`, `verschieblich` oder `eingespannt`, Felder darueber.

#### BalkensystemEintrag.querschnitt

```python
def querschnitt(self, name: str, vorlage: str=qs.RECHTECK.schluessel, *, E: Optional[float]=None, **masse: float) -> StabquerschnittEintrag
```

Ein Querschnitt nach Vorlage -- Masse in mm, was fehlt nach ihrer
Vorgabe. Mit `E` in N/mm² rechnet er mit diesem E-Modul statt dem
seines Materials; so auch bei den beiden anderen.

#### BalkensystemEintrag.querschnitt_aus

```python
def querschnitt_aus(self, name: str, art: str, bezug: Any, *, E: Optional[float]=None, E_eq: Optional[Mapping[str, Any]]=None) -> StabquerschnittEintrag
```

Ein Querschnitt aus einer Platte (`platte`) oder einer
Querschnittsanalyse (`analyse`). Bei einer Analyse rechnet er mit
`E_eq` -- Felder wie [[opencivil.projekt.balkensystem#ModulEintrag|ModulEintrag]], etwa `{"M": 80}` --
mit ihrem aequivalenten E-Modul.

#### BalkensystemEintrag.querschnitt_mit_kennwerten

```python
def querschnitt_mit_kennwerten(self, name: str, *, A: float, I: float, E: Optional[float]=None) -> StabquerschnittEintrag
```

Ein Querschnitt mit Kennwerten von Hand -- A in mm², I in 10⁶ mm⁴.

#### BalkensystemEintrag.lastfall

```python
def lastfall(self, name: str, *, eigengewicht: bool=False) -> LastfallEintrag
```

#### BalkensystemEintrag.kombination

```python
def kombination(self, name: str, *faktoren: Tuple[Any, float]) -> LastkombinationEintrag
```

Eine Kombination -- je Lastfall (Eintrag oder Kennung) ein Beiwert: `(g, 1.35), (w, 1.5)`.

#### BalkensystemEintrag.diagramm

```python
def diagramm(self, fall: Any, groesse: str='M') -> StatikdiagrammEintrag
```

Ein Diagramm der Statik-Analyse -- `fall` ein Lastfall oder eine Kombination.

#### BalkensystemEintrag.stablast

```python
def stablast(self, lastfall: Any, linie: Any, art: Lastart=Lastart.LINIENLAST, wert: float=10.0, **felder: Any) -> StablastEintrag
```

Eine Last auf einer Linie -- `wert` ist `wert_a`; Felder wie [[opencivil.projekt.balkensystem#StablastEintrag|StablastEintrag]].

#### BalkensystemEintrag.knotenlast

```python
def knotenlast(self, lastfall: Any, ort: Ort, wert: float=10.0, *, art: str='kraft', richtung: Lastrichtung=Lastrichtung.SENKRECHT) -> KnotenlastEintrag
```

#### BalkensystemEintrag.teilen

```python
def teilen(self, kennung: str, stelle: float) -> SystemlinieEintrag
```

Teilt eine Linie bei `stelle` m ab ihrem Anfang: sie endet dort, und
eine neue laeuft weiter zum alten Ende -- mit ihren Eigenschaften. Die
Lasten gehen mit: eine verteilte liegt danach auf beiden Haelften, mit
dem Wert an der Schnittstelle, die auf der zweiten mit einer eigenen
Kennung; eine Einzellast bleibt dort, wo sie steht, ihre Stelle in %
der neuen Haelfte. Das Gelenk am Ende wandert mit ans neue Ende; an der
Schnittstelle ist die Linie durchlaufend.

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
def neu(cls, kennung: str, name: str) -> 'BalkensystemEintrag'
```

Ein frisches System, wie der Benutzer es angelegt bekommt: ohne
Knoten, Linie, Lager und Querschnitt (Benutzer, 2026-10-19), aber mit
den Lastfaellen Eigengewicht -- es kommt von selbst --, Auflast und
Nutzlast, die beiden ohne Last, und den Kombinationen GZT mit 1.35,
1.35 und 1.5 und GZG mit je 1.0 (Benutzer, 2026-10-23). Dazu die
Diagramme M, V und N der GZT und die Verschiebung der GZG.


## Konstanten

- `HALT = ('frei', 'fest', 'feder')` – Wie ein Lager oder Linienlager je Richtung haelt.
- `EINHEIT_DER_LAST = {Lastart.LINIENLAST: KN_PRO_M, Lastart.EINZELLAST: KN, Lastart.MOMENT…` – Die Einheit jeder Last in der Beschreibung, nach ihrer Art -- an einem Stab oder Knoten. Umgerechnet wird beim Bauen, mit diesen.
- `EINHEIT_DER_FEDER = {'k_x': KN_PRO_M, 'k_z': KN_PRO_M, 'k_phi': KNM_PRO_RAD, 'k_quer': KN…` – Die Einheit jeder Feder, nach ihrem Feld: Lager in kN/m und kNm/rad, Bettung in kN/m je m Stab.
- `KNOTENLASTEN = ('kraft', 'moment')` – Was fuer Lasten an einem Knoten liegen koennen; an einem Stab jede [[opencivil.stabwerk.modell#Lastart|Lastart]].
- `KNOTENRICHTUNGEN = (Lastrichtung.SENKRECHT, Lastrichtung.WAAGRECHT)` – Wohin eine Kraft an einem Knoten zeigt -- nur senkrecht oder waagrecht.
- `QUERSCHNITTSARTEN = ('vorlage', 'kennwerte', 'platte', 'analyse')` – Woher ein Querschnitt kommt.
- `KENNWERTE = ('A', 'I')` – Die Kennwerte eines Querschnitts von Hand: A in mm², I in 10⁶ mm⁴.
- `E_MODULE = ('material', 'zahl', 'e_eq')` – Woher der E-Modul eines Querschnitts kommt: vom Material des Stabs -- E_cm beim Beton, E_s beim Stahl --, als Zahl von Hand, unabhaengig vom Material, oder als E_eq der Querschnittsanalyse bei N und M (Benutzer, 2026-10-23).
- `E_EQ_ARTEN = ('analyse',)` – Die Arten eines Querschnitts, die ein E_eq haben: nur der gezeichnete Querschnitt hat eine Momenten-Kruemmungs-Linie mit seiner Bewehrung.
- `MATERIAL_DES_QUERSCHNITTS = 'querschnitt'` – Das Material einer Linie, das ihr Querschnitt mitbringt: der Beton der Platte oder der Querschnittsanalyse (Benutzer, 2026-10-23). Es kann keine Kennung im Projekt sein -- die beginnen mit ihrer Vorsilbe und einer Zahl.
- `MIT_MATERIAL = ('platte', 'analyse')` – Die Arten eines Querschnitts, die ein Material mitbringen: ein Bauteil des Projekts. Einer nach Vorlage oder von Hand ist nur eine Form.
- `DIAGRAMMGROESSEN = ('M', 'V', 'N', 'verschiebung', 'verdrehung', 'lagerkraefte')` – Was ein Diagramm der Statik-Analyse zeigt: je Stab den Verlauf einer Schnittgroesse oder der Verdrehung, das verschobene System oder die Lagerkraefte.
- `LAGERARTEN = {'gelenkig': ('fest', 'fest', 'frei'), 'verschieblich': ('frei', 'fes…` – Die Vorwahlen eines Lagers -- je Richtung frei oder fest.
- `Ort = Union[str, Sequence[float]]` – Ein Punkt in m -- oder die Kennung eines Knotens, der dort liegt.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.netz]]
- [[opencivil.querschnitt.gesetzwahl]]
- [[opencivil.stabwerk.modell]]
- [[opencivil.stabwerk.querschnitte]]
- [[opencivil.stabwerk.system]]

## Gebraucht von

- [[opencivil.projekt]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.balkensystem]]
- [[opencivil.projekt.projekt]]
- [[opencivil.web.api]]
