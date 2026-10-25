---
erzeugt: 8c2b1a3b8904
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
([[opencivil.projekt.aufbau.kern#knickfall|knickfall]]) -- Platte und gezeichneter Querschnitt rufen dieselben.

Was nur eine Art braucht, steht bei ihr: [[opencivil.projekt.aufbau.platte|platte]],
[[opencivil.projekt.aufbau.querschnittsanalyse|querschnittsanalyse]],
[[opencivil.projekt.aufbau.balkensystem|balkensystem]],
[[opencivil.projekt.aufbau.grundbruch|grundbruch]] und
[[opencivil.projekt.aufbau.setzung|setzung]]. Bis 2026-10-17 stand alles in
einer Datei `aufbau.py` von ueber tausend Zeilen.

## Inhalt

### Aufbau

```python
@dataclass
class Aufbau
```

Was beim Zusammenbauen eines Projekts entsteht.

- `werk: Rechenwerk`
- `schnell: bool = False` – Fuer die Bewehrungssuche gebaut -- siehe [[opencivil.projekt.aufbau#aufbauen|aufbauen]].
- `teile: Dict[str, 'Bauteil'] = field(default_factory=dict)` – Jedes Bauteil nach Kennung, in der Reihenfolge von [[opencivil.projekt.aufbau#Konstanten|BAUTEILE]] und der Beschreibung.
- `baustoffe: Dict[str, Baustoff] = field(default_factory=dict)`
- `nachweise: Dict[str, BiegungNormalkraft] = field(default_factory=dict)` – Schluessel ist `<querschnitt>.x`. Die Richtung steht noch im Schluessel, obwohl es nur eine gibt -- sie sagt dem Leser einer Wert-ID, welcher Querschnitt gemeint ist, und die Wert-IDs in abgelegten Berichten sollen nicht bei jeder Umstellung wechseln.
- `querkraft: Dict[str, Querkraft] = field(default_factory=dict)`
- `duktilitaet: Dict[str, Duktilitaet] = field(default_factory=dict)` – Schluessel ist die Querschnittskennung -- ein Nachweis je Platte.
- `rissnormalkraft: Dict[str, Rissnormalkraft] = field(default_factory=dict)` – Schluessel ist `<querschnitt>.x`.
- `sproede: Dict[str, SproedesVersagen] = field(default_factory=dict)` – Mindestbewehrung gegen sproedes Versagen, je `<querschnitt>.x`.
- `zwaengung_biegung: Dict[str, ZwaengungBiegung] = field(default_factory=dict)` – Zwaengung auf Biegung, je `<querschnitt>.x`.
- `spannung: Dict[str, Spannungsbegrenzung] = field(default_factory=dict)` – Stahlspannung gegen Fliessen unter haeufiger Einwirkung, je `<querschnitt>.x`.
- `spannung_riss: Dict[str, Spannungsbegrenzung] = field(default_factory=dict)` – Stahlspannung aus der Rissbreite unter quasi-staendiger Einwirkung, je `<querschnitt>.x`.
- `verformung: Dict[str, Verformung] = field(default_factory=dict)` – Die Durchbiegung je Verformungsfall, je Querschnitt -- nur in x-Richtung.
- `kennzahlen: Dict[str, Plattenkennzahlen] = field(default_factory=dict)` – Die Kennzahlen je Platte mit x-Bewehrung -- immer gerechnet.
- `knicken: Dict[str, Knicken] = field(default_factory=dict)` – Nachweis am verformten System, je Querschnitt -- nur in x-Richtung.
- `fehlende: Dict[str, FehlendeBewehrung] = field(default_factory=dict)` – Je Richtung ohne Bewehrung, fuer die dennoch Einwirkungen angegeben sind. Sie rechnen nichts; sie sorgen dafuer, dass in der Zusammenfassung eine Zeile mit Erfuellungsgrad null steht statt gar nichts.
- `spannungsfaelle: Dict[str, List['SpannungsfallEintrag']] = field(default_factory=dict)` – Je Platte die Auswertungen am Querschnitt -- als Beschreibung, nicht als Nachweis. Sie laufen nicht im Rechenwerk: sie haben kein Ziel, das jemand anderes brauchen koennte, und nichts haengt von ihnen ab.
- `leere_analysen: Dict[str, str] = field(default_factory=dict)` – Je Querschnittsanalyse, in der noch nichts gezeichnet ist, ihr Name. Sie wird kein Bauteil -- es gibt nichts zu rechnen --, aber wer auf sie zeigt, soll hoeren, dass sie leer ist, und nicht, es gebe sie nicht.
- `qa_biegung: Dict[str, SchiefeBiegung] = field(default_factory=dict)` – Biegung und Normalkraft je Querschnittsanalyse, nach ihrer Kennung.
- `qa_schub: Dict[str, Schubwandnachweis] = field(default_factory=dict)` – Querkraft und Torsion je Querschnittsanalyse.
- `qa_duktilitaet: Dict[str, DuktilitaetQA] = field(default_factory=dict)`
- `qa_sproede: Dict[str, SproedesVersagenQA] = field(default_factory=dict)`
- `qa_rissnormalkraft: Dict[str, RissnormalkraftQA] = field(default_factory=dict)`
- `qa_zwaengung_biegung: Dict[str, ZwaengungBiegungQA] = field(default_factory=dict)`
- `qa_spannung_riss: Dict[str, Spannungsbegrenzung] = field(default_factory=dict)`
- `qa_spannung: Dict[str, Spannungsbegrenzung] = field(default_factory=dict)` – Die Gebrauchsnachweise je Querschnittsanalyse, wie bei der Platte.
- `qa_knicken: Dict[str, KnickenQA] = field(default_factory=dict)` – Knicken je Querschnittsanalyse -- je Fall in seiner Richtung.
- `grundbruch: Dict[str, Grundbruch] = field(default_factory=dict)`
- `gleiten: Dict[str, Gleiten] = field(default_factory=dict)` – Grundbruch und Gleiten je Fundament.
- `setzung: Dict[str, Setzung] = field(default_factory=dict)` – Die Setzung je Fundament.
- `warnungen: List[str] = field(default_factory=list)`
- `NACHWEISFELDER = ('nachweise', 'querkraft', 'duktilitaet', 'fehlende', 'rissnormalkraf…` – Die Felder, in denen die Nachweise stehen -- die eine Stelle, an der ein neuer Nachweis eingetragen wird. Alle sind nach Kennung geschluesselt (`q1` oder `q1.x`) und alle tragen Nachweise mit `d_ausnutzung`. Ihre Reihenfolge ist die der Herleitung: in ihr rechnet ein Bauteil seine Nachweise ([[opencivil.projekt.aufbau.kern#Bauteil.ziele|Bauteil.ziele]]).

#### Aufbau.objekte

```python
def objekte(self, art: str) -> Dict[str, Any]
```

Die gebauten Objekte einer Bauteilart nach Kennung -- `art` ist ihr Name.

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

Die Balkensysteme, nach Kennung -- Bauteile ohne Nachweise, mit ihrem Ergebnis.

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

Jeden Nachweis als Ziel -- auch einen ohne Lastfall, der nur fuer sein Bild rechnet.

#### Aufbau.eintragen

```python
def eintragen(self, teil: 'Bauteil', feld: str, schluessel: str, nachweis: Nachweis) -> None
```

Einen Nachweis anmelden: im Rechenwerk, in seinem Feld und bei seinem
Bauteil -- ausser er ist ganz still, und es wird schnell gerechnet.

Den schnellen Weg nimmt nur die Bewehrungssuche, und die zaehlt
stille Urteile nicht ([[opencivil.projekt.aufbau.kern#Aufbau|bewehrungssuche.bewerte]]). Ein ganz
stiller Nachweis kann ihr Ergebnis also nicht aendern, er kostet
nur Zeit -- und bei der Stahlspannung, die immer mitlaeuft, ist
das der groessere Teil der ganzen Rechnung. Exakt und nicht
genaehert: gezaehlt wird dasselbe wie vorher.

Jeder Nachweis geht hier durch, auch die, die nie still sind -- ein
Weg zum Anmelden, nicht zwei.

#### Aufbau.bauteile

```python
def bauteile(self) -> List['Bauteil']
```

Jedes Bauteil, in der Reihenfolge von [[opencivil.projekt.aufbau#Konstanten|BAUTEILE]] und der
Beschreibung: erst die Platten, dann die Querschnittsanalysen, dann
die Balkensysteme -- sie lesen Werte der beiden anderen.

Die eine Stelle, die diese Reihenfolge festlegt -- fuer die Rechenziele,
den Zwischenspeicher und die Zusammenfassung.

#### Aufbau.bauteil

```python
def bauteil(self, kennung: str) -> 'Bauteil'
```

#### Aufbau.bauteil_von

```python
def bauteil_von(self, nachweis: Nachweis) -> 'Bauteil'
```

Das Bauteil, bei dem ein Nachweis angemeldet ist.

#### Aufbau.ziele_von

```python
def ziele_von(self, kennung: str) -> List[str]
```

Die Rechenziele eines einzelnen Bauteils -- siehe [[opencivil.projekt.aufbau.kern#Bauteil.ziele|Bauteil.ziele]].

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

Was im Bericht steht: Nachweise und was die Bauteile sonst rechnen --
ohne die Baustoffkennwerte, die niemand braucht.

#### Aufbau.urteile_von

```python
def urteile_von(self, kennung: str, urteile: Iterable[NachweisUrteil]) -> List[NachweisUrteil]
```

Die Urteile eines Bauteils -- erkannt an den Nachweisen, die bei ihm
angemeldet sind.

Nicht am Namen: den Anzeigetext zu zerlegen hat schon einmal die
Nachweise mehrerer Platten in dieselbe Tabelle gepackt.

#### Aufbau.materialziele

```python
def materialziele(self) -> List[str]
```

Saemtliche Kennwerte aller Materialien -- Beton zuerst, dann Betonstahl.

Gehoert zum Regellauf: ein Material, das noch keine Platte verwendet,
waere sonst nie Ziel und bliebe ungerechnet -- im Editor staenden dann
leere Felder, obwohl die Sorte alles hergibt.

Die Reihenfolge bestimmt zugleich den Aufbau der Herleitung: der Loeser
arbeitet die Ziele der Reihe nach ab, und das Protokoll folgt ihm. So
stehen im Bericht erst die Baustoffe und dann die Bauteile.

### Bauteil

```python
@dataclass
class Bauteil
```

Ein gebautes Bauteil und was zu ihm gehoert. Wem ein Nachweis gehoert,
steht hier -- niemand muss es aus einer Kennung wie «q1.x» zurueckgewinnen.

- `kennung: str`
- `name: str`
- `art: 'Bauteilart'`
- `objekt: Any` – Der Plattenquerschnitt, die Querschnittsanalyse oder das Balkensystem.
- `nachweise: List[Tuple[str, Nachweis]] = field(default_factory=list)` – Feld im [[opencivil.projekt.aufbau.kern#Aufbau|Aufbau]] und Nachweis, angemeldet ueber [[opencivil.projekt.aufbau.kern#Aufbau.eintragen|Aufbau.eintragen]].
- `weitere_ziele: List[str] = field(default_factory=list)` – Was es ausser seinen Nachweisen rechnet -- ein Balkensystem seine Querschnitte und sich.
- `kennzahlen: List[Kennzahl] = field(default_factory=list)` – Was es beschreibt, gleich welche Lastfaelle es gibt, in der Folge der Zusammenfassung -- jede so, wie ihr Erzeuger sie nennt.
- `bezuege: Tuple[str, ...] = ()` – Die Bauteile, deren Werte es liest: Platten und Analysen, aus denen ein System Querschnitte nimmt.

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

### baustoff_bauen

```python
def baustoff_bauen(eintrag: MaterialEintrag, symbol_index: str) -> Baustoff
```

### material

```python
def material(baustoffe: Mapping[str, Baustoff], kennung: str, art: str, wer: str) -> Baustoff
```

Das Material, auf das ein Eintrag zeigt: es muss es geben, und es muss
von dieser Art sein. Ohne Angabe gilt nicht «das erste im Projekt» -- bis
2026-10-16 bekamen Buegel und Staebe ohne Stahl still den ersten.

### ueberschreibungen_setzen

```python
def ueberschreibungen_setzen(projekt: 'Projekt', werk: Rechenwerk, aufbau: Aufbau) -> None
```

Die von Hand ueberschriebenen Kennwerte -- dass es sie gibt, prueft `baustoff_bauen`.

### spannungsnachweise

```python
def spannungsnachweise(eintrag, ort: Stahlspannungsort, kombinationen: Sequence[Any], fall: Callable[[str, Any, float], Any], *, praefix: str, kennung: str, aufbau: Aufbau, teil: Bauteil) -> None
```

Die Stahlspannung, zweimal: aus der Rissbreite unter quasi-staendiger
Einwirkung (bei jeder Anforderung) und gegen Fliessen unter haeufiger
(nur bei erhoehter und hoher). Welche wann gilt, weiss die Grenze selbst.

Fuer die Platte und den gezeichneten Querschnitt dieselbe Schleife: `ort`
sagt, wo gemessen wird, `fall` macht die Faelle
([[opencivil.projekt.aufbau.kern#_gebrauchsfaelle|_gebrauchsfaelle]]), `praefix` das Feld des Aufbaus -- «qa_»
beim gezeichneten Querschnitt. Bis 2026-10-17 stand sie zweimal da.

### _gebrauchsfaelle

```python
def _gebrauchsfaelle(kombinationen: Sequence[Any], liste: Gebrauchsliste, fall: Callable[[str, Any, float], Any]) -> Tuple[List[Any], List[str]]
```

Die Lastfaelle eines Stahlspannungsnachweises -- und welche laut sind.

Einmal fuer die haeufigen, einmal fuer die quasi-staendigen; beide
Listen werden gleich gebildet und unterscheiden sich nur im Anteil.
`fall(name, eintrag, faktor)` macht aus einem Eintrag -- einer
Kombination der Tragsicherheit oder einem eigenen Fall -- den Fall des
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
-- dann eben still. Sie ganz wegzulassen hiesse, den Nachweis erst auf
Verlangen zu fuehren; so steht wenigstens ein Hinweis da, wenn die
Abschaetzung nicht aufgeht.

**Was das kostet.** Jeder Fall ist ein Gleichgewicht am gerissenen
Querschnitt, also ein Durchlauf des Faserloesers -- rund 8 ms.
Gemessen an der Beispielplatte mit drei Kombinationen: der
quasi-staendige Nachweis laeuft immer und hebt die ganze Rechnung von
27 auf 52 ms; bei erhoehter Anforderung kommt der haeufige dazu, 79 ms.
Die Bewehrungssuche zahlt davon nichts, solange beide still sind --
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

Ein Knickfall aus seiner Beschreibung -- kN, kNm und m; `mehr` fuer die Analyse.


## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.core.wert]]
- [[opencivil.geotechnik.grundbruch]]
- [[opencivil.geotechnik.setzung]]
- [[opencivil.material.basis]]
- [[opencivil.material.beton]]
- [[opencivil.material.betonstahl]]
- [[opencivil.nachweis.biegung_normalkraft]]
- [[opencivil.nachweis.duktilitaet]]
- [[opencivil.nachweis.fehlende_bewehrung]]
- [[opencivil.nachweis.kennzahlen]]
- [[opencivil.nachweis.knicken]]
- [[opencivil.nachweis.mindestbewehrung]]
- [[opencivil.nachweis.qa_gebrauch]]
- [[opencivil.nachweis.qa_knicken]]
- [[opencivil.nachweis.querkraft]]
- [[opencivil.nachweis.richtungsnachweise]]
- [[opencivil.nachweis.schiefe_biegung]]
- [[opencivil.nachweis.schubwandnachweis]]
- [[opencivil.nachweis.spannungsbegrenzung]]
- [[opencivil.nachweis.spannungsgrenzen]]
- [[opencivil.nachweis.sproedes_versagen]]
- [[opencivil.nachweis.verformung]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.projekt]]
- [[opencivil.querschnitt.platte]]
- [[opencivil.stabwerk.rechnung]]

## Gebraucht von

- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.balkensystem]]
- [[opencivil.projekt.aufbau.grundbruch]]
- [[opencivil.projekt.aufbau.platte]]
- [[opencivil.projekt.aufbau.querschnittsanalyse]]
- [[opencivil.projekt.aufbau.setzung]]
