---
erzeugt: 464fdb02d7f8
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/aufbau/balkensystem.py
> ein Balkensystem wird Rechnung.
> Paket [[opencivil.projekt.aufbau]] · [Quelltext](../../opencivil/projekt/aufbau/balkensystem.py)

## VERANTWORTUNG

Aus einem [[opencivil.projekt.balkensystem#BalkensystemEintrag|BalkensystemEintrag]] das
Stabwerk in SI mit seinen Meldungen ([[opencivil.projekt.aufbau.balkensystem#modell_von|modell_von]]) und daraus die
Rechnung mit aufgeloesten Materialien und Querschnitten ([[opencivil.projekt.aufbau.balkensystem#bauen|bauen]]). Ein
Material ist ein Beton, Baustahl oder Holz des Projekts oder ein eigenes. Die Art eines
Querschnitts wird hier aufgeloest, einmal: je Art eine Klasse
([[opencivil.stabwerk.stabquerschnitt|stabquerschnitt]]). Ein Querschnitt kann eine
Platte oder eine Querschnittsanalyse des Projekts nehmen; die muessen dann
schon gebaut sein -- darum kommt das Balkensystem in
[[opencivil.projekt.aufbau#Konstanten|BAUTEILE]] nach ihnen. Von dort kommt auch
das Material einer Linie «gemäss Querschnitt»: der Beton der Platte oder
der Analyse.


## GETEILT MIT DEM RAUM

Was das 3D-Balkensystem ([[opencivil.projekt.aufbau.balkensystem3d|balkensystem3d]])
gleich macht, steht hier und wird dort benutzt: die [[opencivil.projekt.aufbau.balkensystem#Uebersetzung|Uebersetzung]]
prueft Faelle und Kennungen und uebersetzt Stabfelder, Lager und Lasten;
[[opencivil.projekt.aufbau.balkensystem#stabwerk_bauen|stabwerk_bauen]] loest Materialien und Querschnitte auf;
[[opencivil.projekt.aufbau.balkensystem#stabquerschnitt_von|stabquerschnitt_von]] loest die Art eines Querschnitts auf -- eine
Vorlage, ein Profil oder Kennwerte von Hand ([[opencivil.projekt.aufbau.balkensystem#form_von|form_von]]), eine Platte
oder eine Querschnittsanalyse.

## Inhalt

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

### Uebersetzung

```python
class Uebersetzung
```

Was ein Stabwerk in der Ebene und eines im Raum gleich in SI uebersetzen
und pruefen: Kennungen, Faelle, Querschnitte, Paare aus Querschnitt und
Material, Lager, Federn, Lasten und Kombinationen -- in dieser Folge
melden sie, was nicht stimmt. Was der Raum anders macht, baut die
Funktion `modell_von` des Systems mit den Klassen ihres Rechenkerns.

Ein Stab ohne Querschnitt oder Material -- oder mit einem Material,
das es im System nicht gibt --, ein Querschnitt mit unmoeglichen
Massen und eine Feder ohne Steifigkeit sind Fehler, die die Meldungen
nennen: gerechnet wird dann nicht -- und nicht etwa mit einem Stab
weniger. Ob ein Material traegt, weiss erst der Aufbau: er kennt die
Materialien des Projekts. Eine Last, deren Lastfall es nicht gibt, und ein
Beiwert dafuer bleiben mit einem Hinweis weg.

#### Uebersetzung.melden

```python
def melden(self, text: str, *elemente: str, fehler: bool=True, unfertig: bool=False) -> None
```

#### Uebersetzung.halt

```python
def halt(self, teil: Any, richtung: str) -> Halt
```

Wie ein Lager oder eine Linie in `richtung` haelt -- die Feder im
Feld `k_<richtung>`, in dessen Einheit.

#### Uebersetzung.stab

```python
def stab(self, l: Any) -> Dict[str, Any]
```

Was ein Stab des Rechenkerns von seiner Linie hat, Linienlager
inbegriffen -- und, wenn sie ein Stab ist, ihr Paar aus Querschnitt
und Material, geprueft.

#### Uebersetzung.lager

```python
def lager(self, klasse: type) -> List[Any]
```

Die Lager, je Richtung gehalten wie beschrieben.

#### Uebersetzung.stablasten

```python
def stablasten(self, klasse: type) -> None
```

Die Lasten auf den Linien, in SI -- verteilt ueber die ganze Linie, einzeln an ihrer Stelle.

#### Uebersetzung.knotenlasten

```python
def knotenlasten(self, last_von: Callable[[Any, float], Any]) -> None
```

Die Lasten an den Knoten -- `last_von` macht aus einer und ihrem Wert in SI die des Rechenkerns.

#### Uebersetzung.modell

```python
def modell(self, system: type, knoten: type, staebe: List[Any], lager: List[Any]) -> Modell
```

Das Modell, mit den Kombinationen -- `system` und `knoten` die Klassen des Rechenkerns.

### modell_von

```python
def modell_von(eintrag: BalkensystemEintrag) -> Modell
```

Das Stabwerk zum Rechnen, in SI ([[opencivil.stabwerk.modell]]) -- siehe [[opencivil.projekt.aufbau.balkensystem#Uebersetzung|Uebersetzung]].

### _knotenlast

```python
def _knotenlast(p: Any, wert: float) -> Knotenlast
```

Ein Moment, eine Kraft waagrecht nach rechts oder senkrecht nach unten.

### bauen

```python
def bauen(art: 'Bauteilart', eintrag: BalkensystemEintrag, aufbau: Aufbau) -> Bauteil
```

Ein Balkensystem: das Stabwerk der Beschreibung, seine Materialien und
Querschnitte aufgeloest. Hart scheitert nur ein Verweis, den es nicht
gibt -- ein Beton, eine Platte, eine Querschnittsanalyse --; was dem
System selbst fehlt, steht in seinen Meldungen, und der Rest des
Projekts rechnet.

### stabwerk_bauen

```python
def stabwerk_bauen(klasse: type, art: 'Bauteilart', eintrag: Any, aufbau: Aufbau, modell: Modell, querschnitte: List[Stabquerschnitt]) -> Bauteil
```

Die Rechnung eines Stabwerks der Klasse `klasse` -- in der Ebene und im Raum.

### form_von

```python
def form_von(q: StabquerschnittBasis, wo: str, achse: Optional[Profilachse]=None) -> Stabquerschnitt
```

Ein Querschnitt nach Vorlage, als Stahlprofil oder von Hand -- in der
Ebene und im Raum. Ein Profil biegt sich in der Ebene um `achse`, im
Raum um beide.

### stabquerschnitt_von

```python
def stabquerschnitt_von(q: StabquerschnittBasis, aufbau: Aufbau, wo: str, achse: Optional[Profilachse]=None) -> Stabquerschnitt
```

Woher die Kennwerte eines Querschnitts kommen -- hier wird seine Art
aufgeloest, in der Ebene und im Raum. Die Platte oder Analyse dazu muss
es geben; ist noch keine gewaehlt oder fehlt ihr noch etwas
([[opencivil.projekt.aufbau.kern#Aufbau|Aufbau.unfertige]]), rechnet er nicht, und die Meldung sagt es. Ein Profil biegt sich in der Ebene um `achse`, im Raum um
beide ([[opencivil.projekt.aufbau.balkensystem#form_von|form_von]]).

### _rechnet_nicht

```python
def _rechnet_nicht(welche: str, unfertig: Unfertiges) -> str
```

Der Satz zu einer Platte oder Analyse, der noch etwas fehlt -- klein beginnend.

### _modulfrage

```python
def _modulfrage(q: StabquerschnittBasis, quelle, stoffe: Mapping[str, Baustoff]) -> Optional[Modulfrage]
```

Die Frage nach dem E_eq eines Querschnitts -- nur, wenn er es nehmen soll;
mit den Werten je Material der Platte oder Analyse, aus der er kommt.

### _paare

```python
def _paare(eintrag: Any, modell: Modell, aufbau: Aufbau, kennwerte: Sequence[Materialkennwert]) -> Tuple[Dict[str, Tuple[str, Stabmaterial]], List[Meldung]]
```

Je tragenden Stab sein Querschnitt und sein Material, aufgeloest --
«gemäss Querschnitt» wird zum Beton der Platte oder Analyse. Traegt das
Material nicht, sagt es eine Meldung, und das System rechnet nicht: eine
je Material, mit allen Staeben, die es nehmen -- bis 2026-11-19 eine je
Stab, und ein geloeschter Beton gab so viele gleiche Zeilen wie Staebe.
«gemäss Querschnitt» heisst je Querschnitt etwas anderes.

### _stabmaterial

```python
def _stabmaterial(m: StabmaterialEintrag, aufbau: Aufbau, kennwerte: Sequence[Materialkennwert]) -> Tuple[Optional[Stabmaterial], Optional[Grund]]
```

Ein Material des Systems, aufgeloest: ein Beton, Baustahl oder Holz des
Projekts oder ein eigenes mit den `kennwerte` von Hand. Traegt es
nicht, ist es `None`, und der zweite Teil sagt warum -- klein
beginnend, er folgt auf ein «aber». Ob es den Stoff gibt und ob er von
der Art ist, sagt dieselbe Regel wie bei jedem Bauteil
([[opencivil.projekt.aufbau.kern#materialgrund|materialgrund]]); bis 2026-11-19 hielt ein geloeschter das ganze
System an, und das Zeichenfenster bekam nur einen Fehler.

### _stabmaterialname

```python
def _stabmaterialname(m: StabmaterialEintrag, aufbau: Aufbau) -> str
```

Wie eine Meldung ein Material des Systems nennt: wie die Liste der
Materialien -- ein eigenes mit seinem Namen, eines des Projekts mit dem
Namen des Stoffs. Gibt es den Stoff nicht, nur seine Art; die Kennung
sieht der Benutzer nirgends (bis 2026-11-19 «das Material M1»).

### _material_des_querschnitts

```python
def _material_des_querschnitts(q: StabquerschnittBasis, aufbau: Aufbau) -> Tuple[Optional[Stabmaterial], Optional[Grund]]
```

Das Material, das ein Querschnitt mitbringt: der Beton einer Platte, das
eine Material der Flaechen einer Analyse. Sonst `None`, und der zweite
Teil sagt, warum.


## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.sprache]]
- [[opencivil.material.arten]]
- [[opencivil.material.basis]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.faelle]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.balkensystem]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.staebe]]
- [[opencivil.spannungsanalyse.modul]]
- [[opencivil.stabwerk.modell]]
- [[opencivil.stabwerk.rechnung]]
- [[opencivil.stabwerk.stabquerschnitt]]
- [[opencivil.stabwerk.system]]
- [[opencivil.stahlprofile.tabelle]]

## Gebraucht von

- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.balkensystem3d]]
