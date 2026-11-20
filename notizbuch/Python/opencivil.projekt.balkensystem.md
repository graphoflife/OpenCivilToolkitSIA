---
erzeugt: 857888643a62
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/balkensystem.py
> ein 2D-Balkensystem, wie die Oberflaeche es beschreibt.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/balkensystem.py)

## VERANTWORTUNG

Der [[opencivil.projekt.balkensystem#BalkensystemEintrag|BalkensystemEintrag]]: ein ebener Rahmen aus Knoten und Linien,
Lagern und Lasten, mit seinen Materialien, Querschnitten, Lastfaellen und
Kombinationen
-- als speicherbare Datenklasse wie die Querschnittsanalyse
([[opencivil.projekt.querschnittsanalyse]]). Was es mit dem
3D-Balkensystem teilt -- zeichnen ohne Oberflaeche, teilen, umkehren, die
Felder eines Querschnitts --, steht in [[opencivil.projekt.staebe]].
Gerechnet wird in [[opencivil.stabwerk]].


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

### federfeld

```python
def federfeld(heisst: str, einheit: Einheit) -> Any
```

Das Feld einer Feder: Lager in kN/m und kNm/rad, Bettung in kN/m je m
Stab -- nie negativ. Null nimmt das Feld an, frei heisst die Richtung
damit nicht: eine Feder ohne Steifigkeit meldet das System.

### Profilachse

```python
class Profilachse(Wahl)
```

Um welche Achse ein Stahlprofil sich im Rahmen biegt: um `y`, die
starke -- der Steg liegt in der Ebene des Rahmens --, oder um `z`.

- `Y = 'y'`
- `Z = 'z'`

#### Profilachse.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Profilachse.kurz

```python
@property
def kurz(self) -> str
```

Fuer den Schalter -- der lange Name steht in seinem Titel.

#### Profilachse.traegheit

```python
@property
def traegheit(self) -> str
```

Der Kurzname des Traegheitsmoments der Profilform, das dann `I` ist.

### SystemknotenEintrag

```python
@dataclass
class SystemknotenEintrag(Beschreibung)
```

Ein Punkt des Systems, in m.

- `kennung: str = ''`
- `x: float = bereich(0.0, heisst='x', einheit=M)`
- `z: float = bereich(0.0, heisst='z', einheit=M)`

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
- `wert_a: float = bereich(10.0, heisst='Wert am Anfang')`
- `wert_b: Optional[float] = bereich(None, heisst='Wert am Ende')`
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
- `material: str = ''` – Kennung eines Materials des Systems (`M1`) -- oder [[opencivil.projekt.staebe#Konstanten|MATERIAL_DES_QUERSCHNITTS]]: das Material, das eine Platte oder Querschnittsanalyse als Querschnitt mitbringt.
- `gelenk_anfang: bool = False`
- `gelenk_ende: bool = False`
- `quer: str = einer_von(HALT, 'frei')`
- `k_quer: float = federfeld('Bettung quer', KN_PRO_M2)`
- `laengs: str = einer_von(HALT, 'frei')`
- `k_laengs: float = federfeld('Bettung längs', KN_PRO_M2)`
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
- `k_x: float = federfeld('Federsteifigkeit k_x', KN_PRO_M)`
- `z: str = einer_von(HALT, 'fest')`
- `k_z: float = federfeld('Federsteifigkeit k_z', KN_PRO_M)`
- `phi: str = einer_von(HALT, 'frei')`
- `k_phi: float = federfeld('Federsteifigkeit k_φ', KNM_PRO_RAD)`

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
- `wert: float = bereich(10.0, heisst='Wert')` – kN oder kNm, nach der Art; ohne Grenze wie jede Last.

### StabmaterialEintrag

```python
@dataclass
class StabmaterialEintrag(Beschreibung)
```

Ein Material der Staebe (Benutzer, 2026-10-24): ein Beton oder Baustahl
des Projekts (`stoff`) -- E und Dichte von ihm, siehe
[[opencivil.stabwerk.rechnung#Konstanten|STABKENNWERTE]] -- oder ein eigenes
mit `E` und `rho` von Hand.

- `kennung: str = ''`
- `art: str = einer_von(STABMATERIALARTEN, 'beton')`
- `stoff: str = ''` – Die Kennung des Betons oder Baustahls im Projekt (`b1`, `st1`) -- nicht bei `eigen`.
- `name: str = ''` – Wie ein eigenes heisst; ein Beton oder Baustahl heisst wie im Projekt.
- `E: float = bereich(200000.0, heisst='E-Modul E', einheit=N_PRO_MM2, ueber=0.0)` – N/mm² -- nur bei `eigen`.
- `rho: float = bereich(7850.0, heisst='Dichte ρ', einheit=KG_PRO_M3, ab=0.0)` – kg/m³, fuer das Eigengewicht -- nur bei `eigen`.

### StabquerschnittEintrag

```python
@dataclass
class StabquerschnittEintrag(StabquerschnittBasis)
```

Ein Querschnitt der Staebe in der Ebene: ein Stahlprofil biegt sich um `achse`.

- `KENNWERTE = EBEN`
- `achse: Profilachse = Profilachse.Y`

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

### BalkensystemEintrag

```python
@dataclass
class BalkensystemEintrag(MitStaeben, MitFaellen, BauteilEintrag)
```

Ein ebener Rahmen: Knoten, Linien, Lager, Lasten, Querschnitte, Lastfaelle, Kombinationen.

Ohne Regeln, die das ganze Projekt aufhielten: was an einem System nicht
stimmt -- auch zwei Faelle gleichen Namens --, steht in seinen Meldungen
([[opencivil.projekt.balkensystem#BalkensystemEintrag|modell]]), und die anderen Bauteile rechnen weiter.

- `BEZEICHNUNG = 'Balkensystem'`
- `kennung: str`
- `name: str`
- `knoten: List[SystemknotenEintrag] = field(default_factory=list)`
- `linien: List[SystemlinieEintrag] = field(default_factory=list)`
- `lager: List[LagerEintrag] = field(default_factory=list)`
- `knotenlasten: List[KnotenlastEintrag] = field(default_factory=list)`
- `stabmaterialien: List[StabmaterialEintrag] = field(default_factory=list)`
- `querschnitte: List[StabquerschnittEintrag] = field(default_factory=list)`
- `lastfaelle: List[LastfallEintrag] = field(default_factory=list)`
- `kombinationen: List[LastkombinationEintrag] = field(default_factory=list)`
- `diagramme: List[StatikdiagrammEintrag] = field(default_factory=list)`
- `beschreibung: str = ''` – Freier Text -- geht in keine Rechnung ein.
- `ACHSEN = ('x', 'z')`
- `LAGERFELDER = ('x', 'z', 'phi')`
- `LINIENLAGER = ('quer', 'laengs')`
- `LAGERARTEN = LAGERARTEN`
- `NEUE_DIAGRAMME = ('M', 'V', 'N')`
- `LAUFRICHTUNGEN = ((1.0, 0.0), (0.0, -1.0))` – Nach rechts, steht sie senkrecht, nach unten: so liegt die gestrichelte Faser einer neuen Linie unten bzw. links (Benutzer, 2026-10-24). Wohin die Faser zeigt, legt der Kern ([[opencivil.stabwerk3d.stab#achsen_eben|achsen_eben]]); ein Test prueft beides zusammen.
- `KNOTEN = SystemknotenEintrag`
- `LINIE = SystemlinieEintrag`
- `LAGER = LagerEintrag`
- `STABLAST = StablastEintrag`
- `KNOTENLAST = KnotenlastEintrag`
- `MATERIAL = StabmaterialEintrag`
- `QUERSCHNITT = StabquerschnittEintrag`
- `DIAGRAMM = StatikdiagrammEintrag`

#### BalkensystemEintrag._kehrt_um

```python
def _kehrt_um(self, last: StablastEintrag) -> bool
```

Die gestrichelte Faser liegt nach dem Umkehren auf der anderen Seite:
eine Kraft quer oder laengs kehrt mit ihr um. Senkrecht, waagrecht und
Momente -- sie drehen im Gegenuhrzeigersinn -- aendern sich nicht.

#### BalkensystemEintrag.stahlprofil

```python
def stahlprofil(self, name: str, profil: str, achse: str='y') -> StabquerschnittEintrag
```

Ein Stahlprofil aus der Tabelle, «HEB 300» -- gebogen um `achse`, y die starke.


## Konstanten

- `HALT = ('frei', 'fest', 'feder')` – Wie ein Lager oder Linienlager je Richtung haelt.
- `EINHEIT_DER_LAST = {Lastart.LINIENLAST: KN_PRO_M, Lastart.EINZELLAST: KN, Lastart.MOMENT…` – Die Einheit jeder Last in der Beschreibung, nach ihrer Art -- an einem Stab oder Knoten. Umgerechnet wird beim Bauen, mit diesen.
- `KNOTENLASTEN = ('kraft', 'moment')` – Was fuer Lasten an einem Knoten liegen koennen; an einem Stab jede [[opencivil.stabwerk.modell#Lastart|Lastart]].
- `KNOTENRICHTUNGEN = (Lastrichtung.SENKRECHT, Lastrichtung.WAAGRECHT)` – Wohin eine Kraft an einem Knoten zeigt -- nur senkrecht oder waagrecht.
- `STABMATERIALARTEN = (*(art.value for art in STABKENNWERTE), 'eigen')` – Was ein Material des Systems ist: ein Beton oder Baustahl des Projekts -- E und Dichte von ihm, nicht zu aendern -- oder ein eigenes mit E und Dichte von Hand (Benutzer, 2026-10-24; Baustahl seit 2026-11-15). Betonstahl ist keines: aus ihm ist kein Stab. Welche Arten des Projekts es gibt, sagen die Kennwerte, die ein Stab aus ihnen nimmt.
- `DIAGRAMMGROESSEN = ('N', 'V', 'M', 'verschiebung', 'verdrehung', 'lagerkraefte')` – Was ein Diagramm der Statik-Analyse zeigt: je Stab den Verlauf einer Schnittgroesse oder der Verdrehung, das verschobene System oder die Lagerkraefte. N, V, M wie im Raum und in der Tabelle der Grenzwerte -- bis 2026-11-19 stand M zuerst.
- `LAGERARTEN = {'gelenkig': ('fest', 'fest', 'frei'), 'verschieblich': ('frei', 'fes…` – Die Vorwahlen eines Lagers -- je Richtung frei oder fest.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.wahl]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.faelle]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.staebe]]
- [[opencivil.stabwerk.modell]]
- [[opencivil.stabwerk.rechnung]]
- [[opencivil.stabwerk.stabquerschnitt]]

## Gebraucht von

- [[opencivil.projekt]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.balkensystem]]
- [[opencivil.projekt.balkensystem3d]]
- [[opencivil.projekt.beispiele]]
- [[opencivil.projekt.projekt]]
- [[opencivil.web.api]]
- [[opencivil.web.systemkatalog]]
