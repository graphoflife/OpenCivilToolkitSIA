# JetBrains Mono

Die Schrift der ganzen Oberfläche: jedes Zeichen gleich breit, wie in einem
Code-Editor. Die Formeln setzen weiterhin KaTeX und der Formeleditor, jeder mit
seinen eigenen Schriften.

## Woher

Das Repository <https://github.com/JetBrains/JetBrainsMono>, Stand
`19371302b95d218af43299bce79ddbddd0bc364d` (2025-01-31). Die veränderliche
Webschrift gibt es erst dort, nicht schon in der Ausgabe v2.304.

| Hier                           | Dort                                       | SHA-256 |
| ------------------------------ | ------------------------------------------ | ------- |
| `JetBrainsMono-Variable.woff2` | `fonts/webfonts/JetBrainsMono[wght].woff2` | `31ec365b93e4bad6f202ce23352a56d01ca4462b2afc782ed2cf6fa42ca9ac0e` |
| `OFL.txt`                      | `OFL.txt`                                  | `a76abf002c49097d146e86740a3105a5d00450b1592e820a1109a8c5680cd697` |

Die Schrift ist umbenannt, sonst unverändert: eckige Klammern sind in einer
Adresse nicht erlaubt und müssten überall maskiert werden.

## Warum hier und nicht von Google Fonts

Dieselbe Überlegung wie bei KaTeX, MathLive und Pyodide nebenan: die Seite soll
ohne fremden Dienst laufen, auch offline. Von Google Fonts geladen, meldete
dazu jeder Aufruf die Adresse des Besuchers an Google.

## Was hier liegt und was nicht

Eine Datei trägt alle Stärken von 100 bis 800; die Seite braucht 400, 600 und
700. Eingebunden ist sie in `web/css/stil.css` (`@font-face`).

Weggelassen: die Kursive (`JetBrainsMono-Italic[wght].woff2`, 120 KB). Die
Seite setzt nur an zwei Stellen kursiv, dort neigt der Browser die aufrechte
Schrift selbst. Ebenso die Einzelschnitte und die TTF-Dateien.

Es fehlen der Schrift ⌀ und einige Werkzeugzeichen der Zeichenfläche
(↶ ↷ ↺ ▭ ▱ ▥ ▣ ▬ ⤢ ⤧). Die nimmt der Browser aus einer Ersatzschrift des
Systems, wie schon mit der früheren Schrift.

## Erneuern

Datei holen, umbenennen, Stand und Prüfsummen oben nachführen. Danach die Seite
öffnen und in der Konsole prüfen, dass die Schrift geladen ist:

```js
[...document.fonts].map((f) => `${f.family} ${f.status}`)
```

## Lizenz

SIL Open Font License 1.1 (siehe `OFL.txt`): Weitergabe mit einem Programm
erlaubt, mit dem Lizenztext; allein verkauft werden darf die Schrift nicht.
