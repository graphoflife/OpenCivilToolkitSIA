---
erzeugt: 77108ef3ca82
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/server.py
> Schlanker HTTP-Server fuer die Oberflaeche.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/server.py)

## VERANTWORTUNG

Liefert die Dateien der Oberflaeche aus und reicht Anfragen an
[[opencivil.web.dienst]] weiter. Mehr nicht -- gerechnet wird ausschliesslich
dort, und zwar von demselben Code, der im Browser unter Pyodide laeuft.

Bewusst nur mit der Standardbibliothek gebaut. Der Rechenkern kommt ohne
Fremdpakete aus; das soll auch fuer den Server gelten, damit das ganze Werkzeug
mit einem blossen `python3` laeuft.


## WARUM ES IHN NEBEN DER BROWSERFASSUNG NOCH GIBT

Zwei Dinge kann nur er. Erstens startet die Oberflaeche sofort, statt erst
einige Sekunden auf Pyodide zu warten. Zweitens kann er den Bericht mit einer
richtigen TeX-Maschine zu PDF uebersetzen -- im Browser bleibt es beim `.tex`.


## WURZEL DES DOKUMENTBAUMS

Ausgeliefert wird vom Projektverzeichnis aus, nicht von `web/`. Das ist
Absicht: auf GitHub Pages liegt das Repo genauso im Netz, und die Bruecke im
Browser holt sich die `.py`-Dateien unter `/opencivil/…`. Waere die Wurzel
hier eine andere, haetten die Adressen auf beiden Wegen verschiedene Tiefe --
und genau solche Unterschiede faellt einem erst auf der veroeffentlichten Seite
auf die Fuesse.


## SICHERHEIT

Der Server bindet sich nur an 127.0.0.1. Er ist ein Arbeitsgeraet fuer den
eigenen Rechner, nicht fuer ein Netz. Ausgeliefert werden nur die in
[[opencivil.web.server#Konstanten|OEFFENTLICH]] genannten Ordner, und Pfadausbrueche sind geprueft.


## AUFRUF


```
python3 start_ui.py
# oder
python3 -m opencivil.web.server --port 8080
```

## Inhalt

### bericht_mit_pdf

```python
def bericht_mit_pdf(rumpf: dict) -> dienst.Antwort
```

Der Bericht des Dienstes, zusaetzlich auf die Platte gelegt und uebersetzt.

Das `.tex` stammt unveraendert aus [[opencivil.web.dienst#bericht|opencivil.web.dienst.bericht]] --
hier kommt nur dazu, was ein Browser nicht kann.

### aufloesen

```python
def aufloesen(pfad: str) -> Path | None
```

Wandelt eine Adresse in eine Datei -- oder `None`, wenn sie nicht darf.

Erlaubt ist nur, was in [[opencivil.web.server#Konstanten|OEFFENTLICH]] und
[[opencivil.web.server#Konstanten|OEFFENTLICHE_DATEIEN]] steht. Alles andere im Projektverzeichnis --
`daten/`, `.git/`, `tests/` -- bleibt draussen, auch wenn der Server
ohnehin nur auf 127.0.0.1 horcht.

Die Adresse kommt verschluesselt: «Statische Höhe.md» als
`Statische%20H%C3%B6he.md`. Erst entschluesselt, dann geprueft -- sonst
fiele ein `%2E%2E` an der Pruefung auf `..` vorbei.

### Handler

```python
class Handler(BaseHTTPRequestHandler)
```

- `server_version = 'OpenCivilToolkitSIA'`
- `protocol_version = 'HTTP/1.1'`

#### Handler.do_GET

```python
def do_GET(self) -> None
```

#### Handler.do_POST

```python
def do_POST(self) -> None
```

#### Handler.log_message

```python
def log_message(self, format: str, *args: Any) -> None
```

### starten

```python
def starten(port: int=8080, adresse: str='127.0.0.1') -> None
```


## Konstanten

- `WURZEL = Path(__file__).resolve().parents[2]`
- `AUSGABE_ORDNER = WURZEL / 'ausgabe'`
- `OEFFENTLICH = ('web', 'opencivil', 'notizbuch')` – Was aus dem Projektverzeichnis ins Netz darf. `opencivil` muss dabei sein: die Bruecke im Browser laedt von dort die Quelldateien des Rechenkerns; `notizbuch` zeigt die Oberflaeche unter «Formelsammlung».
- `OEFFENTLICHE_DATEIEN = ('index.html', 'favicon.ico')` – Einzelne Dateien im Wurzelverzeichnis, die ebenfalls ausgeliefert werden.

## Braucht

- [[opencivil.bericht.latex_dokument]]
- [[opencivil.web.dienst]]
- [[opencivil.web.umschlag]]
