---
erzeugt: 0d6171762c41
art: modul
tags: [modul]
---
> [!abstract] opencivil/mcp/werkzeuge.py
> was eine KI mit dem Werkzeug tun kann, und mit welchen Angaben.
> Paket [[opencivil.mcp]] · [Quelltext](../../opencivil/mcp/werkzeuge.py)

Jedes Werkzeug ist eine Funktion mit Titel, Beschreibung und Eingaben
([[opencivil.mcp.werkzeuge#werkzeug|werkzeug]]). Was es annimmt, sagt seine Unterschrift: ein Argument
ohne Vorgabe ist Pflicht, und die Eingaben muessen in Namen und Folge zu ihr
passen -- so laufen Beschreibung und Funktion nicht auseinander. Jedes gibt
Text zurueck. Was es nicht kann, meldet es als Fehler des Werkzeugs
(`isError`), mit dem Satz des Kerns; ein Werkzeug, das aendert, aendert
dann nichts ([[opencivil.mcp.sitzung#Sitzung.aendern|aendern]]).

## Inhalt

### Werkzeug

```python
@dataclass(frozen=True)
class Werkzeug
```

Ein Werkzeug, wie `tools/list` es nennt und `tools/call` es ruft.

- `name: str`
- `titel: str`
- `beschreibung: str`
- `eingaben: Mapping[str, Mapping[str, Any]]`
- `pflicht: Tuple[str, ...]`
- `lesend: bool` – Ob es nur liest -- dann aendert es weder die Mappe noch eine Datei.
- `tun: Callable[..., str]`

#### Werkzeug.verzeichnis

```python
def verzeichnis(self) -> Dict[str, Any]
```

Wie `tools/list` es nennt, mit dem JSON-Schema seiner Eingaben.

#### Werkzeug.aufrufen

```python
def aufrufen(self, sitzung: Sitzung, argumente: Any) -> Dict[str, Any]
```

`tools/call`: sein Ergebnis als Text -- ein Fehler mit `isError`, wie MCP es will.

### werkzeug

```python
def werkzeug(titel: str, beschreibung: str, *, lesend: bool=False, **eingaben: Mapping[str, Any]) -> Callable[[Callable[..., str]], Callable[..., str]]
```

Traegt die Funktion darunter als Werkzeug ein, unter ihrem Namen. Ihr
erstes Argument ist die Sitzung; die uebrigen sind die `eingaben`, je
mit ihrem JSON-Schema, in derselben Folge.

### datei_oeffnen

```python
@werkzeug('Projektdatei öffnen', 'Öffnet eine Projektdatei (eine Mappe mit einem oder mehreren Projekten) wie «Öffnen» der Seite: geprüft, mit den Sandboxen, wie gespeichert. Danach ist das erste Projekt gewählt; in ihm arbeiten alle anderen Werkzeuge.', pfad=DATEI, verwerfen=VERWERFEN)
def datei_oeffnen(sitzung: Sitzung, pfad: str, verwerfen: bool=False) -> str
```

### datei_neu

```python
@werkzeug('Neue Projektdatei', f'Eine neue Mappe mit einem Projekt «Projekt 1» – mit {ERSTER_BETON} und {ERSTER_STAHL} und einer Sandbox je App, noch ohne Datei: datei_speichern mit pfad schreibt sie.', verwerfen=VERWERFEN)
def datei_neu(sitzung: Sitzung, verwerfen: bool=False) -> str
```

### datei_speichern

```python
@werkzeug('Projektdatei speichern', 'Schreibt die Mappe mit allen Projekten und ihren Sandboxen, wie «Speichern» der Seite – ohne pfad in die offene Datei.', pfad=_text('Wohin – ohne Angabe in die offene Datei.'), ueberschreiben=UEBERSCHREIBEN)
def datei_speichern(sitzung: Sitzung, pfad: str='', ueberschreiben: bool=False) -> str
```

### projekte

```python
@werkzeug('Projekte', 'Die Projekte der Mappe und welches gewählt ist.', lesend=True)
def projekte(sitzung: Sitzung) -> str
```

### projekt_waehlen

```python
@werkzeug('Projekt wählen', 'Wählt ein Projekt der Mappe – in ihm arbeiten danach alle anderen Werkzeuge.', name=_text('Der Name des Projekts.'))
def projekt_waehlen(sitzung: Sitzung, name: str) -> str
```

### projekt_anlegen

```python
@werkzeug('Projekt anlegen', f'Ein neues Projekt hinter den anderen, gleich gewählt – wie «+» der Projektreihe: mit {ERSTER_BETON}, {ERSTER_STAHL} und einer Sandbox je App.', name=_text('Sein Name – ohne Angabe «Projekt 2» oder die nächste freie Nummer.'))
def projekt_anlegen(sitzung: Sitzung, name: str='') -> str
```

### arten

```python
@werkzeug('Apps', 'Die Apps, je mit ihrer Liste – so heisst «app» in den anderen Werkzeugen – und dem Namen ihrer Felder für felder; dazu die Sorten der Materialien. Braucht keine offene Datei.', lesend=True)
def arten(sitzung: Sitzung) -> str
```

### felder

```python
@werkzeug('Felder', 'Was eine Art von Eintrag hält, je Feld: «art» (zahl, ganz, text, ja/nein, wahl mit ihren Werten, eintrag, liste oder zuordnung), «leer», wo auch nichts stehen darf, Einheit und Grenzen; dazu unter «neu», wie ein neuer aussieht. Elemente darin – Lastfälle, Lagen, Schichten – mit dem Namen, den «klasse» nennt.', lesend=True, art=_text('Eine App – ihre Liste («querschnitte») oder der Name ihrer Einträge («Platte») – oder eine Klasse, wie «klasse» sie nennt («kombination»).'))
def felder(sitzung: Sitzung, art: str) -> str
```

### _klasse

```python
def _klasse(art: str) -> type
```

Die Klasse von Eintraegen, die `art` nennt -- ueber ihren Namen im Katalog oder ihre App.

### eintraege

```python
@werkzeug('Einträge', 'Die Einträge des gewählten Projekts je App, mit Kennung. Die Sandbox jeder App ist zum Ausprobieren: sie kommt nicht in den Bericht und lässt sich nicht löschen, nur zurücksetzen.', lesend=True, app=_text('Nur diese App – ohne Angabe alle.'))
def eintraege(sitzung: Sitzung, app: str='') -> str
```

### eintrag_lesen

```python
@werkzeug('Eintrag lesen', 'Ein Eintrag, wie er in der Projektdatei steht, als JSON – die Form, die eintrag_setzen nimmt und in die die Pfade von eintrag_aendern zeigen.', lesend=True, eintrag=EINTRAG, app=APP)
def eintrag_lesen(sitzung: Sitzung, eintrag: str, app: str='') -> str
```

### eintrag_setzen

```python
@werkzeug('Eintrag setzen', 'Ersetzt einen Eintrag ganz durch inhalt, in der Form von eintrag_lesen. Der Kern liest ihn wie eine Datei; was er nicht lesen kann, ändert nichts, und seine Meldung kommt zurück. Die Kennung bleibt. Elemente darin – Lastfälle, Knoten – tragen eigene Kennungen, und eine gelöschte kommt nie wieder.', eintrag=EINTRAG, inhalt={'type': 'object', 'description': 'Der ganze Eintrag.'}, app=APP)
def eintrag_setzen(sitzung: Sitzung, eintrag: str, inhalt: Dict[str, Any], app: str='') -> str
```

### eintrag_aendern

```python
@werkzeug('Eintrag ändern', 'Ändert Felder eines Eintrags über Pfade in seine Form von eintrag_lesen: «/h», «/lastfaelle/0/M_Ed»; «-» am Ende einer Liste hängt an. Die Änderungen gelten alle zusammen oder keine. Der Kern prüft sie sofort; was er nicht lesen kann, ändert nichts, und seine Meldung kommt zurück.', eintrag=EINTRAG, aenderungen={'type': 'array', 'description': 'Die Änderungen, der Reihe nach.', 'items': {'type': 'object', 'additionalProperties': False, 'required': ['pfad'], 'properties': {'pfad': _text('Wohin, nach RFC 6901: «/h», «/lastfaelle/0/M_Ed», «/lastfaelle/-» hängt an; «» ist der ganze Eintrag.'), 'wert': {'description': 'Der neue Wert – Zahl, Text, true/false, Liste oder Objekt.'}, 'entfernen': _ja_nein('true statt wert: aus der Liste nehmen, ein Feld auf seine Vorgabe zurück.')}}}, app=APP)
def eintrag_aendern(sitzung: Sitzung, eintrag: str, aenderungen: list, app: str='') -> str
```

### eintrag_anlegen

```python
@werkzeug('Eintrag anlegen', '«+» einer App: ein neuer Eintrag nach der Vorlage des Kerns, am Ende der Liste, mit dem ersten Material jeder Art, das er nimmt. Er heisst wie in der Seite – «Platte 1» – oder name.', app=_text('Die App: ihre Liste («querschnitte») oder der Name ihrer Einträge («Platte»). Materialien legt material_anlegen an.'), name=_text('Sein Name – ohne Angabe der nächste freie, «Platte 2».'))
def eintrag_anlegen(sitzung: Sitzung, app: str, name: str='') -> str
```

### material_anlegen

```python
@werkzeug('Material anlegen', '«+ Material»: eine Normsorte, wie sie ist – oder mit eigen ein eigenes Material mit ihr als Vorlage, dessen Kennwerte sich ändern lassen.', art=_text('Die Art des Materials.', enum=list(MATERIALARTEN)), sorte=_text('Die Sorte – «C30/37», «B500B», «S355»; arten nennt alle.'), eigen=_ja_nein('true: ein eigenes Material nach der Sorte.'))
def material_anlegen(sitzung: Sitzung, art: str, sorte: str, eigen: bool=False) -> str
```

### eintrag_kopieren

```python
@werkzeug('Eintrag kopieren', '⧉: eine Kopie gleich hinter dem Original, alles wie dort – «Decke (Kopie)». Die Kopie der Sandbox ist ein gewöhnlicher Eintrag und heisst wie ein neuer.', eintrag=EINTRAG, app=APP)
def eintrag_kopieren(sitzung: Sitzung, eintrag: str, app: str='') -> str
```

### eintrag_loeschen

```python
@werkzeug('Eintrag löschen', '×: ein Eintrag oder ein Material geht – nicht die Sandbox, und nicht, solange ein Bauteil darauf zeigt; die Meldung nennt es dann.', eintrag=EINTRAG, app=APP)
def eintrag_loeschen(sitzung: Sitzung, eintrag: str, app: str='') -> str
```

### sandbox_zuruecksetzen

```python
@werkzeug('Sandbox zurücksetzen', '↺: die Sandbox einer App beginnt neu, nach der Vorlage und mit dem ersten Material jeder Art. Wer auf sie zeigt, zeigt weiter auf sie.', app=_text('Die App: ihre Liste («querschnitte») oder der Name ihrer Einträge («Platte»).'))
def sandbox_zuruecksetzen(sitzung: Sitzung, app: str) -> str
```

### _gemeldet

```python
def _gemeldet(was: str, geaendert: Geaendert) -> str
```

Was eine Aenderung zurueckgibt: den Eintrag und, in den Worten des Kerns, was ihm fehlt.

### rechnen

```python
@werkzeug('Rechnen', 'Rechnet das gewählte Projekt – ohne die Sandboxen, wie der Bericht – oder mit eintrag nur dieses Bauteil, auch eine Sandbox. Zurück kommt je Bauteil die Tabelle seiner Nachweise mit dem Erfüllungsgrad, wie die Zusammenfassung der Seite, und was der Kern dazu sagt – auch, was noch fehlt.', lesend=True, eintrag=_text('Nur dieses Bauteil, Name oder Kennung – ohne Angabe alle.'), app=APP)
def rechnen(sitzung: Sitzung, eintrag: str='', app: str='') -> str
```

### herleitung

```python
@werkzeug('Herleitung', 'Die Herleitung eines Bauteils als Markdown mit LaTeX, wie die rechte Spalte der Seite – mit seinen Materialien und den Bauteilen, deren Querschnitt es nimmt. Sie ist lang: mit pfad in eine Datei.', eintrag=EINTRAG, app=APP, pfad=AUSGABE, ueberschreiben=UEBERSCHREIBEN)
def herleitung(sitzung: Sitzung, eintrag: str, app: str='', pfad: str='', ueberschreiben: bool=False) -> str
```

### bericht

```python
@werkzeug('Bericht', 'Der Bericht des gewählten Projekts, ohne die Sandboxen – als Markdown oder als LaTeX-Dokument, wie «Bericht» der Seite. Er ist lang: mit pfad in eine Datei.', als=_text('markdown oder latex.', enum=['markdown', 'latex']), pfad=AUSGABE, ueberschreiben=UEBERSCHREIBEN)
def bericht(sitzung: Sitzung, als: str='markdown', pfad: str='', ueberschreiben: bool=False) -> str
```

### _bauteil

```python
def _bauteil(sitzung: Sitzung, eintrag: str, app: str) -> str
```

Die Kennung des Bauteils, das `eintrag` nennt -- ein Material oder Skript rechnet nicht fuer sich.

### _ausgeben

```python
def _ausgeben(text: str, pfad: str, ueberschreiben: bool) -> str
```

`text` zurueck -- oder mit `pfad` in diese Datei, und zurueck, wohin.

### _pruefen

```python
def _pruefen(w: Werkzeug, argumente: Any) -> None
```

Die Argumente gegen die Eingaben des Werkzeugs -- vor dem Aufruf, mit Satz statt Ausnahme.


## Konstanten

- `WERKZEUGE = {}` – Die Werkzeuge unter ihrem Namen, in der Folge, in der `tools/list` sie nennt.
- `EINTRAG = _text('Name oder Kennung des Eintrags, wie eintraege sie nennt – «Dec…`
- `APP = _text('Die App, wenn der Name in mehreren steht wie «Sandbox»: ihre L…`
- `DATEI = _text('Pfad der Projektdatei (.json), absolut oder vom Arbeitsverzeic…`
- `VERWERFEN = _ja_nein('true: Änderungen der offenen Mappe, die noch nicht gespeich…`
- `UEBERSCHREIBEN = _ja_nein('true: eine Datei, die es dort schon gibt, überschreiben.')`
- `AUSGABE = _text('In diese Datei schreiben, statt den Text zurückzugeben.')`
- `_TYPEN = {'string': (str, 'Text'), 'boolean': (bool, 'true oder false'), 'inte…` – Je Typ des JSON-Schemas, was ihn in Python traegt, und wie er in einer Meldung heisst.

## Braucht

- [[opencivil.material.arten]]
- [[opencivil.material.beton]]
- [[opencivil.material.betonstahl]]
- [[opencivil.mcp.ausgabe]]
- [[opencivil.mcp.sitzung]]
- [[opencivil.mcp.zeiger]]
- [[opencivil.projekt]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.projekt]]
- [[opencivil.web.api]]

## Gebraucht von

- [[opencivil.mcp.server]]
