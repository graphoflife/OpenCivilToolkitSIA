# MathLive 0.110.0

Der Formeleditor der «Analytischen Gleichungen»: ein `<math-field>` je Zeile,
getippt wird wie in Mathcad, heraus kommt LaTeX. Gerechnet und gesetzt wird im
Kern (`opencivil/gleichungen/`); MathLive liefert nur die Eingabe.

## Woher

Das npm-Paket <https://registry.npmjs.org/mathlive/-/mathlive-0.110.0.tgz>,
SHA-1 des Pakets `3fc411009bb1eaf37256025f0122a53fddf64166`.

## Warum hier und nicht vom CDN

Dieselbe Überlegung wie bei KaTeX und Pyodide nebenan: die Seite soll ohne
fremden Dienst laufen, auch offline. Geladen wird die Datei erst, wenn ein
Blatt offen ist (`web/js/gleichungen.js`) — wer keines öffnet, lädt sie nie.

## Was hier liegt und was nicht

| Datei              | Zweck                               |
| ------------------ | ----------------------------------- |
| `mathlive.min.mjs` | der Editor, als Modul, unverändert  |
| `LICENSE.txt`      | die Lizenz aus dem Paket            |

Weggelassen: die übrigen Bauformen (`mathlive.js`, `mathlive.mjs`,
`mathlive.min.js`, `mathlive-ssr.min.mjs`, `vue-mathlive.mjs`), die
Stilblätter für statisches Setzen, `sounds/` (Tastenklicks, abgeschaltet),
`types/` (Typangaben für TypeScript).

Auch `fonts/` fehlt: die 20 Schriften darin sind byte-gleich mit denen von
KaTeX. `gleichungen.js` zeigt MathLive darum auf `web/vendor/katex/fonts/`.
Beim Erneuern prüfen, dass das noch stimmt:

```bash
for f in package/fonts/*.woff2; do cmp "$f" web/vendor/katex/fonts/$(basename "$f"); done
```

## Erneuern

Paket holen, `mathlive.min.mjs` und `LICENSE.txt` hierher kopieren, Version
und SHA-1 oben nachführen, die Schriften wie oben vergleichen. Danach ein
Blatt öffnen und prüfen: Formel tippen, Enter, Raster, keine Fehler in der
Konsole.

## Lizenz

MIT (siehe `LICENSE.txt`) — Weitergabe erlaubt, mit dem Lizenztext.
