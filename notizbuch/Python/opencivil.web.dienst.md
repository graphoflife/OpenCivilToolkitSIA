---
erzeugt: a7f406f3d45f
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/dienst.py
> Der Rechendienst, unabhaengig vom Transportweg.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/dienst.py)

## VERANTWORTUNG

Nimmt eine Anfrage als gewoehnliches `dict` entgegen und gibt die Antwort als
`dict` zurueck. Von HTTP weiss dieser Baustein nichts, vom Dateisystem auch
nichts, und einen Unterprozess startet er nie.


## WARUM DAS WICHTIG IST

Die Oberflaeche laeuft auf zwei Wegen -- auf dem Rechner ueber
[[opencivil.web.server]] mit CPython, im Browser ueber `web/js/kern.js` mit
Pyodide. Beide Wege sind bloss duenne Huellen um genau dieses Modul. Damit ist
baulich ausgeschlossen, dass im Browser etwas *nachgebaut* wird: es gibt nur
eine einzige Rechenimplementierung, und die ist Python.

Was eine Huelle beisteuern darf, ist alles, was ihre Umgebung eigen hat -- der
Server etwa die Uebersetzung des Berichts zu PDF, der Browser das Ablegen des
Projekts im Speicher des Browsers. Gerechnet wird in beiden Faellen hier.


## EIGENSTAENDIG NUTZBAR


```python
from opencivil.web.dienst import bearbeite
antwort = bearbeite("rechnen", {"projekt": {...}})
print(antwort.status, antwort.daten["werte"])
```

## Inhalt

### DienstFehler

```python
class DienstFehler(Exception)
```

Fehler mit vorgegebenem Status, etwa fuer eine unbekannte Anfrage.

### Antwort

```python
@dataclass(frozen=True)
class Antwort
```

Was der Dienst zurueckgibt: Nutzlast plus Status nach HTTP-Art.

- `daten: Dict[str, Any] = field(default_factory=dict)`
- `status: int = 200`

#### Antwort.ist_fehler

```python
@property
def ist_fehler(self) -> bool
```

### _projekt

```python
def _projekt(rumpf: Mapping[str, Any]) -> Projekt
```

Baut das Projekt aus dem Anfragerumpf.

### katalog

```python
def katalog(rumpf: Mapping[str, Any]) -> Dict[str, Any]
```

Normsorten, Kennwertvorlagen und Einheiten -- alles, was fest steht.

### beispiel

```python
def beispiel(rumpf: Mapping[str, Any]) -> Dict[str, Any]
```

Das Beispielprojekt, mit dem eine leere Oberflaeche startet.

### pruefen

```python
def pruefen(rumpf: Mapping[str, Any]) -> Dict[str, Any]
```

Prueft eine Projektbeschreibung und gibt sie aufgeraeumt zurueck.

Dafuer gedacht, dass eine hochgeladene oder im Browser abgelegte Datei durch
denselben Aufbau laeuft wie alles andere: fehlt ein Feld oder stammt die
Datei aus einer aelteren Fassung, greifen hier die Wandlung des alten
Formats und die Pruefungen aus [[opencivil.projekt]] -- nicht eine
zweite, nachgebaute Pruefung in JavaScript.

Die Vorpruefung auf [[opencivil.web.dienst#Konstanten|KENNFELDER]] ist noetig, weil
`Projekt.aus_dict` mit Absicht nachsichtig ist: es nimmt jedes `dict`
und macht daraus notfalls ein leeres Projekt. Beim Laden einer Beschreibung
ist das richtig -- beim Oeffnen einer Datei waere es verheerend. Wer eine
beliebige JSON-Datei erwischt, bekaeme sonst wortlos ein leeres Projekt
und haette seine Arbeit verloren.

### rechnen

```python
def rechnen(rumpf: Mapping[str, Any]) -> Dict[str, Any]
```

Rechnet ein Projekt durch.

Ohne `ziele` wird alles gerechnet, was die Nachweise brauchen. Mit
`ziele` genau diese -- dann loest das Rechenwerk rueckwaerts auf und
meldet, welche Eingabe fehlt.

### _stromabwaerts

```python
def _stromabwaerts(projekt: Projekt, aufbau) -> Loesung
```

Alles rechnen -- aber nur, was sich geaendert hat.

Zuerst die Baustoffe: sie stehen am Anfang jeder Herleitung und jede
Platte braucht sie. Dann Platte fuer Platte, jede in einem eigenen Lauf,
der die schon bekannten Werte mitbekommt und sie darum weder erneut
rechnet noch erneut herleitet. Eine Platte, deren Abdruck seit dem letzten
Mal derselbe ist, wird gar nicht erst angefasst; ihr Beitrag kommt
fertig aus dem Speicher.

Die Reihenfolge ist dieselbe wie vorher -- erst die Baustoffe, dann die
Bauteile in der Reihenfolge der Beschreibung --, und daran haengt der
Aufbau des Protokolls. Ein Zwischenspeicher, der die Reihenfolge
verschoebe, aenderte den Bericht, und das waere keine Beschleunigung mehr,
sondern eine andere Ausgabe.

### querkraftkurven

```python
def querkraftkurven(rumpf: Mapping[str, Any]) -> Dict[str, Any]
```

Die M-V-Kurven fuer selbst gewaehlte Normalkraefte.

Der Querkraftwiderstand haengt ueber `m_Rd(N_Ed)` von der Normalkraft ab.
Unter jedem Diagramm laesst sich eine einstellen; `n_ed` bildet die
Kennung der Kurve auf diese Normalkraft in kN ab.

Eine eigene Anfrage, weil es eine eigene Frage ist -- und weil die
Oberflaeche die Formel sonst ein zweites Mal enthalten muesste, um die
Kurve selbst zu zeichnen. Gerechnet wird an genau einer Stelle.

### bericht

```python
def bericht(rumpf: Mapping[str, Any]) -> Dict[str, Any]
```

Baut den Bericht als LaTeX-Dokument und als Markdown, beide als
Zeichenkette.

Geschrieben wird hier nichts. Der Browser macht daraus einen Download, der
Server legt es zusaetzlich in `ausgabe/` ab und versucht die Uebersetzung
zu PDF -- das `.tex` ist auf beiden Wegen dasselbe.

### dateiname

```python
def dateiname(name: str) -> str
```

Macht aus einem Projektnamen einen brauchbaren Dateinamen.

### bewehrung_suchen

```python
def bewehrung_suchen(rumpf: Mapping[str, Any]) -> Dict[str, Any]
```

Sucht zu einer Platte die kleinste Bewehrung und gibt sie zurueck -- mit
«Plattendicke optimieren» auch die duennste Platte dazu.

Gerechnet, nicht gesetzt: zurueck kommt das gefundene Projekt, und ob die
Oberflaeche es uebernimmt, entscheidet sie. So bleibt der Knopf ein
einzelner Schritt, den man sieht und rueckgaengig machen kann -- und
nicht eine Bewehrung, die sich bei jeder Eingabe im Hintergrund aendert.

Wie gesucht wird, steht an der Platte und nur dort. Frueher liess sich
jede Einstellung mit dem Rumpf uebersteuern, per ``rumpf.get(...) or
eintrag...` -- und das `or`` las eine Null als «nicht angegeben»: ein
Mindestdurchmesser 0, also «kein Minimum», wurde still zur Vorgabe der
Platte. Zwei Quellen fuer dieselbe Zahl, und die Oberflaeche benutzte die
zweite ohnehin nie.

### geometrie

```python
def geometrie(rumpf: Mapping[str, Any]) -> Dict[str, Any]
```

Was das Zeichenfenster einer Querschnittsanalyse zeigt -- ohne Nachweise.

Stablagen und tatsaechliche Teilungen, Schwerpunkt, Zellen der
Schubwaende und jede Meldung zur Zeichnung, am Element, das sie betrifft.
Schnell genug fuer jede Aenderung: gerechnet wird nur Geometrie.

### analysediagramme

```python
def analysediagramme(rumpf: Mapping[str, Any]) -> Dict[str, Any]
```

Die Diagramme einer Querschnittsanalyse -- erst, wenn jemand sie sehen will.

Die M_y-M_z-Kurven brauchen je Lastfall siebzig Bruchzustaende, die kein
Nachweis braucht. Mit jeder Rechnung mitgeliefert, machten sie jede
Eingabe langsamer, auch bei geschlossenem Reiter. Darum eine eigene
Anfrage, wie die M-V-Kurven.

Die Nachweise selbst rechnen nicht noch einmal, wenn der Zwischenspeicher
sie zu genau dieser Beschreibung noch hat -- nach einer Rechnung ist das
der Fall. Sonst wird das eine Bauteil gerechnet.

### _vorlagenwahl

```python
def _vorlagenwahl(rumpf: Mapping[str, Any]) -> Dict[str, Any]
```

Was die Oberflaeche zu einer Vorlage eingestellt hat -- Masse, Achsabstand, die zwei Haken.

### vorlage

```python
def vorlage(rumpf: Mapping[str, Any]) -> Dict[str, Any]
```

Die Teile einer Vorlage zu den eingestellten Massen -- fuer die Skizze,
waehrend man tippt. Passen die Masse nicht zueinander, steht der Grund in
`fehler` und es gibt keine Teile: das ist keine falsche Anfrage, nur
eine unfertige Eingabe.

### vorlage_einsetzen

```python
def vorlage_einsetzen(rumpf: Mapping[str, Any]) -> Dict[str, Any]
```

Setzt eine Vorlage in eine Querschnittsanalyse ein, mit dem Baukasten
des Kerns ([[opencivil.projekt.querschnittsanalyse#QuerschnittsanalyseEintrag.vorlage_einsetzen|QuerschnittsanalyseEintrag.vorlage_einsetzen]]). Zurueck
kommen ihre Elementlisten und die Kennungen der neuen Elemente -- die
Oberflaeche uebernimmt sie in einem Schritt, den man rueckgaengig machen
kann.

### bearbeite

```python
def bearbeite(name: str, rumpf: Mapping[str, Any] | None=None) -> Antwort
```

Fuehrt eine Anfrage aus. Wirft nicht -- Fehler kommen als Antwort zurueck.

Dass auch der Fehlerfall eine gewoehnliche Antwort ist, haelt die beiden
Huellen duenn: keine muss sich ueberlegen, welche Ausnahme welchen Status
verdient.

### nach_json

```python
def nach_json(daten: Any) -> str
```

Wandelt eine Antwort in JSON.

`allow_nan=False` ist Absicht: `json.dumps` schriebe sonst `Infinity`
und `NaN`. Python liest das wieder, `JSON.parse` im Browser lehnt es ab
-- die Antwort kaeme heil an und waere trotzdem unbrauchbar. Lieber hier
laut scheitern als dort stumm. [[opencivil.web.api#endlich|endlich]] raeumt die Faelle vorher weg,
sodass der Riegel nur zuschlaegt, wenn wirklich etwas Neues auftaucht.

### bearbeite_json

```python
def bearbeite_json(name: str, rumpf_json: str='{}') -> str
```

Dasselbe wie [[opencivil.web.dienst#bearbeite|bearbeite]], aber mit JSON hinein und heraus.

Der Weg fuer den Browser. Dass hier dieselbe Wandlung nach JSON laeuft wie
im Server, ist kein Zufall: so trifft die Oberflaeche auf beiden Wegen
genau dieselben Daten, bis aufs Zeichen.

Zurueck kommt ein Umschlag `{"status": …, "daten": …}`; der Status
entspricht dem, was der Server ueber HTTP melden wuerde.


## Konstanten

- `SPEICHER = speicher.Ergebnisspeicher()` – Das Gedaechtnis zwischen zwei Anfragen -- siehe [[opencivil.web.speicher]]. Im Modul und damit im Prozess: beim Server die laufende Sitzung, im Browser der offene Reiter.
- `KENNFELDER = ('name', 'materialien', *BAUTEILE)` – Woran eine Projektdatei zu erkennen ist. Mindestens eines davon muss da sein.
- `ANFRAGEN = {'katalog': katalog, 'beispiel': beispiel, 'pruefen': pruefen, 'rechn…` – Name der Anfrage -> Funktion. Diese Namen sind der ganze Vertrag zwischen Oberflaeche und Kern; beide Huellen reichen sie unveraendert durch.

## Braucht

- [[opencivil.bericht.latex_dokument]]
- [[opencivil.bericht.markdown]]
- [[opencivil.bewehrungssuche]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.projekt]]
- [[opencivil.querschnitt.interaktion]]
- [[opencivil.querschnitt.vorlagen]]
- [[opencivil.web.api]]
- [[opencivil.web.diagrammdaten]]
- [[opencivil.web.speicher]]

## Gebraucht von

- [[opencivil.web.server]]
