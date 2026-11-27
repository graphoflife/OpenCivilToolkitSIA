---
erzeugt: 291c02bd5da3
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/projekt.py
> das Projekt als Ganzes.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/projekt.py)

## VERANTWORTUNG

Das [[opencivil.projekt.projekt#Projekt|Projekt]] haelt Materialien und Bauteile zusammen und ist das, was
gespeichert, geoeffnet und gerechnet wird. Hier stehen der Zugriff auf die
Teile, die Methoden fuer das Rechnen ohne Oberflaeche, die Pruefungen ueber
mehrere Teile hinweg (eindeutige Kennungen und Materialnamen), die Sandbox
jeder App, Speichern und Laden. Das Beispiel, mit dem die Oberflaeche
startet, und das Pruefprojekt «Jeder Nachweis» baut
[[opencivil.projekt.beispiele]].

Gebaut wird in [[opencivil.projekt.aufbau]]; [[opencivil.projekt.projekt#Projekt.aufbauen|Projekt.aufbauen]]
reicht nur weiter.

## Inhalt

### naechster_name

```python
def naechster_name(stamm: str, namen: Iterable[str]) -> str
```

Der Name eines neuen Eintrags: «Platte 1», «Platte 2» … – der erste, den
es unter `namen` noch nicht gibt. So nennt auch die Oberflaeche, was
«+» anlegt (`naechsterName`, web/js/zustand.js); ein Test haelt beide
gleich.

### kopie_name

```python
def kopie_name(name: str, namen: Iterable[str]) -> str
```

Der Name einer Kopie: «Decke über EG (Kopie)», dann «… (Kopie 2)» – der
erste, den es unter `namen` noch nicht gibt. Wie ⧉ in der Oberflaeche
(`kopieName`, web/js/zustand.js); ein Test haelt beide gleich.

### Projekt

```python
@dataclass
class Projekt(Beschreibung)
```

Die vollstaendige, speicherbare Beschreibung eines Projekts.

- `STAMM = 'Projekt'`
- `name: str = 'Neues Projekt'`
- `materialien: List[MaterialEintrag] = field(default_factory=list)`
- `querschnitte: List[QuerschnittEintrag] = field(default_factory=list)`
- `querschnittsanalysen: List[QuerschnittsanalyseEintrag] = field(default_factory=list)` – Gezeichnete Querschnitte: Polygone, Bewehrung, Schubwände.
- `balkensysteme: List[BalkensystemEintrag] = field(default_factory=list)` – Ebene Rahmen: Knoten, Stäbe, Lager, Lasten, Lastfälle.
- `balkensysteme3d: List[Balkensystem3dEintrag] = field(default_factory=list)` – Rahmen im Raum: wie die ebenen, mit x, y und z und Torsion.
- `decken: List[DeckeEintrag] = field(default_factory=list)` – Stahlbetondecken nach der Streifenmethode: Platten, Lager, Stützen, Unterzüge.
- `durchstanzstellen: List[DurchstanzEintrag] = field(default_factory=list)` – Stützen und Wände, an denen das Durchstanzen nachgewiesen wird.
- `grundbrueche: List[GrundbruchEintrag] = field(default_factory=list)` – Flachfundamente mit Grundbruch und Gleiten.
- `setzungen: List[SetzungEintrag] = field(default_factory=list)` – Flachfundamente auf geschichtetem Baugrund, mit ihrer Setzung.
- `pfaehle: List[PfahlEintrag] = field(default_factory=list)` – Einzelpfähle: Bohr- und Mikropfähle mit äusserem und innerem Widerstand.
- `erdbeben: List[ErdbebenEintrag] = field(default_factory=list)` – Gebäude im Erdbeben, nach dem Ersatzkraftverfahren – Geschosse und Tragwände.
- `skripte: List[SkriptEintrag] = field(default_factory=list)` – Die Python-Skripte der App «Python» – gespeichert, nicht gerechnet.
- `sandboxen: Dict[str, str] = field(default_factory=dict)` – Je Liste einer App ([[opencivil.projekt.projekt#Konstanten|APPLISTEN]]) die Kennung ihrer Sandbox, des Eintrags zum Ausprobieren – siehe [[opencivil.projekt.projekt#Projekt.sandbox_zuruecksetzen|sandbox_zuruecksetzen]]. Hier und nicht an den Eintraegen: so steht die Regel an einer Stelle, und eine Kopie der Sandbox ist von selbst ein gewoehnlicher Eintrag.
- `vergeben: Dict[str, int] = field(default_factory=dict)` – Je Vorsilbe die hoechste Nummer, die das Projekt je vergeben hat – an Materialien, Bauteile, Skripte: eine Kennung kommt nie wieder ([[opencivil.projekt.netz#neue_kennung|neue_kennung]]).

#### Projekt.material

```python
def material(self, kennung: str) -> MaterialEintrag
```

#### Projekt.querschnitt

```python
def querschnitt(self, kennung: str) -> QuerschnittEintrag
```

#### Projekt.querschnittsanalyse

```python
def querschnittsanalyse(self, kennung: str) -> QuerschnittsanalyseEintrag
```

#### Projekt.bauteile

```python
def bauteile(self) -> List[Any]
```

Alle Bauteile in der Reihenfolge der Beschreibung – siehe [[opencivil.projekt.aufbau#Konstanten|BAUTEILE]].

#### Projekt.nur

```python
def nur(self, kennung: str) -> 'Projekt'
```

Eine Kopie, in der von den Bauteilen nur dieses eine steht – mit
denen, deren Querschnitt es nimmt (`bezuege`), auch ueber mehrere
Stufen; die Materialien bleiben. So rechnet die Bewehrungssuche: die
anderen Bauteile kann sie nicht beeinflussen, und ihre Urteile
zaehlten sonst mit. Und so holt der MCP-Zugang die Herleitung eines
Bauteils – ein Stab, dessen Querschnitt eine Analyse ist, rechnete
ohne sie nicht.

#### Projekt.bauteil

```python
def bauteil(self, kennung: str) -> Any
```

Ein Bauteil gleich welcher Art – eine Platte, eine Analyse, ein System.

#### Projekt.freie_kennung

```python
def freie_kennung(self, vorsilbe: str) -> str
```

Eine Kennung, die es im Projekt nie gab – siehe [[opencivil.projekt.netz#neue_kennung|neue_kennung]].

#### Projekt.verweise

```python
def verweise(self, kennung: str) -> List[Any]
```

Die Bauteile, die auf diese Kennung zeigen – als Material oder als
Querschnitt ([[opencivil.projekt.projekt#Projekt|materialien]] und [[opencivil.projekt.projekt#Projekt|bezuege]] jedes Eintrags).
Was hier steht, darf nicht geloescht werden; die Oberflaeche fragt hier,
bevor sie loescht (Dienst `verweise`), statt es in einer eigenen
Liste nachzubauen.

Eine Sandbox haelt nichts fest: zeigt sie auf etwas Geloeschtes, sagt
sie es selbst, und zurueckgesetzt nimmt sie wieder das erste Material.
Sonst liesse sich der einzige Beton nicht loeschen, weil die Sandbox
der Platten ihn nimmt.

#### Projekt.eigener_name

```python
def eigener_name(self, art: str) -> str
```

Der erste freie Name eines eigenen Materials: BE1, BE2 ..., S1 ..., ST1 ...,
SP1 ..., H1 ..., PB1 ... oder FL1 ...

#### Projekt.beton

```python
def beton(self, sorte: str='C30/37') -> MaterialEintrag
```

Eine Betonsorte nach Norm – Kennung `b1`, `b2` ...

#### Projekt.stahl

```python
def stahl(self, sorte: str='B500B') -> MaterialEintrag
```

Eine Betonstahlsorte nach Norm – Kennung `s1`, `s2` ...

#### Projekt.baustahl

```python
def baustahl(self, sorte: str='S235') -> MaterialEintrag
```

Eine Baustahlsorte nach SIA 263 – Kennung `st1`, `st2` ...

#### Projekt.spannstahl

```python
def spannstahl(self, sorte: str='Y1860') -> MaterialEintrag
```

Eine Spannstahlsorte nach SIA 262 – Kennung `sp1`, `sp2` ...

#### Projekt.holz

```python
def holz(self, sorte: str='C24') -> MaterialEintrag
```

Eine Holzsorte nach SIA 265 – Kennung `h1`, `h2` ...

#### Projekt.profilblech

```python
def profilblech(self, sorte: str='SE 350 G') -> MaterialEintrag
```

Ein Profilblechstahl nach SIA 264 – Kennung `pb1`, `pb2` ...

#### Projekt.fluessigkeit

```python
def fluessigkeit(self, sorte: str=ERSTE_FLUESSIGKEIT) -> MaterialEintrag
```

Eine Fluessigkeit, das Wasser – Kennung `fl1`, `fl2` ...

#### Projekt.eigener_beton

```python
def eigener_beton(self, vorlage: str='C30/37') -> MaterialEintrag
```

Ein eigener Beton, `BE1`, `BE2` ... – mit den Kennwerten der Sorte
`vorlage`, abzuaendern ueber `abweichungen` und
`ueberschreibungen`. Eine Normsorte selbst bleibt, wie sie ist.

#### Projekt.eigener_stahl

```python
def eigener_stahl(self, vorlage: str='B500B') -> MaterialEintrag
```

Ein eigener Betonstahl, `S1`, `S2` ... – siehe [[opencivil.projekt.projekt#Projekt.eigener_beton|eigener_beton]].

#### Projekt.eigener_baustahl

```python
def eigener_baustahl(self, vorlage: str='S235') -> MaterialEintrag
```

Ein eigener Baustahl, `ST1`, `ST2` ... – siehe [[opencivil.projekt.projekt#Projekt.eigener_beton|eigener_beton]].

#### Projekt.eigener_spannstahl

```python
def eigener_spannstahl(self, vorlage: str='Y1860') -> MaterialEintrag
```

Ein eigener Spannstahl, `SP1`, `SP2` ... – siehe [[opencivil.projekt.projekt#Projekt.eigener_beton|eigener_beton]].

#### Projekt.eigenes_holz

```python
def eigenes_holz(self, vorlage: str='C24') -> MaterialEintrag
```

Ein eigenes Holz, `H1`, `H2` ... – siehe [[opencivil.projekt.projekt#Projekt.eigener_beton|eigener_beton]].

#### Projekt.eigene_fluessigkeit

```python
def eigene_fluessigkeit(self, vorlage: str=ERSTE_FLUESSIGKEIT) -> MaterialEintrag
```

Eine eigene Fluessigkeit, `FL1`, `FL2` ... – eine Bentonitsuspension
etwa, ihre Dichte in `abweichungen["rho_fl"]`; siehe [[opencivil.projekt.projekt#Projekt.eigener_beton|eigener_beton]].

#### Projekt.material_anlegen

```python
def material_anlegen(self, art: str, sorte: str, *, eigen: bool=False) -> MaterialEintrag
```

«+ Material»: eine Normsorte der Art `art` – mit `eigen` ein
eigenes Material, die Sorte als Vorlage ([[opencivil.projekt.projekt#Projekt.eigener_beton|eigener_beton]]). Fuer
wer die Art als Text hat, den MCP-Zugang; [[opencivil.projekt.projekt#Projekt.beton|beton]] und die
anderen sagen sie im Namen.

#### Projekt._normsorte

```python
def _normsorte(self, art: str, sorte: str) -> MaterialEintrag
```

Legt eine Normsorte an und prueft sie sofort.

Sofort und nicht erst beim Rechnen: ein Tippfehler in der Sorte soll
an der Zeile auffallen, in der er steht.

#### Projekt.platte

```python
def platte(self, name: str, *, h: float=300.0, x: Sequence[float]=(12.0, 12.0), y: Sequence[float]=(12.0, 12.0), x_zulage: Sequence[float]=(0.0, 0.0), y_zulage: Sequence[float]=(0.0, 0.0), teilung: float=150.0, x_innen: bool=True, beton: Union[str, MaterialEintrag, None]=None, stahl: Union[str, MaterialEintrag, None]=None, **felder: Any) -> QuerschnittEintrag
```

Eine Platte – Masse in mm, Bewehrung als Durchmesser je Richtung.

`x` und `y` sind je zwei Durchmesser, *unten* und *oben*;
`x_zulage` und `y_zulage` ebenso, null heisst keine. Alle Posten
liegen in derselben `teilung`. `x_innen` legt die Tragrichtung
auf die 2. und 3. Lage, wie die Vorgabe der Oberflaeche.

`beton` und `stahl` duerfen fehlen, solange das Projekt nur je
einen hat. Alles Weitere – `b`, `rissanforderung`,
`duktilitaet` ... – geht als Stichwort an den Eintrag; ein
unbekanntes Stichwort wird gemeldet, statt still zu verschwinden.
Gelesen wird es wie aus einer Datei: ein Teil darf als Eintrag kommen
oder als seine Felder, `tragsicherheit_wahl={"kriechzahl": 1.0}`
aendert nur die Kriechzahl.

Gebaut wird ueber [[opencivil.projekt.platte#QuerschnittEintrag.neu|QuerschnittEintrag.neu]], dieselbe Vorlage wie
in der Oberflaeche, nur ohne deren Startlast: wer rechnet, gibt seine
Einwirkungen selbst an.

#### Projekt.analyse

```python
def analyse(self, name: str, *, beton: Union[str, MaterialEintrag, None]=None, stahl: Union[str, MaterialEintrag, None]=None, **felder: Any) -> QuerschnittsanalyseEintrag
```

Eine Querschnittsanalyse – ein Rechteck 300 × 600 mm mit drei
Staeben unten und zwei oben, ohne Lastfall: wer rechnet, gibt seine
Lastfaelle selbst an. In der Oberflaeche beginnt eine neue Analyse
seit 2026-10-19 leer; hier bleibt das Rechteck, auf dem Skripte und
Tests aufbauen.

Gezeichnet wird danach mit dem Baukasten des Eintrags –
`polygon`, `stab`, `stablinie`, `schubwand`, `hilfslinie`,
Masse in mm. Wie bei [[opencivil.projekt.projekt#Projekt.platte|platte]] geht alles Weitere als Stichwort
an den Eintrag.

#### Projekt.balkensystem

```python
def balkensystem(self, name: str, **felder: Any) -> BalkensystemEintrag
```

Ein leeres Balkensystem, ein ebener Rahmen. Gezeichnet wird danach
mit dem Baukasten des Eintrags – `querschnitt`, `linie`,
`lager_an`, `lastfall`, `stablast`, `knotenlast`,
`kombination` –, Koordinaten in m. Leer, ohne die Lastfaelle und
Kombinationen, die die Oberflaeche mitbringt: wer in Python zeichnet,
zeichnet sein eigenes System.

#### Projekt.balkensystem3d

```python
def balkensystem3d(self, name: str, **felder: Any) -> Balkensystem3dEintrag
```

Ein leeres 3D-Balkensystem, ein Rahmen im Raum – gezeichnet wie das
ebene ([[opencivil.projekt.projekt#Projekt.balkensystem|balkensystem]]), mit Punkten `(x, y, z)` in m.

#### Projekt.decke

```python
def decke(self, name: str, **felder: Any) -> DeckeEintrag
```

Eine leere Decke. Gezeichnet wird danach mit dem Baukasten des
Eintrags – `platte`, `lager` (ein Linienlager), `stuetze`,
`unterzug`, `zone` –, Koordinaten in m.

#### Projekt.durchstanzen

```python
def durchstanzen(self, name: str, beton: str, stahl: str, **felder: Any) -> DurchstanzEintrag
```

Ein Durchstanznachweis mit den Vorgaben der Oberflaeche. `beton` und
`stahl` sind Kennungen von Materialien; alles Weitere – `h`,
`lage`, `V_d` ... – geht als Stichwort an den Eintrag: Masse der
Platte und der Stütze in mm, Spannweiten in m, Kräfte in kN.
Aussparungen mit [[opencivil.projekt.durchstanzen#DurchstanzEintrag.aussparung|aussparung]].

#### Projekt.grundbruch

```python
def grundbruch(self, name: str, **felder: Any) -> GrundbruchEintrag
```

Ein Grundbruchnachweis mit den Vorgaben der Oberflaeche, aber ohne
ihre Startkombination: wer rechnet, gibt seine Einwirkungen mit
`kombination` selbst an. Das Wasser ist wie dort die erste
Fluessigkeit des Projekts. Alles Weitere – `phi_k`, `b`, `t` ...
– geht als Stichwort an den Eintrag; Winkel in Grad, Masse in m,
Spannungen in kPa.

#### Projekt.setzung

```python
def setzung(self, name: str, **felder: Any) -> SetzungEintrag
```

Eine Setzungsberechnung mit den Vorgaben der Oberflaeche, aber ohne
ihre Startschicht: wer rechnet, gibt seine Schichten mit `schicht`
selbst an, von der Sohle an nach unten. Alles Weitere – `B`,
`q_E`, `steifigkeit` ... – geht als Stichwort an den Eintrag;
Masse in m, Pressungen in kN/m², die zulaessige Setzung in mm.

#### Projekt.pfahl

```python
def pfahl(self, name: str, stahl: str, beton: str='', **felder: Any) -> PfahlEintrag
```

Ein Pfahl mit den Vorgaben der Oberflaeche, aber ohne ihre Startschicht
und Startkombination: wer rechnet, gibt sie mit `schicht` und
`kombination` selbst an. `stahl` und `beton` sind Kennungen von
Materialien, der Beton nur beim Bohrpfahl; das Wasser ist wie in der
Oberflaeche die erste Fluessigkeit des Projekts. Alles Weitere –
`art`, `D`, `grundlage` ... – geht als Stichwort an den Eintrag;
Masse des Querschnitts in mm, Tiefen in m, Spannungen in kPa.

#### Projekt.gebaeude

```python
def gebaeude(self, name: str, **felder: Any) -> ErdbebenEintrag
```

Ein Gebaeude fuer das Erdbeben, mit den Vorgaben der Oberflaeche, aber
ohne ihr Startgeschoss und ihre Startwand: wer rechnet, gibt sie mit
`geschoss` und `wand` selbst an, die Geschosse von unten. Alles
Weitere – `zone`, `baugrund`, `q_x` ... – geht als Stichwort an
den Eintrag; Hoehen in m, Lasten in kN, Schwingzeiten in s.

#### Projekt.skript

```python
def skript(self, name: str, code: str='') -> SkriptEintrag
```

Ein Python-Skript für die App «Python» – Kennung `p1`, `p2` ...
Ausgeführt wird es in der Konsole der Oberfläche, nicht hier.

#### Projekt._einziges

```python
def _einziges(self, art: str, gewaehlt: Union[str, MaterialEintrag, None]) -> str
```

Die Kennung des gewaehlten Materials – oder des einzigen dieser Art.

#### Projekt.rechnen

```python
def rechnen(self) -> Ergebnis
```

Alles rechnen, was die Oberflaeche auch rechnet – ohne sie.

Dieselben Ziele in derselben Reihenfolge ([[opencivil.projekt.aufbau.kern#Aufbau.alle_ziele|Aufbau.alle_ziele]]),
also derselbe Bericht – ohne die Sandboxen, wie dort
([[opencivil.projekt.projekt#Projekt.ohne_sandboxen|ohne_sandboxen]]). Ohne Zwischenspeicher: der lohnt sich erst,
wenn man dieselbe Platte hundertmal rechnet.

#### Projekt.eintrag_anlegen

```python
def eintrag_anlegen(self, liste: str) -> Any
```

«+» einer App: ein frischer Eintrag nach der Vorlage seiner Klasse und
mit dem ersten Material jeder Art, die er nimmt
([[opencivil.projekt.eintraege#Beschreibung.frisch|frisch]]), unter einer
Kennung, die es im Projekt nie gab, am Ende der Liste – und mit dem
Namen, den «+» gibt: «Platte 1» ([[opencivil.projekt.projekt#naechster_name|naechster_name]]). Fehlt ein
Material, das er nimmt, rechnet er erst, wenn eines da ist, wie die
Sandbox.

#### Projekt.eintrag_kopieren

```python
def eintrag_kopieren(self, kennung: str) -> Any
```

⧉: eine Kopie gleich hinter dem Original, alles wie dort, nur Kennung
und Name neu – «Decke über EG (Kopie)» ([[opencivil.projekt.projekt#kopie_name|kopie_name]]). Die
Kopie der Sandbox ist ein gewoehnlicher Eintrag und heisst wie ein
neuer, «Platte 1».

#### Projekt.eintrag_loeschen

```python
def eintrag_loeschen(self, kennung: str) -> Any
```

×: ein Eintrag einer App oder ein Material geht – nicht die Sandbox,
die nur zurueckgesetzt wird, und nicht, solange ein Bauteil auf ihn
zeigt ([[opencivil.projekt.projekt#Projekt.verweise|verweise]]); der Fehler nennt dann die Bauteile. Gibt den
geloeschten Eintrag zurueck.

#### Projekt._app

```python
def _app(self, liste: str) -> Tuple[type, str]
```

Klasse und Vorsilbe der App mit dieser Liste ([[opencivil.projekt.projekt#Konstanten|APPLISTEN]]).

#### Projekt._ort_in_app

```python
def _ort_in_app(self, kennung: str) -> Tuple[str, int]
```

In welcher Liste einer App der Eintrag steht, und an welcher Stelle.

#### Projekt.ist_sandbox

```python
def ist_sandbox(self, kennung: str) -> bool
```

Ob dieser Eintrag die Sandbox seiner App ist.

#### Projekt.sandbox_zuruecksetzen

```python
def sandbox_zuruecksetzen(self, liste: str) -> Any
```

Die Sandbox einer App, frisch: nach der Vorlage ihrer Klasse und mit
dem ersten Material jeder Art, das sie nimmt, wie ein neuer Eintrag
der Oberflaeche ([[opencivil.projekt.eintraege#Beschreibung.frisch|frisch]]).
Eine vorhandene wird an ihrem Platz ersetzt und behaelt ihre Kennung
– wer auf sie zeigt, zeigt weiter auf sie. Eine fehlende kommt
zuoberst in die Liste.

#### Projekt.sandboxen_anlegen

```python
def sandboxen_anlegen(self, *, frisch: bool=False) -> None
```

Jede Sandbox, die fehlt – in einem neuen Projekt, in einer Datei, die
noch keine kennt. Mit `frisch` beginnt auch jede vorhandene neu: so
startet die Seite (Benutzer, 2026-11-20).

#### Projekt.ohne_sandboxen

```python
def ohne_sandboxen(self) -> 'Projekt'
```

Eine Kopie ohne die Sandboxen – das Projekt, wie es im Bericht steht.

#### Projekt.pruefen

```python
def pruefen(self) -> None
```

Prueft die Form der Beschreibung – vor jedem Rechnen und beim Oeffnen
einer Datei: jedes Feld gegen das, was an ihm steht
([[opencivil.projekt.lesen#felder_pruefen|felder_pruefen]]), eine Kennung je
Eintrag und die Sorte jedes Materials. Was in Python gebaut wurde,
geht so durch dieselbe Tuer wie eine Datei.

Den Inhalt – Bereiche, die Regeln der Bauteile und Materialien, ihre
Namen – prueft erst das Rechnen
([[opencivil.projekt.lesen#inhalt_pruefen|inhalt_pruefen]]): ein abgelegtes
Projekt mit zwei gleich benannten Materialien soll sich oeffnen und
korrigieren lassen.

#### Projekt.regeln

```python
def regeln(self, wo: str) -> None
```

Die Namen der Materialien, vor dem Rechnen – je Material einer.

#### Projekt.inhalt_pruefen

```python
def inhalt_pruefen(self) -> None
```

Prueft den Inhalt, vor jedem Rechnen und vor jeder Suche: Bereiche
und Regeln jedes Eintrags ([[opencivil.projekt.lesen#inhalt_pruefen|inhalt_pruefen]]).
Die Form prueft [[opencivil.projekt.projekt#Projekt.pruefen|pruefen]].

#### Projekt.aufbauen

```python
def aufbauen(self, *, schnell: bool=False) -> Aufbau
```

Baut aus der Beschreibung ein vollstaendiges Rechenwerk.

Die Arbeit steht in [[opencivil.projekt.aufbau#aufbauen|opencivil.projekt.aufbau.aufbauen]], neben
dem [[opencivil.projekt.aufbau.kern#Aufbau|Aufbau]], der dabei herauskommt.

#### Projekt.speichern

```python
def speichern(self, pfad: str | Path) -> Path
```

#### Projekt.laden

```python
@classmethod
def laden(cls, pfad: str | Path) -> 'Projekt'
```

#### Projekt.aus_dict

```python
@classmethod
def aus_dict(cls, roh: Mapping[str, Any], wo: Optional[str]=None) -> 'Projekt'
```

Ein Projekt aus der Datei, gelesen und geprueft. Was eine Datei von
frueher anders schreibt, bringt [[opencivil.projekt.frueher|frueher]] in
die neue Form: die Zahl γ_w von Grundbruch und Pfahl wird ein Wasser,
die Spannungen eines Spannglieds werden Faktoren, und ein Pfahl
bekommt den Schalter fuer η_a.

#### Projekt.neu

```python
@classmethod
def neu(cls, name: str='Neues Projekt') -> 'Projekt'
```

Ein neues Projekt, wie es «+» in der Oberflaeche anlegt: je
Materialart eine Sorte ([[opencivil.projekt.projekt#Konstanten|NEUES_PROJEKT]]) und ohne Bauteile. So
rechnet das erste Bauteil jeder App gleich. Die Sandboxen legt die
Oberflaeche dazu an ([[opencivil.projekt.projekt#Projekt.sandboxen_anlegen|sandboxen_anlegen]]); wer in Python
rechnet, braucht sie nicht.

#### Projekt.beispiel

```python
@classmethod
def beispiel(cls) -> 'Projekt'
```

Das Beispiel, mit dem die Oberflaeche startet – gebaut in [[opencivil.projekt.beispiele|.beispiele]].

#### Projekt.jeder_nachweis

```python
@classmethod
def jeder_nachweis(cls) -> 'Projekt'
```

Jeder Nachweis einmal laut – gebaut in [[opencivil.projekt.beispiele|.beispiele]].


## Konstanten

- `APPLISTEN = {**{art.liste: (art.eintrag, art.vorsilbe) for art in BAUTEILE}, 'skr…` – Die Listen der Apps ausser den Materialien, je mit der Klasse ihrer Eintraege und der Vorsilbe ihrer Kennungen: die Bauteilarten ([[opencivil.projekt.aufbau#Konstanten|BAUTEILE]]) und die Skripte der App «Python». Was «+» in ihnen anlegt, steht im Katalog (`neu`); jede hat eine Sandbox.
- `SANDBOX = 'Sandbox'` – Wie die Sandbox jeder App heisst (Benutzer, 2026-11-20).
- `NEUES_PROJEKT = {'beton': ERSTER_BETON, 'betonstahl': ERSTER_STAHL, 'baustahl': ERSTE…` – Womit ein neues Projekt anfaengt: je Materialart eine Sorte, damit jede App gleich rechnet (Plan vom 2026-11-27; bis dahin nur Beton und Betonstahl). Das Holz ist GL24h, wie im Plan – nicht C24, das erste Holz des Fensters «Neues Material».

## Braucht

- [[opencivil.ergebnis]]
- [[opencivil.material.arten]]
- [[opencivil.material.baustahl]]
- [[opencivil.material.beton]]
- [[opencivil.material.betonstahl]]
- [[opencivil.material.fluessigkeit]]
- [[opencivil.material.profilblech]]
- [[opencivil.material.spannstahl]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.balkensystem]]
- [[opencivil.projekt.balkensystem3d]]
- [[opencivil.projekt.beispiele]]
- [[opencivil.projekt.decke]]
- [[opencivil.projekt.durchstanzen]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.erdbeben]]
- [[opencivil.projekt.frueher]]
- [[opencivil.projekt.grundbruch]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.netz]]
- [[opencivil.projekt.pfahl]]
- [[opencivil.projekt.platte]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.projekt.setzung]]
- [[opencivil.projekt.skript]]
- [[opencivil.querschnitt.platte]]
- [[opencivil.querschnitt.vorlagen]]

## Gebraucht von

- [[opencivil.mcp.sitzung]]
- [[opencivil.mcp.werkzeuge]]
- [[opencivil.projekt]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.beispiele]]
- [[opencivil.projekt.frueher]]
- [[opencivil.projekt.mappe]]
- [[opencivil.web.api]]
