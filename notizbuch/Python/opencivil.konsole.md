---
erzeugt: 0efd4a7ca0ef
art: modul
tags: [modul]
---
> [!abstract] opencivil/konsole/__init__.py
> Python im Browser, für die App «Python».
> Paket [[opencivil]] · [Quelltext](../../opencivil/konsole/__init__.py)

Ein Skript oder eine Zeile der Konsole läuft in einer Sitzung, deren
Variablen bleiben; rechts stehen sie im Beobachter. Ausgeführt wird im
Browser, in einem eigenen Faden mit Pyodide -- nie auf dem Rechner.

* [[opencivil.konsole.sitzung|sitzung]] -- der Namensraum, das Ausführen, was
  dabei herauskommt, und die Variablen.
* [[opencivil.konsole.zeichnen|zeichnen]] -- Diagramme mit den Befehlen von
  matplotlib, ohne matplotlib: `import zeichnen as plt`.
* [[opencivil.konsole.pakete|pakete]] -- welche Fremdpakete beiliegen (numpy,
  pandas) und wann sie geladen werden.
* [[opencivil.konsole.dienst|dienst]] -- die Anfragen des Fadens, als JSON.

Nichts davon rechnet einen Nachweis: die Skripte gehören dem Benutzer, und
was sie ausgeben, steht in keinem Bericht.

## Module

- [[opencivil.konsole.dienst]] – die Konsole als Dienst für ihren Faden.
- [[opencivil.konsole.pakete]] – welche Fremdpakete ein Skript einbinden kann.
- [[opencivil.konsole.sitzung]] – eine Python-Sitzung für die App «Python».
- [[opencivil.konsole.zeichnen]] – Diagramme aus der App «Python», ohne matplotlib.
