Wie Claude an diesem Projekt arbeitet. Jede neue Sitzung lädt diese Seite über
`CLAUDE.md` im Repo. Was hier steht, gilt, bis der Benutzer etwas anderes sagt;
eine neue Regel für die Arbeit kommt hierher.

## Sprache

Alles auf Deutsch: Oberfläche, Berichte, Fehlermeldungen, Bezeichner im Code,
Kommentare, Tests und Commit-Meldungen – auch wenn der Benutzer auf Englisch
schreibt. Er hat das zu Beginn ausdrücklich so verlangt; die Sprache seiner
Nachricht sagt nichts über die Sprache der Ausgabe. Fachbegriffe deutsch,
technisches Beiwerk darf englisch bleiben (`Groesse`, `Nachweis` neben
`parse`, `handler`).

## Committen

- Nach **jeder** abgeschlossenen Änderung ein Commit, nicht gesammelt am Ende
  einer Sitzung. Die Commits sind das Rückfallnetz des Benutzers; grosse
  Sammel-Commits nehmen es ihm. Nicht vorher fragen – das ist bewilligt.
- Danach Push nach `origin/main`. Ein Push veröffentlicht die Seite.
- Kern und Oberfläche im selben Commit, damit die Seite nie halb steht.
- Commit-Meldungen deutsch, wie die bisherige Geschichte.

Vor jedem Commit:

```bash
python3 -m opencivil.web.bruecke        # Verzeichnis und Versionsmarken der Seite
python3 -m unittest discover -s tests -t .
python3 -m tests.test_schnappschuss     # Abweichungen lesen – erst dann:
python3 -m tests.test_schnappschuss --uebernehmen
```

JavaScript hat keinen Bauschritt. Seine Syntax prüft `node --check` über eine
Kopie der Datei mit der Endung `.mjs`.

## Veröffentlichung

- Repo: <https://github.com/graphoflife/OpenCivilToolkitSIA>, öffentlich,
  Branch `main`.
- Seite: <https://graphoflife.github.io/OpenCivilToolkitSIA/>. GitHub Pages
  liefert direkt vom Branch aus dem Wurzelverzeichnis, ohne Actions-Bau; nach
  dem Push dauert es etwa 20 s.
- Dort rechnet Python in Pyodide: die Seite lädt die `.py`-Dateien aus
  `opencivil/`. Darum wird `opencivil/` mit ausgeliefert, und `.nojekyll` bleibt
  liegen – ohne die Datei machte GitHub aus jeder `.md` eine HTML-Seite.
- Keine Rechenlogik in JavaScript, nie: beide Wege, Server und Pyodide, rufen
  `opencivil/web/dienst.py` auf.
- Pyodide liegt im Repo statt auf einem CDN, Pages baut vom Branch statt über
  Actions. So hat es der Benutzer am 2026-09-11 entschieden, nachdem er die
  Alternativen gesehen hatte. Nicht ohne Rückfrage umstellen.
- Keine fremden Pakete. Was fehlt, wird selbst geschrieben; ein Download
  braucht die ausdrückliche Erlaubnis des Benutzers, Datei für Datei.

## Grundsätze des Codes

- Jede Rechnung schreibt ihre Herleitung in LaTeX selbst.
- Jede Regel steht an genau einer Stelle.
- Die Oberfläche rechnet nichts, was in eine Rechnung eingeht.
- Die Zahlen des Benutzers werden nie still umgedeutet.
- Das Werkzeug ist ein Prototyp: alte Speicherstände müssen nicht weiter
  funktionieren (Benutzer, 2026-10-11).

## Normstellen

- Die Normstellen, also die Passagen aus SIA 262, liefert der Benutzer. Nie
  eine erfinden.
- Kein Verifikationsblatt der Normverweise bauen (entschieden am 2026-09-25):
  der Benutzer gleicht lieber mit den Originaltexten ab, als eine Liste
  nachzuschlagen.
- Kommen Passagen, den Code direkt dagegen prüfen – Konstanten, Formeln,
  `referenz=` – und die offenen Normfragen in [[TODO]] abhaken oder
  korrigieren.
- Was nach Vorgabe eingebaut ist, heisst im Code «nach Vorgabe, nicht
  nachgeschlagen» und steht in [[TODO]].

## Entschieden – nicht wieder ansprechen

- **k_σ = E/(400·f) bleibt** (2026-10-11), auch wenn der Anstieg der Parabel
  bei null damit 1.25·E_c,eff ist. Ändern nur, wenn der Benutzer eine
  Normstelle dazu liefert.

## Berichten und fragen

- In einfacher Sprache, mit einem konkreten Beispiel – wie es vorher aussah,
  wie nachher – und ohne Begriffe aus dem Code vorauszusetzen («Tafel»,
  «Block», «Vorlage», «p.formel»).
- Den eigentlichen Wunsch und das Aufräumen, das eine Durchsicht zusätzlich
  findet, getrennt darstellen und getrennt zur Wahl stellen.
- Abschlussberichte kurz: was sich für den Benutzer ändert, was er entscheiden
  muss (mit Empfehlung) und was er selbst prüfen muss. Einzelheiten nur auf
  Nachfrage oder in den Notizen.
- Warum: Der Benutzer musste bei dichten Fachzusammenfassungen zweimal
  nachfragen.

## Im Browser prüfen

Nach jeder Prüfung im Browser den gespeicherten Projektstand des Benutzers
wiederherstellen.

## Wohin welche Notiz gehört

- Was gebaut wurde und warum: [[Entwicklung]], neueste Einträge oben.
- Was offen ist: [[TODO]].
- Wie Claude arbeitet: hierher.
- Normstellen: in den Code (`referenz=`), nicht ins Notizbuch – der Bericht
  braucht sie auch.
