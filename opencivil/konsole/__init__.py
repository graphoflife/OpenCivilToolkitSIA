"""
opencivil/konsole -- Python im Browser, für die App «Python».

Ein Skript oder eine Zeile der Konsole läuft in einer Sitzung, deren
Variablen bleiben; rechts stehen sie im Beobachter. Ausgeführt wird im
Browser, in einem eigenen Faden mit Pyodide -- nie auf dem Rechner.

* :mod:`~opencivil.konsole.sitzung` -- der Namensraum, das Ausführen, was
  dabei herauskommt, und die Variablen.
* :mod:`~opencivil.konsole.zeichnen` -- Diagramme mit den Befehlen von
  matplotlib, ohne matplotlib: ``import zeichnen as plt``.
* :mod:`~opencivil.konsole.pakete` -- welche Fremdpakete beiliegen (numpy,
  pandas) und wann sie geladen werden.
* :mod:`~opencivil.konsole.dienst` -- die Anfragen des Fadens, als JSON.

Nichts davon rechnet einen Nachweis: die Skripte gehören dem Benutzer, und
was sie ausgeben, steht in keinem Bericht.
"""
