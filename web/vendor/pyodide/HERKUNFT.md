# Pyodide 314.0.6

Python als WebAssembly. Damit läuft in `web/js/kern_arbeiter.js` derselbe Rechenkern im
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

## Fremdpakete für die App «Python»

Was ein Skript dort einbinden kann, liegt als Rad daneben — numpy und pandas,
mit allem, was pandas braucht. Freigegeben vom Benutzer am 2026-10-15, Datei
für Datei; ein weiteres Paket nur mit seiner Erlaubnis. Geholt aus der vollen
Verteilung derselben Fassung,
<https://cdn.jsdelivr.net/pyodide/v314.0.6/full/>, und jede Datei gegen ihre
Prüfsumme in `pyodide-lock.json` gehalten:

| Datei                                                       | Grösse  | Lizenz       |
| ----------------------------------------------------------- | ------- | ------------ |
| `numpy-2.4.6-cp314-cp314-pyemscripten_2026_0_wasm32.whl`    | 2.92 MB | BSD-3-Clause |
| `pandas-3.0.2-cp314-cp314-pyemscripten_2026_0_wasm32.whl`   | 4.18 MB | BSD-3-Clause |
| `python_dateutil-2.9.0.post0-py2.py3-none-any.whl`          | 0.23 MB | Apache-2.0, BSD |
| `pytz-2026.1.post1-py2.py3-none-any.whl`                    | 0.51 MB | MIT          |
| `six-1.17.0-py2.py3-none-any.whl`                           | 0.01 MB | MIT          |

Der Browser lädt ein Rad erst, wenn ein Skript das Paket mit `import`
einbindet. Welche beiliegen, schreibt `python3 -m opencivil.web.bruecke` aus
den Dateien hier ins Kernverzeichnis (`web/kern/dateien.json`, `pakete`).

## Erneuern

```bash
python3 werkzeug/pyodide_holen.py 314.0.7
```

Das holt auch die Fremdpakete in der neuen Fassung und räumt die alten weg;
nur sie allein: `python3 werkzeug/pyodide_holen.py --pakete`.

Danach die Oberfläche einmal aufrufen und prüfen, dass unten links
„Kern bereit" steht.

## Lizenz

Pyodide steht unter der Mozilla Public License 2.0, die mitgelieferte
Standardbibliothek unter der PSF-Lizenz. Beide erlauben die Weitergabe in
unveränderter Form, wie sie hier geschieht.
