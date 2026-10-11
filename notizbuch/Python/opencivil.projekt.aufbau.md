---
erzeugt: 30c671794c82
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/aufbau.py
> aus der Beschreibung ein Rechenwerk.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/aufbau.py)

## VERANTWORTUNG

[[opencivil.projekt.aufbau#aufbauen|aufbauen]] macht aus einem [[opencivil.projekt.projekt#Projekt|Projekt]] Baustoffe, Querschnitte und
Nachweise und meldet sie in einem [[opencivil.core.rechenwerk#Rechenwerk|Rechenwerk]] an. Heraus kommt ein
[[opencivil.projekt.aufbau#Aufbau|Aufbau]] -- das Werk samt allen Nachweisobjekten, nach Platte und Art
abgelegt, damit Schnittstelle, Zwischenspeicher und Bewehrungssuche sie
wiederfinden.

Die Beschreibung selbst rechnet nichts; hier wird sie zum ersten Mal
Rechnung. Darum stehen auch die Pruefungen hier, die erst beim Bauen
auffallen koennen -- ein Verweis auf ein geloeschtes Material, eine Platte
ohne Bewehrung.

## Inhalt

### Aufbau

```python
@dataclass
class Aufbau
```

Was beim Zusammenbauen eines Projekts entsteht.

- `werk: Rechenwerk`
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
- `knicken: Dict[str, Knicken] = field(default_factory=dict)` – Nachweis am verformten System, je Querschnitt -- nur in x-Richtung.
- `fehlende: Dict[str, FehlendeBewehrung] = field(default_factory=dict)` – Je Richtung ohne Bewehrung, fuer die dennoch Einwirkungen angegeben sind. Sie rechnen nichts; sie sorgen dafuer, dass in der Zusammenfassung eine Zeile mit Erfuellungsgrad null steht statt gar nichts.
- `spannungsfaelle: Dict[str, List['SpannungsfallEintrag']] = field(default_factory=dict)` – Je Platte die Auswertungen am Querschnitt -- als Beschreibung, nicht als Nachweis. Sie laufen nicht im Rechenwerk: sie haben kein Ziel, das jemand anderes brauchen koennte, und nichts haengt von ihnen ab.
- `blaetter: Dict[str, Gleichungsblatt] = field(default_factory=dict)` – Die Blätter analytischer Gleichungen, nach Kennung.
- `querschnittsanalysen: Dict[str, Any] = field(default_factory=dict)` – Die gezeichneten Querschnitte, nach Kennung -- Bauteile wie die Platten.
- `qa_biegung: Dict[str, SchiefeBiegung] = field(default_factory=dict)` – Biegung und Normalkraft je Querschnittsanalyse, nach ihrer Kennung.
- `qa_schub: Dict[str, Schubwandnachweis] = field(default_factory=dict)` – Querkraft und Torsion je Querschnittsanalyse.
- `qa_duktilitaet: Dict[str, DuktilitaetQA] = field(default_factory=dict)`
- `qa_sproede: Dict[str, SproedesVersagenQA] = field(default_factory=dict)`
- `warnungen: List[str] = field(default_factory=list)`
- `NACHWEISFELDER = ('nachweise', 'querkraft', 'duktilitaet', 'fehlende', 'rissnormalkraf…` – Die Felder, in denen die Nachweise einer Platte stehen -- die eine Stelle, an der ein neuer Nachweis eingetragen wird. Alle sind nach Kennung geschluesselt (`q1` oder `q1.x`) und alle tragen Nachweise mit `d_ausnutzung`. Daraus ergeben sich Rechenziele, Aufteilen nach Platte und Zwischenspeichern von selbst; frueher stand dieselbe Liste viermal da, und wer einen Nachweis hinzufuegte, musste alle vier finden.

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

#### Aufbau.gehoert_zu

```python
def gehoert_zu(self, schluessel: str, kennung: str) -> bool
```

Ob ein Feldschluessel (`q1` oder `q1.x`) zu dieser Platte gehoert.

#### Aufbau.teile_von

```python
def teile_von(self, kennung: str) -> Dict[str, Dict[str, Any]]
```

Alle Nachweisobjekte einer Platte, nach Feld geordnet.

Gebraucht vom Zwischenspeicher: ein uebernommenes Ergebnis besteht
nicht nur aus Zahlen, sondern auch aus dem, was die Nachweise sich
beim Rechnen gemerkt haben -- Interaktionslinien, Fallergebnisse,
Iterationsschritte. Die Schnittstelle liest das aus den Objekten, also
muessen die Objekte mitwandern und nicht bloss ihre Ausgabewerte.

#### Aufbau.teile_setzen

```python
def teile_setzen(self, kennung: str, teile: Mapping[str, Dict[str, Any]]) -> None
```

Die Nachweisobjekte einer Platte durch frueher gerechnete ersetzen.

#### Aufbau.ziele_von

```python
def ziele_von(self, kennung: str) -> List[str]
```

Die Rechenziele einer einzelnen Platte -- Eckwerte und Nachweise.

#### Aufbau.eckwertziele

```python
def eckwertziele(self) -> List[str]
```

Was ein Bauteil auch ohne Lastfall rechnet: die Eckwerte seines
M-N-Nachweises. Eine Analyse ohne Lastfall zeigt so trotzdem ihren
Querschnitt und ihre reine Normalkraft.

#### Aufbau.bauteile

```python
def bauteile(self) -> List['Bauteilkopf']
```

Jedes Bauteil, in der Reihenfolge der Beschreibung: erst die Platten,
dann die Querschnittsanalysen.

Die eine Stelle, die diese Reihenfolge festlegt -- fuer die Rechenziele,
den Zwischenspeicher und die Zusammenfassung.

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

#### Aufbau.blattziele

```python
def blattziele(self) -> List[str]
```

Die Blätter zuletzt -- sie lesen Werte der Platten, nie umgekehrt.

#### Aufbau.berichtsziele

```python
def berichtsziele(self) -> List[str]
```

Was im Bericht steht: Nachweise, Eckwerte, Blätter -- ohne die
Baustoffkennwerte, die niemand braucht.

#### Aufbau.urteile_von

```python
def urteile_von(self, kennung: str, urteile: Iterable[NachweisUrteil]) -> List[NachweisUrteil]
```

Die Urteile einer Platte -- erkannt am Namensraum ihres Nachweises.

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

### Bauteilkopf

```python
@dataclass(frozen=True)
class Bauteilkopf
```

Was man von einem Bauteil wissen muss, um seine Teile zu finden.

- `kennung: str`
- `name: str`
- `raum: str` – Der Namensraum seiner Werte und Urteile.
- `art: str` – `platte` oder `querschnittsanalyse`.

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
def _platte(eintrag: QuerschnittEintrag, aufbau: Aufbau, eintragen: Eintragen, *, schnell: bool) -> None
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
def _querschnittsanalyse(eintrag: QuerschnittsanalyseEintrag, aufbau: Aufbau, eintragen: Eintragen) -> None
```

Ein gezeichneter Querschnitt: das Bauteil und seine Nachweise.

Biegung und Normalkraft immer -- ihre Eckwerte gehoeren dem Querschnitt.
Querkraft und Torsion, sobald ein Lastfall sie hat oder die
Laengszugkraft zaehlt. Duktilitaet und sproedes Versagen immer, still,
wenn ausgeschaltet -- wie bei der Platte.

### _analyse

```python
def _analyse(eintrag: QuerschnittsanalyseEintrag, baustoffe: Mapping[str, Baustoff]) -> Querschnittsanalyse
```

Aus der Beschreibung das Bauteil -- und aus jedem Fehler der Zeichnung
einen Satz, der die Analyse nennt.

### _lagennachweise

```python
def _lagennachweise(eintrag: QuerschnittEintrag, querschnitt: Plattenquerschnitt, richtung: Richtung, nachweis: BiegungNormalkraft, eintragen: Eintragen) -> None
```

Die Nachweise je x-Lage: sproedes Versagen, Zwaengung auf Biegung und
auf Normalkraft, Duktilitaet.

Die beiden x-Lagen, von unten nach oben. Beide werden gerechnet; in die
Zusammenfassung kommt die unguenstigere. Ausgeschaltet heisst still --
gerechnet wird trotzdem, damit ein Hinweis stehen kann.

### _spannungsnachweise

```python
def _spannungsnachweise(eintrag: QuerschnittEintrag, querschnitt: Plattenquerschnitt, richtung: Richtung, eintragen: Eintragen) -> None
```

Die Stahlspannung, zweimal: aus der Rissbreite unter quasi-staendiger
Einwirkung (bei jeder Anforderung) und gegen Fliessen unter haeufiger
(nur bei erhoehter und hoher). Welche wann gilt, weiss die Grenze selbst.

### _gebrauchsfaelle

```python
def _gebrauchsfaelle(kombinationen: Sequence[KombinationEintrag], liste: Gebrauchsliste) -> Tuple[List[Gebrauchsfall], List[str]]
```

Die Lastfaelle eines Stahlspannungsnachweises -- und welche laut sind.

Einmal fuer die haeufigen, einmal fuer die quasi-staendigen; beide
Listen werden gleich gebildet und unterscheiden sich nur im Anteil.

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


## Konstanten

- `Eintragen = Callable[[str, str, Nachweis], None]` – Wie ein fertig gebauter Nachweis angemeldet wird: Feld im [[opencivil.projekt.aufbau#Aufbau|Aufbau]], Schluessel darin, Nachweis.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.gleichungen.blatt]]
- [[opencivil.material.basis]]
- [[opencivil.material.beton]]
- [[opencivil.material.betonstahl]]
- [[opencivil.nachweis.biegung_normalkraft]]
- [[opencivil.nachweis.dehnungsfaecher]]
- [[opencivil.nachweis.duktilitaet]]
- [[opencivil.nachweis.fehlende_bewehrung]]
- [[opencivil.nachweis.knicken]]
- [[opencivil.nachweis.mindestbewehrung]]
- [[opencivil.nachweis.querkraft]]
- [[opencivil.nachweis.richtungsnachweise]]
- [[opencivil.nachweis.schiefe_biegung]]
- [[opencivil.nachweis.schubwandnachweis]]
- [[opencivil.nachweis.spannungsbegrenzung]]
- [[opencivil.nachweis.sproedes_versagen]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.platte]]
- [[opencivil.projekt.projekt]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.geometrie]]
- [[opencivil.querschnitt.platte]]

## Gebraucht von

- [[opencivil.projekt]]
- [[opencivil.projekt.projekt]]
