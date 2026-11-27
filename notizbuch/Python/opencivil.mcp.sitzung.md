---
erzeugt: a862b1436cee
art: modul
tags: [modul]
---
> [!abstract] opencivil/mcp/sitzung.py
> die offene Projektdatei, und wie sie sich aendert.
> Paket [[opencivil.mcp]] · [Quelltext](../../opencivil/mcp/sitzung.py)

## VERANTWORTUNG

Die [[opencivil.mcp.sitzung#Sitzung|Sitzung]] haelt, was die Seite im Browser haelt: die Mappe mit
ihren Projekten ([[opencivil.projekt.mappe#Mappe|Mappe]]), welches gewaehlt
ist, aus welcher Datei sie kam und ob seither etwas ungespeichert ist.
Gerechnet und geoeffnet wird ueber den Rechendienst ([[opencivil.mcp.sitzung#dienst|dienst]]), wie in
der Seite.


## EINE TUER FUER JEDE AENDERUNG

Ein Werkzeug aendert an einer Kopie des Projekts ([[opencivil.mcp.sitzung#Sitzung.aendern|Sitzung.aendern]]).
Gilt sie, ersetzt sie das Projekt; sonst bleibt alles, wie es war, und die
Meldung des Kerns geht unveraendert zurueck. Abgewiesen wird, was der Kern
nicht lesen kann – ein Feld, das es nicht gibt, ein Text statt einer Zahl
–, und was das ganze Projekt anhielte, wo es vorher rechnete: zwei
Materialien mit demselben Namen. Was nur den Eintrag anhaelt – eine Platte
ohne Bewehrung, eine Dicke von null –, gilt; der Rest rechnet weiter
(Benutzer, 2026-11-19), und die Antwort sagt gleich, was fehlt, in den Worten
des Kerns ([[opencivil.mcp.sitzung#Geaendert|Geaendert.hinweise]]).

## Inhalt

### Werkzeugfehler

```python
class Werkzeugfehler(Exception)
```

Was ein Werkzeug nicht tun kann – ein Satz, der so zurueckgeht.

### Fund

```python
class Fund(NamedTuple)
```

Ein Eintrag des gewaehlten Projekts: seine Liste, seine Stelle darin und er selbst.

- `liste: str`
- `stelle: int`
- `eintrag: Any`

### Geaendert

```python
@dataclass
class Geaendert
```

Was eine Aenderung hinterlaesst: den Eintrag und was der Kern zu ihm sagt.

- `eintrag: Any`
- `hinweise: List[str] = field(default_factory=list)` – Die Hinweise des Aufbaus zu ihm, wie der Kern sie schreibt – auch, was ihm fehlt.
- `projektfehler: str = ''` – Warum das Projekt nicht rechnet – nur, wo es das schon vorher nicht tat.

### Sitzung

```python
@dataclass
class Sitzung
```

Die offene Mappe, das gewaehlte Projekt darin, die Datei dazu.

- `mappe: Optional[Mappe] = None`
- `gewaehlt: int = 0`
- `pfad: Optional[Path] = None`
- `ungespeichert: bool = False`

#### Sitzung.oeffnen

```python
def oeffnen(self, pfad: str, *, verwerfen: bool=False) -> None
```

Oeffnet eine Projektdatei wie «Öffnen» der Seite (Dienst
`mappe_oeffnen`): geprueft, mit den Sandboxen, wie gespeichert.

#### Sitzung.neu

```python
def neu(self, *, verwerfen: bool=False) -> None
```

Eine neue Mappe mit einem neuen Projekt, noch ohne Datei.

#### Sitzung.speichern

```python
def speichern(self, pfad: str='', *, ueberschreiben: bool=False) -> Path
```

Schreibt die Mappe, wie «Speichern» der Seite, mit den Sandboxen –
ohne `pfad` in ihre Datei. Eine andere, die es schon gibt, nur mit
`ueberschreiben`.

#### Sitzung.offen

```python
def offen(self) -> Mappe
```

Die offene Mappe – ohne eine sagt der Fehler, wie man zu einer kommt.

#### Sitzung.projekt

```python
@property
def projekt(self) -> Projekt
```

Das gewaehlte Projekt – in ihm arbeitet jedes Werkzeug.

#### Sitzung.waehlen

```python
def waehlen(self, name: str) -> Projekt
```

#### Sitzung.projekt_anlegen

```python
def projekt_anlegen(self, name: str='') -> Projekt
```

Ein neues Projekt hinter den anderen, gleich gewaehlt – wie «+» der Projektreihe.

#### Sitzung.finden

```python
def finden(self, eintrag: str, app: str='') -> Fund
```

Ein Eintrag des gewaehlten Projekts, nach seinem Namen oder seiner
Kennung – mit `app` nur in deren Liste. Heissen mehrere so, etwa
die Sandboxen, sagt der Fehler, welche.

#### Sitzung.aendern

```python
def aendern(self, tun: Callable[[Projekt], Any]) -> Geaendert
```

`tun` aendert eine Kopie des Projekts und gibt den Eintrag zurueck,
den es angelegt oder geaendert hat. Gilt die Kopie (siehe Dateikopf),
ersetzt sie das Projekt; sonst bleibt es, wie es war.

#### Sitzung.ersetzen

```python
def ersetzen(self, eintrag: str, app: str, neu: Callable[[Dict[str, Any]], Any]) -> Geaendert
```

Ersetzt einen Eintrag durch das, was `neu` aus seiner Datei-Form
macht – gelesen vom Leser des Kerns, wie eine Datei. Seine Kennung
bleibt, auf sie zeigen andere; eine Kennung seiner Elemente kommt nie
wieder ([[opencivil.projekt.netz#von_hand|von_hand]]).

### dienst

```python
def dienst(name: str, rumpf: Mapping[str, Any]) -> Dict[str, Any]
```

Eine Anfrage an den Rechendienst, wie die Seite sie stellt
([[opencivil.web.dienst#bearbeite|bearbeite]]). Seine Fehlermeldung wird zum
[[opencivil.mcp.sitzung#Werkzeugfehler|Werkzeugfehler]]; die Spur eines unerwarteten geht nach stderr.

### neues_projekt

```python
def neues_projekt(namen: Iterable[str]) -> Projekt
```

Ein neues Projekt, wie «+» der Projektreihe es anlegt (web/js/projekte.js):
«Projekt 1» oder die naechste freie Nummer, mit dem ersten Beton und
Stahl und mit den Sandboxen.

### liste_von

```python
def liste_von(app: str) -> str
```

Die Liste einer App, gesagt mit ihr selbst («querschnitte») oder dem Namen ihrer Eintraege («Platte»).

### name_von

```python
def name_von(eintrag: Any) -> str
```

Wie ein Eintrag heisst – ein Material ohne eigenen Namen nach seiner Sorte.

### kennung_im_raum

```python
def kennung_im_raum(raum: str) -> str
```

Die Kennung des Eintrags, dem ein Name im Rechenwerk gehoert: «q3» in
«querschnitt.q3.nachweis.mn.x» – wie `inSandbox` in web/js/zustand.js.

### datei_form

```python
def datei_form(eintrag: Any) -> Dict[str, Any]
```

Ein Eintrag, wie er in der Datei steht – als JSON-Daten, eine Wahl als ihr Text.

### unbekannt

```python
def unbekannt(satz: str, name: str, namen: Iterable[str]) -> str
```

`satz`, und wenn es einen gibt, der aehnlichste der `namen` – wie der Leser des Kerns.

### dateipfad

```python
def dateipfad(pfad: str) -> Path
```

Ein Pfad, wie ein Werkzeug ihn bekommt – `~` und Relatives vom Arbeitsverzeichnis aus aufgeloest.

### schreiben

```python
def schreiben(ziel: Path, text: str, *, ueberschreiben: bool=False) -> None
```

Schreibt `text` nach `ziel` – eine Datei, die es schon gibt, nur mit
`ueberschreiben`. Erst ganz daneben, dann an ihren Ort: bricht etwas
ab, bleibt die alte Datei heil.

### _rechnet

```python
def _rechnet(projekt: Projekt) -> bool
```

Ob der Kern das Projekt aufbauen kann – ohne Fehler, der alles anhaelt.


## Konstanten

- `LISTEN = {'materialien': MaterialEintrag, **{liste: klasse for liste, (klasse,…` – Die Listen, deren Eintraege ein Werkzeug anspricht – die Materialien und die Apps –, je mit der Klasse ihrer Eintraege.
- `BAUTEILLISTEN = tuple((art.liste for art in BAUTEILE))` – Die Listen, deren Eintraege rechnen: ohne Materialien und Skripte.

## Braucht

- [[opencivil.projekt]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.netz]]
- [[opencivil.projekt.projekt]]
- [[opencivil.web.dienst]]

## Gebraucht von

- [[opencivil.mcp.ausgabe]]
- [[opencivil.mcp.server]]
- [[opencivil.mcp.werkzeuge]]
- [[opencivil.mcp.zeiger]]
