Das Notizbuch von [OpenCivilToolkitSIA](https://github.com/graphoflife/OpenCivilToolkitSIA):
wie das Werkzeug rechnet, wie seine Python-Bibliothek gebaut ist und was beim
Bauen gelernt wurde. Es ist ein gewöhnlicher Ordner mit Markdown-Dateien –
Obsidian liest ihn als Tresor, und GitHub zeigt die Dateien als Text.

## Was wo steht

- [[Formelsammlung]] – jede Formel des Werkzeugs als eigene Seite: die Formel,
  ihre Normstelle, die Grössen mit Links, ein Zahlenbeispiel, die Stelle im
  Code und die Theorie. Dazu je Thema eine Seite.
- [[Python]] – je Modul der Bibliothek eine Seite, aus den Docstrings erzeugt;
  wie alles zusammen rechnet, sagt [[opencivil]].
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

## Erzeugt und von Hand

Die Seiten der Formelsammlung und der Python-Doku schreibt
`python3 -m opencivil.web.bruecke` aus dem Code. Sie tragen oben die Eigenschaft `erzeugt` – eine Prüfsumme über
alles bis zur Linie `<!-- Ab hier von Hand … -->`.

- **Über der Linie** schreibt nur der Generator, bei jedem Lauf neu. Wer dort
  etwas ändert, ändert die Prüfsumme: die Brücke schreibt dann gar nichts und
  nennt die Datei.
- **Unter der Linie** steht, was von Hand dazukommt – die Theorie. Es bleibt
  beim Neuerzeugen Zeichen für Zeichen erhalten.
- **Erzeugte Seiten nicht umbenennen.** Ihr Name kommt aus dem Code; Obsidian
  führte sonst die Links in anderen erzeugten Seiten nach, und deren
  Prüfsummen stimmten nicht mehr.
- **Eigene Notizen** dürfen überall liegen. Dateien ohne `erzeugt` fasst der
  Generator nie an. Auf der Seite erscheint eine neue Notiz, sobald die Brücke
  gelaufen ist; eine geänderte gleich nach dem Hochladen.
- **Normstellen** stehen im Code, nicht hier – der Bericht braucht sie auch.
  Welche noch fehlen, sagt die [[Formelsammlung]].
