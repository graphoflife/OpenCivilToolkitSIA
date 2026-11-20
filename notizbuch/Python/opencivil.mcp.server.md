---
erzeugt: edbe55cd8c0d
art: modul
tags: [modul]
---
> [!abstract] opencivil/mcp/server.py
> das Protokoll: JSON-RPC 2.0 ueber stdin und stdout.
> Paket [[opencivil.mcp]] · [Quelltext](../../opencivil/mcp/server.py)

## VERANTWORTUNG

Wie eine Anfrage ankommt und ihre Antwort hinausgeht -- eine Nachricht je
Zeile, wie MCP es fuer stdio vorsieht. Der Server kennt `initialize`,
`ping`, `tools/list` und `tools/call`; eine Mitteilung (ohne `id`)
beantwortet er nicht. Was ein Werkzeug tut, steht in
[[opencivil.mcp.werkzeuge]].


## STDOUT GEHOERT DEM PROTOKOLL

Waehrend der Server laeuft, schreibt `print` nach stderr: eine Zeile, die
ein Baustein des Kerns ausgibt, zerbraeche sonst die naechste Nachricht.

## Inhalt

### Protokollfehler

```python
class Protokollfehler(Exception)
```

Ein Fehler von JSON-RPC, mit seinem Code -- anders als der Fehler eines Werkzeugs.

### Server

```python
class Server
```

Beantwortet die Nachrichten einer Verbindung, mit einer Sitzung fuer alle Werkzeuge.

#### Server.antwort

```python
def antwort(self, nachricht: Any) -> Optional[Any]
```

Die Antwort auf eine Nachricht -- auf einen Stapel die Liste der Antworten, auf eine Mitteilung keine.

#### Server._beginnen

```python
def _beginnen(self, parameter: Dict[str, Any]) -> Dict[str, Any]
```

`initialize`: die Fassung des Programms, wenn der Server sie spricht, sonst seine neueste.

### bedienen

```python
def bedienen(eingabe: IO[bytes], ausgabe: IO[bytes]) -> None
```

Liest Nachrichten aus `eingabe`, Zeile fuer Zeile, und schreibt jede Antwort als eine Zeile nach `ausgabe`.

### main

```python
def main() -> None
```

`python3 -m opencivil.mcp`: bedient stdin und stdout, bis stdin endet.


## Konstanten

- `FASSUNGEN = ('2025-06-18', '2025-03-26', '2024-11-05')` – Die Fassungen des Protokolls, die der Server spricht, die neueste zuerst.
- `SERVER = {'name': 'opencivil', 'title': 'OpenCivilToolkitSIA', 'version': '1'}` – Was `initialize` ueber den Server sagt.
- `ANLEITUNG = 'OpenCivilToolkitSIA rechnet Bauteile nach SIA 262:2025 und SIA 267:2…` – Was eine KI vor dem ersten Werkzeug wissen sollte -- `instructions` von `initialize`.

## Braucht

- [[opencivil.mcp.sitzung]]
- [[opencivil.mcp.werkzeuge]]

## Gebraucht von

- [[opencivil.mcp.__main__]]
