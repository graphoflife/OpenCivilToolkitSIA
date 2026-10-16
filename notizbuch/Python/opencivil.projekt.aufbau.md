---
erzeugt: a339a48c3011
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/aufbau.py
> aus der Beschreibung ein Rechenwerk.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/aufbau.py)

## VERANTWORTUNG

[[opencivil.projekt.aufbau#aufbauen|aufbauen]] macht aus einem [[opencivil.projekt.projekt#Projekt|Projekt]] Baustoffe, Querschnitte,
Nachweise und Balkensysteme und meldet sie in einem [[opencivil.core.rechenwerk#Rechenwerk|Rechenwerk]] an.
Heraus kommt ein [[opencivil.projekt.aufbau#Aufbau|Aufbau]] -- das Werk samt allen Nachweisobjekten und
Systemen, nach Bauteil und Art abgelegt, damit Schnittstelle,
Zwischenspeicher und Bewehrungssuche sie wiederfinden.

Die Beschreibung selbst rechnet nichts; hier wird sie zum ersten Mal
Rechnung. Darum stehen auch die Pruefungen hier, die erst beim Bauen
auffallen koennen -- ein Verweis auf ein geloeschtes Material, eine Platte
ohne Bewehrung.


## DIE BAUTEILARTEN

Platte, Querschnittsanalyse, Balkensystem und Grundbruch haben je einen Steckbrief
([[opencivil.projekt.aufbau#Bauteilart|Bauteilart]]) in [[opencivil.projekt.aufbau#Konstanten|BAUTEILE]] -- Liste in der Datei, Klasse der
Eintraege, Vorsilbe der Kennungen, Namensraum, Baufunktion. Wer alle
Bauteile durchgeht, geht diese Liste durch; eine neue Art kommt dort dazu
und nirgends sonst. Gebaut wird je Eintrag ein [[opencivil.projekt.aufbau#Bauteil|Bauteil]], das seine
Nachweise, Ziele und Bezuege selbst fuehrt.

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
- `querschnitte: Dict[str, Plattenquerschnitt] = field(default_factory=dict)`
- `nachweise: Dict[str, BiegungNormalkraft] = field(default_factory=dict)` – Schluessel ist `<querschnitt>.x`. Die Richtung steht noch im Schluessel, obwohl es nur eine gibt -- sie sagt dem Leser einer Wert-ID, welcher Querschnitt gemeint ist, und die Wert-IDs in abgelegten Berichten sollen nicht bei jeder Umstellung wechseln.
- `querkraft: Dict[str, Querkraft] = field(default_factory=dict)`
- `duktilitaet: Dict[str, Duktilitaet] = field(default_factory=dict)` – Schluessel ist die Querschnittskennung -- ein Nachweis je Platte.
- `rissnormalkraft: Dict[str, Rissnormalkraft] = field(default_factory=dict)` – Schluessel ist `<querschnitt>.x`.
- `sproede: Dict[str, SproedesVersagen] = field(default_factory=dict)` – Mindestbewehrung gegen sproedes Versagen, je `<querschnitt>.x`.
- `zwaengung_biegung: Dict[str, ZwaengungBiegung] = field(default_factory=dict)` – Zwaengung auf Biegung, je `<querschnitt>.x`.
- `spannung: Dict[str, Spannungsbegrenzung] = field(default_factory=dict)` – Stahlspannung gegen Fliessen unter haeufiger Einwirkung, je `<querschnitt>.x`.
- `spannung_riss: Dict[str, Spannungsbegrenzung] = field(default_factory=dict)` – Stahlspannung aus der Rissbreite unter quasi-staendiger Einwirkung, je `<querschnitt>.x`.
- `verformung: Dict[str, Verformung] = field(default_factory=dict)` – Die Durchbiegung je Verformungsfall, je Querschnitt -- nur in x-Richtung.
- `vergroesserung: Dict[str, Vergroesserungsfaktor] = field(default_factory=dict)` – Die Vergroesserungsfaktoren je Platte mit x-Bewehrung -- immer gerechnet.
- `kennzahlen: Dict[str, Plattenkennzahlen] = field(default_factory=dict)` – Die Kennzahlen je Platte mit x-Bewehrung -- immer gerechnet.
- `knicken: Dict[str, Knicken] = field(default_factory=dict)` – Nachweis am verformten System, je Querschnitt -- nur in x-Richtung.
- `fehlende: Dict[str, FehlendeBewehrung] = field(default_factory=dict)` – Je Richtung ohne Bewehrung, fuer die dennoch Einwirkungen angegeben sind. Sie rechnen nichts; sie sorgen dafuer, dass in der Zusammenfassung eine Zeile mit Erfuellungsgrad null steht statt gar nichts.
- `spannungsfaelle: Dict[str, List['SpannungsfallEintrag']] = field(default_factory=dict)` – Je Platte die Auswertungen am Querschnitt -- als Beschreibung, nicht als Nachweis. Sie laufen nicht im Rechenwerk: sie haben kein Ziel, das jemand anderes brauchen koennte, und nichts haengt von ihnen ab.
- `querschnittsanalysen: Dict[str, Any] = field(default_factory=dict)` – Die gezeichneten Querschnitte, nach Kennung -- Bauteile wie die Platten.
- `qa_biegung: Dict[str, SchiefeBiegung] = field(default_factory=dict)` – Biegung und Normalkraft je Querschnittsanalyse, nach ihrer Kennung.
- `qa_schub: Dict[str, Schubwandnachweis] = field(default_factory=dict)` – Querkraft und Torsion je Querschnittsanalyse.
- `qa_duktilitaet: Dict[str, DuktilitaetQA] = field(default_factory=dict)`
- `qa_sproede: Dict[str, SproedesVersagenQA] = field(default_factory=dict)`
- `qa_rissnormalkraft: Dict[str, RissnormalkraftQA] = field(default_factory=dict)`
- `qa_zwaengung_biegung: Dict[str, ZwaengungBiegungQA] = field(default_factory=dict)`
- `qa_spannung_riss: Dict[str, SpannungsbegrenzungQA] = field(default_factory=dict)`
- `qa_spannung: Dict[str, SpannungsbegrenzungQA] = field(default_factory=dict)` – Die Gebrauchsnachweise je Querschnittsanalyse, wie bei der Platte.
- `qa_knicken: Dict[str, KnickenQA] = field(default_factory=dict)` – Knicken je Querschnittsanalyse -- je Fall in seiner Richtung.
- `balkensysteme: Dict[str, Balkensystem] = field(default_factory=dict)` – Die Balkensysteme, nach Kennung -- Bauteile ohne Nachweise, mit ihrem Ergebnis.
- `grundbrueche: Dict[str, Fundament] = field(default_factory=dict)` – Die Fundamente der Grundbruchnachweise, nach Kennung.
- `grundbruch: Dict[str, Grundbruch] = field(default_factory=dict)`
- `gleiten: Dict[str, Gleiten] = field(default_factory=dict)` – Grundbruch und Gleiten je Fundament.
- `warnungen: List[str] = field(default_factory=list)`
- `NACHWEISFELDER = ('nachweise', 'querkraft', 'duktilitaet', 'fehlende', 'rissnormalkraf…` – Die Felder, in denen die Nachweise stehen -- die eine Stelle, an der ein neuer Nachweis eingetragen wird. Alle sind nach Kennung geschluesselt (`q1` oder `q1.x`) und alle tragen Nachweise mit `d_ausnutzung`. Ihre Reihenfolge ist die der Herleitung: in ihr rechnet ein Bauteil seine Nachweise ([[opencivil.projekt.aufbau#Bauteil.ziele|Bauteil.ziele]]).

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
stille Urteile nicht ([[opencivil.projekt.aufbau#Aufbau|bewehrungssuche.bewerte]]). Ein ganz
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

Die Rechenziele eines einzelnen Bauteils -- siehe [[opencivil.projekt.aufbau#Bauteil.ziele|Bauteil.ziele]].

#### Aufbau.ziele_je_bauteil

```python
def ziele_je_bauteil(self) -> List[Tuple[str, List[str]]]
```

Die Rechenziele Bauteil fuer Bauteil, in der Reihenfolge von
[[opencivil.projekt.aufbau#Aufbau.bauteile|bauteile]].

Die Oberflaeche geht darueber, um je Bauteil zwischenzuspeichern
([[opencivil.web.dienst#_stromabwaerts|opencivil.web.dienst._stromabwaerts]]); [[opencivil.projekt.aufbau#Aufbau.alle_ziele|alle_ziele]]
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
- `nachweise: List[Tuple[str, Nachweis]] = field(default_factory=list)` – Feld im [[opencivil.projekt.aufbau#Aufbau|Aufbau]] und Nachweis, angemeldet ueber [[opencivil.projekt.aufbau#Aufbau.eintragen|Aufbau.eintragen]].
- `weitere_ziele: List[str] = field(default_factory=list)` – Was es ausser seinen Nachweisen rechnet -- ein Balkensystem seine Querschnitte und sich.
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

Seine Nachweise in einem Feld des [[opencivil.projekt.aufbau#Aufbau|Aufbau]], in der Folge der Anmeldung.

#### Bauteil.ziele

```python
def ziele(self) -> List[str]
```

Was ein Lauf fuer dieses Bauteil rechnet: die Nachweise in der Folge
von [[opencivil.projekt.aufbau#Aufbau|Aufbau.NACHWEISFELDER]], dann die weiteren Ziele.

### aufbauen

```python
def aufbauen(projekt: 'Projekt', *, schnell: bool=False) -> Aufbau
```

Baut aus der Beschreibung ein vollstaendiges Rechenwerk.

Wirft [[opencivil.projekt.lesen#ProjektFehler|ProjektFehler]], wenn die Beschreibung nicht stimmig ist --
etwa wenn ein Querschnitt auf ein geloeschtes Material verweist.

Mit `schnell` lassen Nachweise teure Nebenrechnungen weg, die das
Urteil nicht aendern -- die Suche nach der Knickgrenzkraft und die
genaue Resistenzlinie --, und ganz stille Nachweise entstehen gar
nicht erst. Gedacht fuer das Bewehrungswerkzeug, das hundertfach
rechnet und nur wissen muss, ob es aufgeht. Fuer eine Herleitung ist
das nichts: dort soll die Zahl stehen, die auch in der Tabelle steht.

### _platte

```python
def _platte(art: 'Bauteilart', eintrag: QuerschnittEintrag, aufbau: Aufbau) -> Bauteil
```

Eine Platte: der Querschnitt und alle Nachweise, die an ihm haengen.

Nachgewiesen wird nur die Tragrichtung x. Die y-Lagen stehen im
Querschnitt -- sie tragen zum Bewehrungsgehalt bei und druecken die
statische Hoehe von x nach innen --, aber kein Nachweis fragt nach ihnen.
Vorher lief hier alles doppelt, einmal je Richtung, und die Haelfte der
Tabelle handelte von einer Richtung, fuer die niemand Schnittgroessen
hatte.

### _querschnittsanalyse

```python
def _querschnittsanalyse(art: 'Bauteilart', eintrag: QuerschnittsanalyseEintrag, aufbau: Aufbau) -> Bauteil
```

Ein gezeichneter Querschnitt: das Bauteil und seine Nachweise.

Biegung und Normalkraft immer -- ihre Eckwerte gehoeren dem Querschnitt.
Querkraft und Torsion, sobald ein Lastfall sie hat oder die
Laengszugkraft zaehlt. Duktilitaet, sproedes Versagen und die Zwaengungen
immer, still, wenn ausgeschaltet -- wie bei der Platte. Ebenso die
Stahlspannungen, sobald es Lastfaelle gibt ([[opencivil.projekt.aufbau#_qa_spannungsnachweise|_qa_spannungsnachweise]]),
und das Knicken, sobald ein Fall eingeschaltet ist.

### _balkensystem

```python
def _balkensystem(art: 'Bauteilart', eintrag: BalkensystemEintrag, aufbau: Aufbau) -> Bauteil
```

Ein Balkensystem: das Stabwerk der Beschreibung, seine Querschnitte
aufgeloest. Hart scheitert nur ein Verweis, den es nicht gibt -- ein
Material, eine Platte, eine Querschnittsanalyse --; was dem System selbst
fehlt, steht in seinen Meldungen, und der Rest des Projekts rechnet.

### _stabquerschnitt

```python
def _stabquerschnitt(q: StabquerschnittEintrag, aufbau: Aufbau, wo: str) -> Stabquerschnitt
```

Woher A und I eines Querschnitts kommen -- die Platte oder Analyse dazu muss es geben.

### _analyse

```python
def _analyse(eintrag: QuerschnittsanalyseEintrag, baustoffe: Mapping[str, Baustoff], *, praefix: str) -> Querschnittsanalyse
```

Aus der Beschreibung das Bauteil -- und aus jedem Fehler der Zeichnung
einen Satz, der die Analyse nennt.

### _lagennachweise

```python
def _lagennachweise(eintrag: QuerschnittEintrag, querschnitt: Plattenquerschnitt, richtung: Richtung, nachweis: BiegungNormalkraft, aufbau: Aufbau, teil: Bauteil) -> None
```

Die Nachweise je x-Lage: sproedes Versagen, Zwaengung auf Biegung und
auf Normalkraft, Duktilitaet.

Die beiden x-Lagen, von unten nach oben. Beide werden gerechnet; in die
Zusammenfassung kommt die unguenstigere. Ausgeschaltet heisst still --
gerechnet wird trotzdem, damit ein Hinweis stehen kann.

### _spannungsnachweise

```python
def _spannungsnachweise(eintrag: QuerschnittEintrag, querschnitt: Plattenquerschnitt, richtung: Richtung, aufbau: Aufbau, teil: Bauteil) -> None
```

Die Stahlspannung, zweimal: aus der Rissbreite unter quasi-staendiger
Einwirkung (bei jeder Anforderung) und gegen Fliessen unter haeufiger
(nur bei erhoehter und hoher). Welche wann gilt, weiss die Grenze selbst.

### _qa_spannungsnachweise

```python
def _qa_spannungsnachweise(eintrag: QuerschnittsanalyseEintrag, analyse: Querschnittsanalyse, aufbau: Aufbau, teil: Bauteil) -> None
```

Die Stahlspannungen des gezeichneten Querschnitts -- wie bei der Platte, je Grenze.

### _knickfall

```python
def _knickfall(k: KnickEintrag, klasse: type=Knickfall, **mehr: Any) -> Knickfall
```

Ein Knickfall aus seiner Beschreibung -- kN, kNm und m; `mehr` fuer die Analyse.

### _verformungsfall

```python
def _verformungsfall(f: VerformungsfallEintrag) -> Verformungsfall
```

Ein Verformungsfall aus seiner Beschreibung -- w in mm, die Spannweite in m.

### _stoff

```python
def _stoff(baustoffe: Mapping[str, Baustoff], kennung: str, art: str, wer: str) -> Baustoff
```

Das Material, auf das ein Eintrag zeigt: es muss es geben, und es muss
von dieser Art sein. Ohne Angabe gilt nicht «das erste im Projekt» -- bis
2026-10-16 bekamen Buegel und Staebe ohne Stahl still den ersten.

### _gebrauchsfaelle

```python
def _gebrauchsfaelle(kombinationen: Sequence[Any], liste: Gebrauchsliste, fall: Callable[[str, Any, float], Any]) -> Tuple[List[Any], List[str]]
```

Die Lastfaelle eines Stahlspannungsnachweises -- und welche laut sind.

Einmal fuer die haeufigen, einmal fuer die quasi-staendigen; beide
Listen werden gleich gebildet und unterscheiden sich nur im Anteil.
`fall(name, eintrag, faktor)` macht aus einem Eintrag -- einer
Kombination der Tragsicherheit oder einem eigenen Fall -- den Fall des
Nachweises: bei der Platte einen [[opencivil.nachweis.spannungsbegrenzung#Gebrauchsfall|Gebrauchsfall]], beim
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

### _ausgefallene

```python
def _ausgefallene(kombinationen: Sequence[KombinationEintrag], richtung: Richtung) -> List[Ausgefallen]
```

Welche Nachweise in dieser unbewehrten Richtung ausfallen.

Je Kombination der M-N-Nachweis, und wo eine Querkraft angegeben ist,
auch der Querkraftnachweis: ohne Bewehrung gibt es keine statische
Hoehe, also auch keinen Querkraftwiderstand. Beide Zeilen gehoeren in
die Tabelle -- eine davon wegzulassen hiesse, die Luecke nur zur
Haelfte zu schliessen.

### _kombination

```python
def _kombination(eintrag: KombinationEintrag) -> Schnittgroessen
```

Eine Einwirkung -- welche Massstaebe es gibt, prueft ihr Feld.

### _grundbruch

```python
def _grundbruch(art: 'Bauteilart', eintrag: GrundbruchEintrag, aufbau: Aufbau) -> Bauteil
```

Ein Fundament und seine beiden Nachweise -- Grundbruch und Gleiten --,
sobald eine Kombination eingeschaltet ist. Ohne sie steht das Fundament
allein da, wie eine Platte ohne Einwirkung.

### _ueberschreibungen_setzen

```python
def _ueberschreibungen_setzen(projekt: 'Projekt', werk: Rechenwerk, aufbau: Aufbau) -> None
```

Die von Hand ueberschriebenen Kennwerte -- dass es sie gibt, prueft `_baustoff`.

### Bauteilart

```python
@dataclass(frozen=True)
class Bauteilart
```

Der Steckbrief einer Bauteilart: was ausserhalb ihres Eintrags und ihrer
Baufunktion von ihr bekannt sein muss. Eine neue Art kommt in
[[opencivil.projekt.aufbau#Konstanten|BAUTEILE]] dazu und nirgends sonst.

- `name: str` – Wie sie im Aufbau, im Bericht und in der Oberflaeche heisst: `platte`.
- `liste: str` – Ihre Liste im [[opencivil.projekt.projekt#Projekt|Projekt]] und in der Datei: `querschnitte`.
- `eintrag: type` – Die Klasse ihrer Eintraege -- sie liest einen Eintrag aus der Datei.
- `vorsilbe: str` – Womit ihre Kennungen beginnen: `q` fuer q1, q2 ...
- `raum: str` – Womit ihre Namensraeume beginnen: `querschnitt` fuer querschnitt.q1.
- `bereich: str` – Wie ihr Abschnitt in der Formelsammlung heisst.
- `bauen: Callable[['Bauteilart', Any, Aufbau], Bauteil]` – Aus dem Eintrag das Bauteil -- Objekt und Nachweise, angemeldet im Werk.


## Konstanten

- `PLATTE = Bauteilart('platte', 'querschnitte', QuerschnittEintrag, 'q', 'quersc…`
- `ANALYSE = Bauteilart('querschnittsanalyse', 'querschnittsanalysen', Querschnitt…`
- `BALKENSYSTEM = Bauteilart('balkensystem', 'balkensysteme', BalkensystemEintrag, 'r',…`
- `GRUNDBRUCH = Bauteilart('grundbruch', 'grundbrueche', GrundbruchEintrag, 'g', 'gru…`
- `BAUTEILE = (PLATTE, ANALYSE, BALKENSYSTEM, GRUNDBRUCH)` – Die Bauteilarten, in der Reihenfolge von Baum, Bericht und Rechnung -- ein Balkensystem liest Werte der Platten und Analysen, also kommt es nach ihnen; ein Grundbruch liest nichts von den anderen. Wer alle Bauteile durchgeht (Lesen, Kennungen, Aufbau, Zwischenspeicher, Erkennen einer Datei), geht diese Liste durch.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.geotechnik.grundbruch]]
- [[opencivil.material.basis]]
- [[opencivil.material.beton]]
- [[opencivil.material.betonstahl]]
- [[opencivil.nachweis.biegung_normalkraft]]
- [[opencivil.nachweis.dehnungsfaecher]]
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
- [[opencivil.nachweis.sproedes_versagen]]
- [[opencivil.nachweis.verformung]]
- [[opencivil.projekt.balkensystem]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.grundbruch]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.platte]]
- [[opencivil.projekt.projekt]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.geometrie]]
- [[opencivil.querschnitt.platte]]
- [[opencivil.querschnitt.schnittanalyse]]
- [[opencivil.stabwerk.rechnung]]

## Gebraucht von

- [[opencivil.notizbuch.formelseiten]]
- [[opencivil.projekt]]
- [[opencivil.projekt.projekt]]
