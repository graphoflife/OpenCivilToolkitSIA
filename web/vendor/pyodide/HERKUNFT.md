# Pyodide 314.0.6

Python als WebAssembly. Damit läuft in `web/js/kern.js` derselbe Rechenkern im
Browser, der auf dem Rechner unter CPython läuft — dieselben `.py`-Dateien,
nicht eine Nachbildung in JavaScript.

## Woher

<https://github.com/pyodide/pyodide/releases/tag/314.0.6>, Paket
`pyodide-core-314.0.6.tar.bz2`. Die Versionsnummer folgt der CPython-Version:
314 bedeutet Python 3.14.

## Warum hier und nicht vom CDN

Dieselbe Überlegung wie bei KaTeX nebenan: die Seite soll ohne fremden Dienst
laufen. Ein CDN-Ausfall oder eine zurückgezogene Version legte sonst das ganze
Werkzeug lahm, und offline ginge gar nichts. Der Preis sind rund 13 MB im Repo.

## Was hier liegt und was nicht

Aus dem Paket übernommen sind nur die fünf Dateien, die der Browser braucht:

| Datei               | Zweck                                            |
| ------------------- | ------------------------------------------------ |
| `pyodide.mjs`       | Ladehilfe, davon wird `loadPyodide` eingebunden   |
| `pyodide.asm.mjs`   | Bindeglied zwischen JavaScript und WebAssembly    |
| `pyodide.asm.wasm`  | der Python-Interpreter selbst                     |
| `python_stdlib.zip` | die Standardbibliothek                            |
| `pyodide-lock.json` | Paketverzeichnis, wird beim Start gelesen         |

Weggelassen: `python.exe`, `python`, `python.bat`, `python_cli_entry.mjs`
(Kommandozeile, im Browser nutzlos), `pyodide.js` (ältere Einbindungsart, wir
nehmen das Modul), `*.d.ts` (Typangaben für TypeScript).

Fremdpakete braucht der Kern keine — er kommt mit der Standardbibliothek aus.
`pyodide-lock.json` liegt trotzdem hier, weil `loadPyodide` es beim Start liest.

## Erneuern

```bash
python3 werkzeug/pyodide_holen.py 314.0.7
```

Danach die Oberfläche einmal aufrufen und prüfen, dass unten links
„Kern bereit" steht.

## Lizenz

Pyodide steht unter der Mozilla Public License 2.0, die mitgelieferte
Standardbibliothek unter der PSF-Lizenz. Beide erlauben die Weitergabe in
unveränderter Form, wie sie hier geschieht.
