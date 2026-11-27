---
erzeugt: 34c0b21e7883
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/aufbau/kern.py
> was alle Bauteilarten beim Bauen teilen.
> Paket [[opencivil.projekt.aufbau]] · [Quelltext](../../opencivil/projekt/aufbau/kern.py)

## VERANTWORTUNG

Der [[opencivil.projekt.aufbau.kern#Aufbau|Aufbau]], in dem das Gebaute nach Feld und Kennung liegt, das
[[opencivil.projekt.aufbau.kern#Bauteil|Bauteil]] mit seinen Nachweisen und Zielen, und was mehr als eine
Bauteilart braucht: die Baustoffe aus den Materialien
([[opencivil.projekt.aufbau.kern#baustoff_bauen|baustoff_bauen]], [[opencivil.projekt.aufbau.kern#material|material]], [[opencivil.projekt.aufbau.kern#ueberschreibungen_setzen|ueberschreibungen_setzen]]),
die beiden Stahlspannungen ([[opencivil.projekt.aufbau.kern#spannungsnachweise|spannungsnachweise]]) und den Knickfall
([[opencivil.projekt.aufbau.kern#knickfall|knickfall]]) – Platte und gezeichneter Querschnitt rufen dieselben.

Was nur eine Art braucht, steht bei ihr: [[opencivil.projekt.aufbau.platte|platte]],
[[opencivil.projekt.aufbau.querschnittsanalyse|querschnittsanalyse]],
[[opencivil.projekt.aufbau.balkensystem|balkensystem]],
[[opencivil.projekt.aufbau.durchstanzen|durchstanzen]],
[[opencivil.projekt.aufbau.grundbruch|grundbruch]],
[[opencivil.projekt.aufbau.setzung|setzung]] und
[[opencivil.projekt.aufbau.pfahl|pfahl]]. Bis 2026-10-17 stand alles in
einer Datei `aufbau.py` von ueber tausend Zeilen.

## Inhalt

### Warnung

```python
class Warnung(NamedTuple)
```

Ein Hinweis aus dem Aufbau: `raum` ist der Namensraum des Eintrags, dem
er gilt – «querschnitt.q1» –, `text` der Satz. Am Namensraum grenzt
die Oberflaeche ihn ein wie alles andere: unter «Aktuelle Seite» stehen
die Hinweise des gewaehlten Eintrags, unter «Gesamt» alle ausser denen
der Sandboxen. Bis 2026-11-20 standen alle ueber jeder Herleitung – mit
der Sandbox auch ihr «noch nichts gezeichnet», in jedem Projekt.

- `raum: str`
- `text: str`

### Aufbau

```python
@dataclass
class Aufbau
```

Was beim Zusammenbauen eines Projekts entsteht.

- `werk: Rechenwerk`
- `schnell: bool = False` – Fuer die Bewehrungssuche gebaut – siehe [[opencivil.projekt.aufbau#aufbauen|aufbauen]].
- `teile: Dict[str, 'Bauteil'] = field(default_factory=dict)` – Jedes Bauteil nach Kennung, in der Reihenfolge von [[opencivil.projekt.aufbau#Konstanten|BAUTEILE]] und der Beschreibung.
- `baustoffe: Dict[str, Baustoff] = field(default_factory=dict)`
- `kennzahlen: Dict[str, Plattenkennzahlen] = field(default_factory=dict)` – Die Kennzahlen je Platte mit x-Bewehrung – immer gerechnet.
- `spannungsfaelle: Dict[str, List[Tuple['SpannungsfallEintrag', Rechenwahl]]] = field(default_factory=dict)` – Je Platte die Auswertungen am Querschnitt – als Beschreibung, nicht als Nachweis, jede mit ihrer Wahl am Bauteil. Sie laufen nicht im Rechenwerk: sie haben kein Ziel, das jemand anderes brauchen koennte, und nichts haengt von ihnen ab.
- `unfertige: Dict[str, 'Unfertiges'] = field(default_factory=dict)` – Je Bauteil oder Material, dem noch etwas fehlt, was: eine Querschnittsanalyse ohne Zeichnung, eine Platte ohne Bewehrung, ein Pfahl ohne Schicht, ein Wert, den der Kern abweist ([[opencivil.projekt.aufbau.kern#Aufbau.unfertig|unfertig]]). Es wird nicht gebaut, aber wer auf es zeigt, soll hoeren, was ihm fehlt, und nicht, es gebe es nicht.
- `warnungen: List[Warnung] = field(default_factory=list)` – Was beim Aufbau auffiel, je Eintrag ([[opencivil.projekt.aufbau.kern#Aufbau.warnen|warnen]]).
- `NACHWEISFELDER = ('nachweise', 'querkraft', 'duktilitaet', 'fehlende', 'rissnormalkraf…` – Die Felder, in denen die Nachweise stehen – die eine Stelle, an der ein neuer Nachweis eingetragen wird. Alle sind nach Kennung geschluesselt (`q1` oder `q1.x` – die Richtung steht noch im Schluessel der Platte, damit Wert-IDs in abgelegten Berichten nicht wechseln) und alle tragen Nachweise mit `d_ausnutzung`. Ihre Reihenfolge ist die der Herleitung: in ihr rechnet ein Bauteil seine Nachweise ([[opencivil.projekt.aufbau.kern#Bauteil.ziele|Bauteil.ziele]]). `fehlende` rechnet nichts: eine Richtung ohne Bewehrung mit Einwirkungen bekommt so eine Zeile mit Erfuellungsgrad null statt gar keiner.

#### Aufbau.warnen

```python
def warnen(self, raum: str, text: str) -> None
```

Ein Hinweis zum Eintrag mit dem Namensraum `raum` ([[opencivil.projekt.aufbau.kern#Warnung|Warnung]]).

#### Aufbau.unfertig

```python
def unfertig(self, liste: str, eintrag: Any, wo: str, grund: str, *, raum: str) -> None
```

Ein Bauteil oder Material, dem noch etwas fehlt: es rechnet nicht,
das Projekt schon, und ein Hinweis sagt, was fehlt – ein unfertiger
Zustand ist kein Fehler des Projekts (Benutzer, 2026-11-19). Bis
dahin hielten eine Platte ohne Bewehrung, ein Pfahl ohne Schicht und
eine halbfertige Zeichnung alles auf. `liste` ist seine Liste im
Projekt; `grund` ein Satzteil («noch keine Bewehrung») oder ein
Satz, ohne Punkt; `raum` sein Namensraum, «beton.b1». Eine
Baufunktion meldet es, indem sie einen [[opencivil.projekt.lesen#ProjektFehler|ProjektFehler]] wirft
([[opencivil.projekt.aufbau#aufbauen|aufbauen]]).

#### Aufbau.ohne_nachweis

```python
def ohne_nachweis(self, teil: 'Bauteil', wo: str, grund: str) -> None
```

Ein Bauteil, das gebaut ist, dem aber fuer jeden Nachweis noch etwas
fehlt – eine Kombination, eine Schicht. Wie [[opencivil.projekt.aufbau.kern#Aufbau.unfertig|unfertig]] kein
Fehler: `grund` steht in der Zusammenfassung an seiner Stelle (bis
2026-11-19 dort nur «Kein Nachweis gerechnet.») und als Warnung in der
Herleitung. Ein Satzteil ohne Punkt.

#### Aufbau.objekte

```python
def objekte(self, art: str) -> Dict[str, Any]
```

Die gebauten Objekte einer Bauteilart nach Kennung – `art` ist ihr
Name. Einen Namen, den keine Art traegt, meldet sie, statt still ein
leeres Verzeichnis zu geben.

#### Aufbau.querschnitte

```python
@property
def querschnitte(self) -> Dict[str, Plattenquerschnitt]
```

Die Plattenquerschnitte, nach Kennung.

#### Aufbau.querschnittsanalysen

```python
@property
def querschnittsanalysen(self) -> Dict[str, Any]
```

Die gezeichneten Querschnitte, nach Kennung.

#### Aufbau.balkensysteme

```python
@property
def balkensysteme(self) -> Dict[str, Balkensystem]
```

Die Balkensysteme, nach Kennung – Bauteile ohne Nachweise, mit ihrem Ergebnis.

#### Aufbau.balkensysteme3d

```python
@property
def balkensysteme3d(self) -> Dict[str, Balkensystem3d]
```

Die 3D-Balkensysteme, nach Kennung – wie die ebenen.

#### Aufbau.decken

```python
@property
def decken(self) -> Dict[str, Deckensystem]
```

Die Decken, nach Kennung – Bauteile ohne Nachweise, mit ihrem Ergebnis.

#### Aufbau.grundbrueche

```python
@property
def grundbrueche(self) -> Dict[str, Fundament]
```

Die Fundamente der Grundbruchnachweise, nach Kennung.

#### Aufbau.setzungen

```python
@property
def setzungen(self) -> Dict[str, Setzungsfundament]
```

Die Fundamente der Setzungsberechnungen, nach Kennung.

#### Aufbau.pfaehle

```python
@property
def pfaehle(self) -> Dict[str, Pfahl]
```

Die Pfähle, nach Kennung.

#### Aufbau.feld

```python
def feld(self, feld: str) -> Dict[str, Nachweis]
```

Die Nachweise eines Feldes, nach ihrem Schluessel – eine Sicht auf
die Bauteile, in ihrer Folge. Bis 2026-10-25 stand jedes Feld als
eigenes Woerterbuch im Aufbau, neben den Nachweisen der Bauteile.

#### Aufbau.nachweise_je_feld

```python
def nachweise_je_feld(self)
```

Alle Nachweise, Feld fuer Feld und in der Reihenfolge der Liste.

#### Aufbau.alle_nachweise

```python
def alle_nachweise(self)
```

Jeden Nachweis einmal, in derselben Reihenfolge wie im Protokoll.

#### Aufbau.alle_nachweisziele

```python
def alle_nachweisziele(self) -> List[str]
```

Jeden Nachweis als Ziel – auch einen ohne Lastfall, der nur fuer sein Bild rechnet.

#### Aufbau.eintragen

```python
def eintragen(self, teil: 'Bauteil', feld: str, schluessel: str, nachweis: Nachweis) -> None
```

Einen Nachweis anmelden: im Rechenwerk und bei seinem Bauteil, mit
Feld und Schluessel – ausser er ist ganz still, und es wird schnell
gerechnet.

Den schnellen Weg nimmt nur die Bewehrungssuche, und die zaehlt
stille Urteile nicht ([[opencivil.projekt.aufbau.kern#Aufbau|bewehrungssuche.bewerte]]). Ein ganz
stiller Nachweis kann ihr Ergebnis also nicht aendern, er kostet
nur Zeit – und bei der Stahlspannung, die immer mitlaeuft, ist
das der groessere Teil der ganzen Rechnung. Exakt und nicht
genaehert: gezaehlt wird dasselbe wie vorher.

Jeder Nachweis geht hier durch, auch die, die nie still sind – ein
Weg zum Anmelden, nicht zwei.

#### Aufbau.kennzahlen_eintragen

```python
def kennzahlen_eintragen(self, teil: 'Bauteil', prozedur: Kennzahlprozedur) -> None
```

Kennzahlen anmelden: im Rechenwerk, als Ziel ihres Bauteils und unter
ihm in der Zusammenfassung – ein Weg wie für die Nachweise
([[opencivil.projekt.aufbau.kern#Aufbau.eintragen|eintragen]]). Bis 2026-11-27 schrieben Querschnittsanalyse und
Pfahl dieselben drei Zeilen je selbst.

#### Aufbau.bauteile

```python
def bauteile(self) -> List['Bauteil']
```

Jedes Bauteil, in der Reihenfolge von [[opencivil.projekt.aufbau#Konstanten|BAUTEILE]] und der
Beschreibung: erst die Platten, dann die Querschnittsanalysen, dann
die Balkensysteme – sie lesen Werte der beiden anderen.

Die eine Stelle, die diese Reihenfolge festlegt – fuer die Rechenziele,
den Zwischenspeicher und die Zusammenfassung.

#### Aufbau.bauteil

```python
def bauteil(self, kennung: str) -> 'Bauteil'
```

Ein gebautes Bauteil – fuer eines, dem noch etwas fehlt, sagt der Fehler, was.

#### Aufbau.bauteil_von

```python
def bauteil_von(self, nachweis: Nachweis) -> 'Bauteil'
```

Das Bauteil, bei dem ein Nachweis angemeldet ist.

#### Aufbau.ziele_von

```python
def ziele_von(self, kennung: str) -> List[str]
```

Die Rechenziele eines einzelnen Bauteils – siehe [[opencivil.projekt.aufbau.kern#Bauteil.ziele|Bauteil.ziele]].

#### Aufbau.ziele_je_bauteil

```python
def ziele_je_bauteil(self) -> List[Tuple[str, List[str]]]
```

Die Rechenziele Bauteil fuer Bauteil, in der Reihenfolge von
[[opencivil.projekt.aufbau.kern#Aufbau.bauteile|bauteile]].

Die Oberflaeche geht darueber, um je Bauteil zwischenzuspeichern
([[opencivil.web.dienst#_stromabwaerts|opencivil.web.dienst._stromabwaerts]]); [[opencivil.projekt.aufbau.kern#Aufbau.alle_ziele|alle_ziele]]
haengt sie aneinander. Vorher bildete jede der beiden die Folge
selbst, und dass sie gleich war, stand nur im Docstring.

#### Aufbau.alle_ziele

```python
def alle_ziele(self) -> List[str]
```

Was ein vollstaendiger Lauf rechnet, in der Reihenfolge der Herleitung:
erst die Baustoffe, dann Platte fuer Platte ihre Eckwerte und
Nachweise. Wer ohne Oberflaeche rechnet, bekommt so denselben Bericht.

#### Aufbau.berichtsziele

```python
def berichtsziele(self) -> List[str]
```

Was im Bericht steht: Nachweise und was die Bauteile sonst rechnen –
ohne die Baustoffkennwerte, die niemand braucht.

#### Aufbau.urteile_von

```python
def urteile_von(self, kennung: str, urteile: Iterable[NachweisUrteil]) -> List[NachweisUrteil]
```

Die Urteile eines Bauteils – erkannt an den Nachweisen, die bei ihm
angemeldet sind.

Nicht am Namen: den Anzeigetext zu zerlegen hat schon einmal die
Nachweise mehrerer Platten in dieselbe Tabelle gepackt.

#### Aufbau.materialziele

```python
def materialziele(self) -> List[str]
```

Saemtliche Kennwerte aller Materialien – in der Folge der Arten,
Beton zuerst, dann die Staehle ([[opencivil.material.arten#Konstanten|MATERIALARTEN]]).

Gehoert zum Regellauf: ein Material, das noch keine Platte verwendet,
waere sonst nie Ziel und bliebe ungerechnet – im Editor staenden dann
leere Felder, obwohl die Sorte alles hergibt.

Die Reihenfolge bestimmt zugleich den Aufbau der Herleitung: der Loeser
arbeitet die Ziele der Reihe nach ab, und das Protokoll folgt ihm. So
stehen im Bericht erst die Baustoffe und dann die Bauteile.

### Unfertiges

```python
@dataclass(frozen=True)
class Unfertiges
```

Ein Bauteil oder Material, dem noch etwas fehlt – seine Liste im
Projekt, sein Name, wie es in Meldungen heisst, und was
([[opencivil.projekt.aufbau.kern#Aufbau.unfertig|Aufbau.unfertig]]).

- `liste: str`
- `name: str`
- `wo: str`
- `grund: str`

#### Unfertiges.meldung

```python
@property
def meldung(self) -> str
```

Für wen nach ihm fragt: «Platte 'Decke': noch keine Bewehrung.»

### Bauteil

```python
@dataclass
class Bauteil
```

Ein gebautes Bauteil und was zu ihm gehoert. Wem ein Nachweis gehoert,
steht hier – niemand muss es aus einer Kennung wie «q1.x» zurueckgewinnen.

- `eintrag: Any` – Der Eintrag des Projekts, aus dem es gebaut ist – fuer ein Bild, das nach einem seiner Felder fragt, etwa der Normalkraft der M-V-Kurve.
- `art: 'Bauteilart'`
- `objekt: Any` – Der Plattenquerschnitt, die Querschnittsanalyse oder das Balkensystem.
- `nachweise: List[Tuple[str, str, Nachweis]] = field(default_factory=list)` – Feld, Schluessel und Nachweis, angemeldet ueber [[opencivil.projekt.aufbau.kern#Aufbau.eintragen|Aufbau.eintragen]].
- `weitere_ziele: List[str] = field(default_factory=list)` – Was es ausser seinen Nachweisen rechnet – ein Balkensystem seine Querschnitte und sich.
- `kennzahlen: List[Kennzahl] = field(default_factory=list)` – Was es beschreibt, gleich welche Lastfaelle es gibt, in der Folge der Zusammenfassung – jede so, wie ihr Erzeuger sie nennt.
- `ohne_nachweis: str = ''` – Warum es keinen seiner Nachweise fuehrt – leer, wenn nichts fehlt ([[opencivil.projekt.aufbau.kern#Aufbau.ohne_nachweis|Aufbau.ohne_nachweis]]).

#### Bauteil.bezuege

```python
@property
def bezuege(self) -> Tuple[str, ...]
```

Die Bauteile, deren Werte es liest – so, wie sein Eintrag sie nennt:
die Platten und Analysen, aus denen ein System Querschnitte nimmt,
die Analysen der Waende eines Gebaeudes.

Bis 2026-11-27 setzte jede Baufunktion sie selbst, und das Erdbeben
vergass es: aenderte sich nur die Analyse einer Wand, blieb im
Zwischenspeicher das alte Ergebnis stehen.

#### Bauteil.kennung

```python
@property
def kennung(self) -> str
```

#### Bauteil.name

```python
@property
def name(self) -> str
```

#### Bauteil.raum

```python
@property
def raum(self) -> str
```

Der Namensraum seiner Werte und Urteile.

#### Bauteil.im_feld

```python
def im_feld(self, feld: str) -> List[Nachweis]
```

Seine Nachweise in einem Feld des [[opencivil.projekt.aufbau.kern#Aufbau|Aufbau]], in der Folge der Anmeldung.

#### Bauteil.ziele

```python
def ziele(self) -> List[str]
```

Was ein Lauf fuer dieses Bauteil rechnet: die Nachweise in der Folge
von [[opencivil.projekt.aufbau.kern#Aufbau|Aufbau.NACHWEISFELDER]], dann die weiteren Ziele.

### kennwertbereich

```python
def kennwertbereich(vorlage: KennwertVorlage) -> Bereich
```

Wo ein Kennwert eines Baustoffs liegen muss: ueber null. Festigkeiten,
Moduln, Dehnungen, Teilsicherheitsbeiwerte sind ihrer Natur nach
positiv; eine Null oder ein negativer Wert liefert keine falsche Zahl,
sondern gar keine – gamma_c = 0 endete in einem ZeroDivisionError, ein
negatives f_ck in einer komplexen Wurzel. Beides kam als Absturzmeldung
beim Benutzer an.

Der Aufbau prueft damit jede Abweichung und Ueberschreibung
([[opencivil.projekt.aufbau.kern#baustoff_bauen|baustoff_bauen]]), die Oberflaeche liest dieselbe Grenze aus dem
Katalog (`materialarten`) und weist eine Null schon am Feld ab. Bis
2026-11-19 fuehrten die Pfeile dort bis 0.

### baustoff_bauen

```python
def baustoff_bauen(eintrag: MaterialEintrag, symbol_index: str, wo: str) -> Baustoff
```

### material

```python
def material(baustoffe: Mapping[str, Baustoff], kennung: str, art: Union[str, Sequence[str]], wo: str, feld: str) -> Baustoff
```

Das Material, das `feld` des Bauteils `wo` waehlt: es muss es geben,
und es muss von dieser Art sein – oder von einer dieser Arten, etwa bei
der Flaeche einer Querschnittsanalyse ([[opencivil.projekt.lesen#materialfeld|materialfeld]]).
Ohne Angabe gilt nicht «das erste im
Projekt» – bis 2026-10-16 bekamen Buegel und Staebe ohne Stahl still den
ersten. `feld` heisst wie in der Oberflaeche: was nicht stimmt, steht
am Bauteil ([[opencivil.projekt.aufbau.kern#Aufbau.unfertig|Aufbau.unfertig]]), dort genuegt das Feld.

### kennwert

```python
def kennwert(aufbau: Aufbau, stoff: Baustoff, kurzname: str) -> Groesse
```

Ein Kennwert eines Materials, wie das Projekt ihn rechnet: mit
Abweichungen und Ueberschreibungen. Fuer eine Regel, die ein Bauteil
schon beim Bauen gegen ein Material prueft – den Boden gegen das Gewicht
seines Wassers. Dafuer stehen die Materialien vor den Bauteilen im Werk
([[opencivil.projekt.aufbau#aufbauen|aufbauen]]).

### schwerer_als_wasser

```python
def schwerer_als_wasser(gamma: float, wasser: Baustoff, aufbau: Aufbau, wo: str, was: str='die Raumlast des Bodens') -> None
```

Haelt auf, wenn ein Boden mit der Raumlast `gamma` in kN/m³ nicht
schwerer ist als sein Wasser: unter dem Spiegel zaehlt gamma - gamma_w,
und ohne Gewicht gibt es dort weder Reibung noch Widerstand. Fuer
Grundbruch und Pfahl – bis 2026-11-27 je in den Regeln ihres Eintrags,
als gamma_w noch eine Zahl dort war.

### ohne_kombination

```python
def ohne_kombination(kombinationen: Sequence[Any]) -> str
```

Warum ein Bauteil mit Einwirkungen keinen Nachweis fuehrt: es hat noch keine, oder jede ist aus.

### Grund

```python
class Grund(NamedTuple)
```

Warum eine Wahl nicht rechnet, klein beginnend. `falsch`: sie
widerspricht sich – etwa ein Stahl, wo ein Beton hingehoert – und steht
rot. Sonst fehlt nur etwas, und sie steht grau, auch wo die Rechnung ohne
sie anhaelt (Benutzer, 2026-11-19).

- `text: str`
- `falsch: bool = False`

### materialgrund

```python
def materialgrund(kennung: str, gefunden: Optional[Tuple[str, str]], art: Union[str, Sequence[str]]) -> Optional[Grund]
```

Was an der Wahl eines Materials nicht stimmt, ohne Ort – `None`, wenn
sie stimmt. `gefunden` sind Art und Name des gewaehlten, `None`, wenn
es das nicht gibt; `art` eine Art oder mehrere, die passen. Falsch ist
nur die falsche Art – «ist kein Beton, Baustahl oder Holz», «ist keine
Fluessigkeit» ([[opencivil.material.arten#keines|keines]]); ein geloeschtes oder
noch nicht gewaehltes fehlt nur. Das geloeschte nennt der Satz nicht beim
Namen: den kennt das Projekt nicht mehr, und die Kennung steht nirgends,
wo der Benutzer sie saehe – bis 2026-11-19 hiess es «das Material 'b9'».
Die Regel fuer [[opencivil.projekt.aufbau.kern#material|material]] und fuer die Meldungen an der Zeichnung
([[opencivil.web.zeichengeometrie#geometrie|opencivil.web.zeichengeometrie.geometrie]]).

### ueberschreibungen_setzen

```python
def ueberschreibungen_setzen(projekt: 'Projekt', werk: Rechenwerk, aufbau: Aufbau) -> None
```

Die von Hand ueberschriebenen Kennwerte – dass es sie gibt, prueft
`baustoff_bauen`. Ein Material, das nicht rechnet, hat keine.

### baustoff_im_werk

```python
def baustoff_im_werk(eintrag: MaterialEintrag, werk: Rechenwerk) -> Optional[Baustoff]
```

Ein Material als Baustoff in `werk`, mit Abweichungen und
Ueberschreibungen, wie das Projekt es rechnet – ohne das Projekt zu
bauen. `None`, wenn es nicht rechnet: was ihm fehlt, sagt es selbst.
Fuer das Zeichenfenster, das zu einem Spannglied schon beim Zeichnen
seine Spannkraft nennt ([[opencivil.web.zeichengeometrie]]).

### stoffe_von

```python
def stoffe_von(aufbau: Aufbau, baustoffe: Iterable[Baustoff]) -> Dict[str, Baustoff]
```

Die Baustoffe eines Bauteils unter ihrer Kennung im Projekt – danach
waehlt ein Kapitel seine Werte je Material
([[opencivil.projekt.eintraege#JeMaterial|JeMaterial]]).

### spannungsfaelle

```python
def spannungsfaelle(eintrag, stoffe: Mapping[str, Baustoff], aufbau: Aufbau) -> None
```

Die eingeschalteten Spannung-Dehnung-Analysen eines Bauteils, jede mit ihrer Wahl an ihm.

### spannungsnachweise

```python
def spannungsnachweise(eintrag, ort: Stahlspannungsort, kombinationen: Sequence[Any], fall: Callable[[str, Any, float], Any], *, praefix: str, kennung: str, aufbau: Aufbau, teil: Bauteil) -> None
```

Die Stahlspannung, zweimal: aus der Rissbreite unter quasi-staendiger
Einwirkung (bei jeder Anforderung) und gegen Fliessen unter haeufiger
(nur bei erhoehter und hoher). Welche wann gilt, weiss die Grenze selbst.

Fuer die Platte und den gezeichneten Querschnitt dieselbe Schleife: `ort`
sagt, wo gemessen wird, `fall` macht die Faelle
([[opencivil.projekt.aufbau.kern#_gebrauchsfaelle|_gebrauchsfaelle]]), `praefix` das Feld des Aufbaus – «qa_»
beim gezeichneten Querschnitt. Bis 2026-10-17 stand sie zweimal da.

### _gebrauchsfaelle

```python
def _gebrauchsfaelle(kombinationen: Sequence[Any], liste: Gebrauchsliste, fall: Callable[[str, Any, float], Any]) -> Tuple[List[Any], List[str]]
```

Die Lastfaelle eines Stahlspannungsnachweises – und welche laut sind.

Einmal fuer die haeufigen, einmal fuer die quasi-staendigen; beide
Listen werden gleich gebildet und unterscheiden sich nur im Anteil.
`fall(name, eintrag, faktor)` macht aus einem Eintrag – einer
Kombination der Tragsicherheit oder einem eigenen Fall – den Fall des
Nachweises: bei der Platte einen
[[opencivil.nachweis.spannungsbegrenzung#Gebrauchsfall|Gebrauchsfall]], beim
gezeichneten Querschnitt einen [[opencivil.querschnitt.analyse#Lastfall|Lastfall]].

Die eigens angegebenen, und zusaetzlich die Tragsicherheitsfaelle mit
`liste.anteil` Prozent. Beides nebeneinander: der Anteil ist eine bequeme
Abschaetzung, deckt aber nicht den Fall ab, den es nur unter
Gebrauchslast gibt. Wer einen solchen kennt, soll ihn dazustellen
koennen, ohne die Abschaetzung fuer alle anderen aufzugeben.

Die abgeleiteten Faelle entstehen auch dann, wenn
`liste.aus_tragsicherheit` aus ist
– dann eben still. Sie ganz wegzulassen hiesse, den Nachweis erst auf
Verlangen zu fuehren; so steht wenigstens ein Hinweis da, wenn die
Abschaetzung nicht aufgeht.

**Was das kostet.** Jeder Fall ist ein Gleichgewicht am gerissenen
Querschnitt, also ein Durchlauf des Faserloesers – rund 8 ms.
Gemessen an der Beispielplatte mit drei Kombinationen: der
quasi-staendige Nachweis laeuft immer und hebt die ganze Rechnung von
27 auf 52 ms; bei erhoehter Anforderung kommt der haeufige dazu, 79 ms.
Die Bewehrungssuche zahlt davon nichts, solange beide still sind –
im schnellen Aufbau entstehen ganz stille Nachweise gar nicht (2.5
statt 29 ms je Bewertung bei erhoehter Anforderung). Wer die Zeit
auch in der Anzeige zurueckhaben will, kommt nicht an dieser Stelle
weiter, sondern am Loeser.

Die Rechnung steht hier und nicht in der Oberflaeche: dort waere sie
eine zweite Wahrheit.

### knickfall

```python
def knickfall(k: KnickEintrag, klasse: type=Knickfall, **mehr: Any) -> Knickfall
```

Ein Knickfall aus seiner Beschreibung – jede Zahl in der Einheit ihres
Feldes; `mehr` fuer die Analyse.


## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.bereich]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.nachweis]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.core.wert]]
- [[opencivil.decke.werk]]
- [[opencivil.geotechnik.fundament]]
- [[opencivil.geotechnik.setzung]]
- [[opencivil.material.arten]]
- [[opencivil.material.basis]]
- [[opencivil.nachweis.kennzahlen]]
- [[opencivil.nachweis.knicken]]
- [[opencivil.nachweis.spannungsbegrenzung]]
- [[opencivil.nachweis.spannungsgrenzen]]
- [[opencivil.pfahl.pfahl]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.projekt]]
- [[opencivil.querschnitt.gesetzwahl]]
- [[opencivil.querschnitt.platte]]
- [[opencivil.stabwerk.rechnung]]
- [[opencivil.stabwerk3d.rechnung]]

## Gebraucht von

- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.balkensystem]]
- [[opencivil.projekt.aufbau.balkensystem3d]]
- [[opencivil.projekt.aufbau.decke]]
- [[opencivil.projekt.aufbau.durchstanzen]]
- [[opencivil.projekt.aufbau.erdbeben]]
- [[opencivil.projekt.aufbau.grundbruch]]
- [[opencivil.projekt.aufbau.pfahl]]
- [[opencivil.projekt.aufbau.platte]]
- [[opencivil.projekt.aufbau.querschnittsanalyse]]
- [[opencivil.projekt.aufbau.setzung]]
- [[opencivil.web.api]]
- [[opencivil.web.erdbebendaten]]
- [[opencivil.web.zeichengeometrie]]
