---
erzeugt: d47a2d4fd20a
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
Richtung, die an der Linie haengt, mit umgekehrtem Vorzeichen – welche,
sagt die Beschreibung ([[opencivil.projekt.staebe#MitStaeben._kehrt_um|MitStaeben._kehrt_um]]).


## QUERSCHNITTE

Ein Querschnitt der Staebe ist in beiden Systemen nach Vorlage, ein
Stahlprofil aus der Tabelle, mit Kennwerten von Hand oder aus einer Platte
oder Querschnittsanalyse des Projekts ([[opencivil.projekt.staebe#StabquerschnittBasis|StabquerschnittBasis]]);
welche Kennwerte, sagt das System. Seit 2026-11-18 nimmt ihn auch das
3D-Balkensystem aus einer Platte oder Analyse (Benutzer: «genau gleich,
einfach einmal in 3D»).

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

Fuer den Schalter und die Zeile des Querschnitts – der lange Name
steht im Titel des Schalters. «QS Analyse», nicht «Analyse»: im
Balkensystem heisst auch die Statik-Analyse so (Benutzer, 2026-11-16).
Ohne «Aus»: der Schalter steht unter «A und I aus» (Benutzer,
2026-11-18).

#### Querschnittsart.aus_bauteil

```python
@property
def aus_bauteil(self) -> bool
```

Ob er ein Bauteil des Projekts nimmt, eine Platte oder eine
Querschnittsanalyse. Nur dann bringt er ein Material mit, den Beton
des Bauteils, und nur dann hat er ein E_eq – eine
Momenten-Kruemmungs-Linie mit ihrer Bewehrung, bei einer Platte immer
in x-Richtung, Zug unten (Benutzer, 2026-10-24). Einer nach Vorlage
oder von Hand ist nur eine Form.

#### Querschnittsart.bauteil

```python
@property
def bauteil(self) -> str
```

Wie das Bauteil heisst, aus dem er seine Werte nimmt – leer bei einer Form.

### ModulEintrag

```python
@dataclass
class ModulEintrag(Beschreibung, JeMaterial)
```

Wie das E_eq eines Querschnitts aus einer Platte oder Querschnittsanalyse
entsteht: bei `N` und `M`, Zug positiv und `M > 0` mit Zug unten –
auf der gestrichelten Faser des Stabs, im Raum an der Seite +z, wo M_y
zieht; bei einer Platte immer in x-Richtung, und `M` zieht unten
(Benutzer, 2026-10-24). Gerechnet wie eine Momenten-Kruemmungs-Linie
ihrer Spannung-Dehnung-Analyse, mit Kriechzahl, Werten je Material und
Rechenart je Beton wie dort (Benutzer, 2026-10-23, je Material
2026-11-20, je Beton 2026-11-25).

- `N: float = bereich(0.0, heisst='N für E_eq', einheit=KN)`
- `M: float = bereich(0.0, heisst='M für E_eq', einheit=KNM)`
- `kriechzahl: float = bereich(0.0, heisst='Kriechzahl φ', ab=0.0)`
- `werkstoffsaetze: Dict[str, Werkstoffsatz] = je_material(Werkstoffsatz.BEMESSUNG)`
- `rechenarten: Dict[str, Rechenart] = je_material(Rechenart.PARABEL, FASERARTEN)`

### StabquerschnittBasis

```python
@dataclass
class StabquerschnittBasis(Beschreibung)
```

Ein Querschnitt der Staebe: nach Vorlage mit Massen in mm (`masse`),
ein Stahlprofil aus der Tabelle (`profil`), mit Kennwerten von Hand
(`kennwerte`) oder aus einer Platte oder Querschnittsanalyse des
Projekts (`platte`, `analyse`). E und G kommen vom Material des
Stabs; nimmt der das Material des Querschnitts, sagt `e_modul`, welches E.

Jede Art hat ihre eigenen Felder: wer umschaltet, setzt nur `art`, und
nach dem Zurueckschalten stehen die alten Zahlen wieder da (Benutzer,
2026-11-19). Bis dahin teilten sich die Arten `masse` und `bezug`,
und die Oberflaeche raeumte beim Umschalten ab, was [[opencivil.projekt.staebe#StabquerschnittBasis.fehler|fehler]] sonst
abwies – dreimal nachgebessert.

- `IM_ORT = 'Querschnitt'`
- `KENNWERTE: ClassVar[Tuple[Kennwert, ...]]` – Die Kennwerte von Hand, wie die Rechnung sie nimmt – mit ihrer Grenze.
- `kennung: str = ''`
- `name: str = ''`
- `art: Querschnittsart = einer_von(tuple(Querschnittsart), Querschnittsart.VORLAGE)`
- `vorlage: str = einer_von((v.schluessel for v in qs.VORLAGEN), qs.RECHTECK.schluessel)`
- `masse: Dict[str, float] = field(default_factory=dict)` – Die Masse der Vorlage in mm – was fehlt, gilt mit ihrer Vorgabe.
- `kennwerte: Dict[str, float] = field(default_factory=dict)` – `A` in mm², Traegheitsmomente in 10⁶ mm⁴ – welche, sagt [[opencivil.projekt.staebe#StabquerschnittBasis|KENNWERTE]].
- `profil: str = 'IPE 300'` – Der Name des Stahlprofils ([[opencivil.stahlprofile.tabelle]]), aus Vollstahl mit seinen Massen: «FL 100 x 10». Kein Wahlfeld, damit die Meldung nicht alle Profile aufzaehlt: einen Namen, der nicht geht, meldet der Aufbau mit dem Grund, wie eine Platte, die es nicht gibt.
- `platte: str = ''` – Die Kennung der Platte, aus der er kommt.
- `analyse: str = ''` – Die Kennung der Querschnittsanalyse, aus der er kommt.
- `e_modul: str = einer_von(E_MODULE, 'e0')` – Welches E ein Stab hat, der das Material dieses Querschnitts nimmt: `e0` – E_cm seines Betons – oder `e_eq`, wie `eq` sagt. Ein Material bringt nur einer aus einer Platte oder Analyse mit; bei einer Form wartet die Wahl, bis er zurueckschaltet.
- `eq: ModulEintrag = teil(ModulEintrag, heisst='E_eq')` – Wie das E_eq entsteht – es gilt nur bei `e_modul = "e_eq"`.

#### StabquerschnittBasis.neu

```python
@classmethod
def neu(cls) -> 'StabquerschnittBasis'
```

Ein frischer Querschnitt, wie die Oberflaeche ihn anlegt: ein Rechteck mit seinen Vorgaben.

#### StabquerschnittBasis.bezug

```python
@property
def bezug(self) -> str
```

Die Kennung der Platte oder Analyse, aus der er kommt – leer bei einer Form.

#### StabquerschnittBasis.biegeachse

```python
@property
def biegeachse(self) -> Optional[Any]
```

Um welche Achse sich ein Profil im ebenen Rahmen biegt, eine
[[opencivil.projekt.balkensystem#Profilachse|Profilachse]] – hier keine:
im Raum biegt es sich um beide.

#### StabquerschnittBasis.stabvorlage

```python
def stabvorlage(self) -> qs.Stabvorlage
```

#### StabquerschnittBasis.masse_mit_vorgaben

```python
def masse_mit_vorgaben(self) -> Dict[str, float]
```

Die Masse der Vorlage – was fehlt, mit ihrer Vorgabe.

#### StabquerschnittBasis.fehler

```python
def fehler(self) -> Optional[str]
```

Was an Massen, Kennwerten oder der Wahl nicht geht – `None`, wenn
alles geht. Ein Mass, das die Vorlage nicht kennt, ist ein Tippfehler:
bis 2026-10-16 stand `B=500` still da, und gerechnet wurde mit b = 300.
Ohne gewaehlte Platte oder Analyse rechnet der Querschnitt nicht, das
Projekt schon – bis 2026-11-19 scheiterte daran das ganze Projekt,
gleich nach dem Umschalten, und die Oberflaeche zeigte weiter die
Werte der vorherigen Art.

### MitStaeben

```python
class MitStaeben
```

Der Baukasten eines Stabwerks – fuer eine Beschreibung mit `knoten`,
`linien`, `lager`, `knotenlasten`, `stabmaterialien`,
`querschnitte` und `diagramme`. Die Klassen ihrer Teile, die Achsen
und die Arten der Lager stehen in ihr als Klassenattribute.

- `BEZEICHNUNG: str`
- `ACHSEN: Tuple[str, ...]` – Wie die Koordinaten eines Knotens heissen – `("x", "z")` in der Ebene.
- `LAGERFELDER: Tuple[str, ...]` – Die Richtungen eines Lagers, in der Folge der Vorwahlen in [[opencivil.projekt.staebe#MitStaeben|LAGERARTEN]] – Felder des Lagers wie des Lagers im Rechenkern.
- `LAGERARTEN: Mapping[str, Tuple[str, ...]]` – Die Vorwahlen eines Lagers – je Richtung frei oder fest.
- `LINIENLAGER: Tuple[str, ...]` – Die Richtungen eines Linienlagers – Felder der Linie wie des Stabs im Rechenkern.
- `ERSTE_MATERIALIEN = {'stabmaterialien/0/stoff': 'beton'}` – Das Material M1 eines frischen Systems ([[opencivil.projekt.staebe#MitStaeben.neu|neu]]) nimmt den ersten Beton des Projekts – damit ein gezeichneter Stab gleich eines hat.
- `NEUE_DIAGRAMME: Tuple[str, ...]` – Was ein frisches System von der GZT zeigt – dazu die Verschiebung der GZG.
- `LAUFRICHTUNGEN: Tuple[Tuple[float, ...], ...]` – Wohin eine neue Linie laeuft, wie herum sie auch gezeichnet ist: in die erste dieser Richtungen, auf der sie nicht senkrecht steht. Keine: wie gezeichnet. Die Oberflaeche legt danach Anfang und Ende.
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
den Lastfaellen Eigengewicht – es kommt von selbst –, Auflast und
Nutzlast, die beiden ohne Last, und den Kombinationen GZT mit 1.35,
1.35 und 1.5 und GZG mit je 1.0 (Benutzer, 2026-10-23), dazwischen
«GZT günstig» mit 0.80 auf den staendigen Lasten (Benutzer,
2026-11-27). Dazu die Diagramme [[opencivil.projekt.staebe#MitStaeben|NEUE_DIAGRAMME]] der GZT und die
Verschiebung der GZG, und das Material M1, ein Beton: welcher, sagt
[[opencivil.projekt.staebe#MitStaeben|ERSTE_MATERIALIEN]].

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

Jedes Material des Projekts, auf das ein Material des Systems zeigt –
auch eines, das gerade keinen Stab traegt: wer es loescht, liesse es
ins Leere zeigen, und spaetestens die naechste Aenderung machte
daraus einen Fehler beim Rechnen.

#### MitStaeben.alle_lasten

```python
def alle_lasten(self) -> List[Any]
```

Jede Last des Systems, auf den Linien und an den Knoten – ihre Kennungen zaehlen zusammen.

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

Wo ein Punkt auf einer Linie liegt, in m ab ihrem Anfang – auf die Linie gelotet.

#### MitStaeben.netz

```python
def netz(self) -> Netz
```

#### MitStaeben._gelesen

```python
def _gelesen(self, cls: type, roh: Dict[str, Any], liste: str, neben: Sequence[Any]) -> Any
```

Ein neues Element der Liste `liste` aus `roh`, gelesen wie aus der
Datei – und gemeldet, wie die Datei es nennte: «L3», «Material
'Beton'» ([[opencivil.projekt.lesen#element_ort|element_ort]]). `neben` sind
die Elemente, zu denen es kommt.

#### MitStaeben.linie

```python
def linie(self, von: Ort, bis: Ort, *, querschnitt: Any=None, material: Any=None, **felder: Any) -> Any
```

Eine Linie von `von` nach `bis` – ein Stab, sobald `querschnitt`
und `material` dastehen: ein Material des Systems ([[opencivil.projekt.staebe#MitStaeben.beton|beton]],
[[opencivil.projekt.staebe#MitStaeben.baustahl|baustahl]], [[opencivil.projekt.staebe#MitStaeben.eigenes_material|eigenes_material]]). Weitere Felder wie die
Klasse der Linien.

#### MitStaeben.lager_an

```python
def lager_an(self, ort: Ort, art: str='gelenkig', **felder: Any) -> Any
```

Ein Lager – eine der [[opencivil.projekt.staebe#MitStaeben|LAGERARTEN]], einzelne Felder darueber.

#### MitStaeben.beton

```python
def beton(self, beton: Any) -> Any
```

Das Material des Systems aus einem Beton des Projekts (Eintrag oder
Kennung) – das schon da ist, sonst ein neues. Ein Beton, der noch
keinen gewaehlt hat wie M1 eines frischen Systems ([[opencivil.projekt.staebe#MitStaeben.neu|neu]]),
bekommt diesen.

#### MitStaeben.baustahl

```python
def baustahl(self, stahl: Any) -> Any
```

Das Material des Systems aus einem Baustahl des Projekts – siehe [[opencivil.projekt.staebe#MitStaeben.beton|beton]].

#### MitStaeben.holz

```python
def holz(self, holz: Any) -> Any
```

Das Material des Systems aus einem Holz des Projekts – siehe [[opencivil.projekt.staebe#MitStaeben.beton|beton]].

#### MitStaeben.eigenes_material

```python
def eigenes_material(self, name: str, **werte: float) -> Any
```

Ein eigenes Material des Systems – E in N/mm², die Dichte in kg/m³, Felder wie seine Klasse.

#### MitStaeben.querschnitt

```python
def querschnitt(self, name: str, vorlage: str=qs.RECHTECK.schluessel, **masse: float) -> Any
```

Ein Querschnitt nach Vorlage – Masse in mm, was fehlt nach ihrer Vorgabe.

#### MitStaeben.stahlprofil

```python
def stahlprofil(self, name: str, profil: str, **felder: Any) -> Any
```

Ein Stahlprofil aus der Tabelle, «HEB 300» – Felder wie die Klasse der Querschnitte.

#### MitStaeben.querschnitt_mit_kennwerten

```python
def querschnitt_mit_kennwerten(self, name: str, **kennwerte: float) -> Any
```

Ein Querschnitt mit Kennwerten von Hand – A in mm², Traegheitsmomente in 10⁶ mm⁴.

#### MitStaeben.querschnitt_aus

```python
def querschnitt_aus(self, name: str, art: str, bezug: Any, *, E_eq: Optional[Mapping[str, Any]]=None) -> Any
```

Ein Querschnitt aus einer Platte (`platte`) oder einer
Querschnittsanalyse (`analyse`). Ein Stab «gemäss Querschnitt»
rechnet mit `E_eq` – Felder wie [[opencivil.projekt.staebe#ModulEintrag|ModulEintrag]], etwa
`{"M": 80}` – mit ihrem aequivalenten E-Modul.

#### MitStaeben.bezuege

```python
def bezuege(self) -> List[str]
```

Die Platten und Querschnittsanalysen, deren Querschnitt ein Stab nimmt.

#### MitStaeben.diagramm

```python
def diagramm(self, fall: Any, groesse: str) -> Any
```

Ein Diagramm der Statik-Analyse – `fall` ein Lastfall oder eine Kombination.

#### MitStaeben.stablast

```python
def stablast(self, lastfall: Any, linie: Any, art: Lastart=Lastart.LINIENLAST, wert: float=10.0, **felder: Any) -> Any
```

Eine Last auf einer Linie – `wert` ist `wert_a`; Felder wie die Klasse der Stablasten.

#### MitStaeben.knotenlast

```python
def knotenlast(self, lastfall: Any, ort: Ort, wert: float=10.0, **felder: Any) -> Any
```

Eine Last an einem Knoten – eine Kraft oder, `art="moment"`, ein Moment; Felder wie ihre Klasse.

#### MitStaeben.teilen

```python
def teilen(self, kennung: str, stelle: float) -> Any
```

Teilt eine Linie bei `stelle` m ab ihrem Anfang: sie endet dort, und
eine neue laeuft weiter zum alten Ende – mit ihren Eigenschaften. Die
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

- `Ort = Union[str, Sequence[float]]` – Ein Punkt in m – oder die Kennung eines Knotens, der dort liegt.
- `Punkt = Tuple[float, ...]` – Ein Punkt in m, mit so vielen Koordinaten, wie das System Achsen hat.
- `E_MODULE = ('e0', 'e_eq')` – Womit ein Stab rechnet, der das Material seines Querschnitts nimmt: E₀, das E_cm des Betons, den der Querschnitt mitbringt, oder das E_eq der Platte oder Querschnittsanalyse bei N und M (Benutzer, 2026-10-24). Einen E-Modul von Hand hat ein Querschnitt nicht mehr – den hat ein eigenes Material.
- `MATERIAL_DES_QUERSCHNITTS = 'querschnitt'` – Das Material einer Linie, das ihr Querschnitt mitbringt: der Beton der Platte oder der Querschnittsanalyse (Benutzer, 2026-10-23). Es kann keine Kennung eines Materials sein – die beginnen mit «M» und einer Zahl.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.wahl]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.faelle]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.netz]]
- [[opencivil.querschnitt.gesetzwahl]]
- [[opencivil.stabwerk.modell]]
- [[opencivil.stabwerk.querschnitte]]
- [[opencivil.stabwerk.stabquerschnitt]]
- [[opencivil.stahlprofile.tabelle]]

## Gebraucht von

- [[opencivil.projekt.aufbau.balkensystem]]
- [[opencivil.projekt.aufbau.balkensystem3d]]
- [[opencivil.projekt.balkensystem]]
- [[opencivil.projekt.balkensystem3d]]
- [[opencivil.projekt.beispiele]]
- [[opencivil.web.dienst]]
- [[opencivil.web.systemkatalog]]
