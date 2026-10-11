Das Notizbuch von [OpenCivilToolkitSIA](https://github.com/graphoflife/OpenCivilToolkitSIA):
wie das Werkzeug rechnet, wie seine Python-Bibliothek gebaut ist und was beim
Bauen gelernt wurde. Es ist ein gewöhnlicher Ordner mit Markdown-Dateien –
Obsidian liest ihn als Tresor, und GitHub zeigt die Dateien als Text.

## Was wo steht

- **Formelsammlung** – jede Formel des Werkzeugs als eigene Seite: die Formel,
  ihre Normstelle, die Grössen mit Links, ein Zahlenbeispiel, die Stelle im
  Code und die Theorie. Dazu je Thema eine Seite. *Entsteht gerade.*
- **Python** – je Modul der Bibliothek eine Seite, aus den Docstrings erzeugt.
  *Entsteht gerade.*
- **Notizen**
  - [[Arbeitsweise]] – wie Claude an diesem Projekt arbeitet.
  - [[Entwicklung]] – was gebaut wurde und warum, neueste Einträge oben.
  - [[TODO]] – was noch offen ist.

## In Obsidian öffnen

1. In Obsidian «Ordner als Tresor öffnen» wählen.
2. Den Ordner `notizbuch` im Repo wählen, also `…/OpenCivilToolkitSIA/notizbuch`.

Mehr braucht es nicht, auch kein Plugin. Formeln (`$…$`, `$$…$$`), Links,
Graph-Ansicht und Rückverweise gehen von selbst. Die Einstellungen liegen bei
(`.obsidian/app.json`): strenge Zeilenumbrüche, Links als `[[Name]]` und
Anhänge unter `Anhänge/`. Alles andere, was Obsidian in `.obsidian/` ablegt,
bleibt auf dem eigenen Rechner.
