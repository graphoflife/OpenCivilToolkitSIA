---
erzeugt: 460283fe03aa
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/__init__.py
> die Oberflaeche, von der Seite des Rechenkerns.
> Paket [[opencivil]] · [Quelltext](../../opencivil/web/__init__.py)

Der Dienst ([[opencivil.web.dienst]]), den der lokale Server und Pyodide
im Browser gleich aufrufen, die Uebersetzung der Ergebnisse nach JSON, die
Daten der Diagramme -- und die Bruecke, die festhaelt, welche Dateien der
Browser laedt, samt dem Notizbuch.

## Module

- [[opencivil.web.api]] – Uebersetzung der Rechenergebnisse nach JSON.
- [[opencivil.web.bruecke]] – Welche Dateien der Browser laden muss.
- [[opencivil.web.diagrammdaten]] – was die Oberflaeche zeichnet, als JSON.
- [[opencivil.web.dienst]] – Der Rechendienst, unabhaengig vom Transportweg.
- [[opencivil.web.server]] – Schlanker HTTP-Server fuer die Oberflaeche.
- [[opencivil.web.speicher]] – was vom letzten Lauf noch gilt.
