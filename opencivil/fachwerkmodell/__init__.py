"""
opencivil/fachwerkmodell -- Fachwerkmodelle einer Scheibe, eben.

Eine Scheibe aus Umrissen und Löchern, gehalten an Lagern und belastet mit
Punktlasten: das Werkzeug sucht ein Fachwerk, das die Lasten im
Gleichgewicht zu den Lagern trägt -- ohne Material und ohne Dicke, nur aus
Form, Lagern und Lasten (Plan vom 2026-11-27, Entscheid 11).

    modell.py      die Scheibe in SI: Umrisse, Löcher, Lager, Lasten und
                   wo Material ist
    pruefen.py     was der Beschreibung fehlt oder an ihr nicht stimmt --
                   ohne Lager, ohne Last, ein Lager im Loch, eine Scheibe,
                   die sich noch bewegen kann
    grundstruktur.py  Ground Structure: die Knoten im Raster und die
                   möglichen Stäbe, die ganz im Material liegen
    optimierung.py die lineare Optimierung, ein primal-duales
                   Innere-Punkte-Verfahren
    suche.py       die Suche Runde um Runde, mit der Nachbearbeitung
    nachrechnung.py  das Gleichgewicht des gefundenen Fachwerks und was die
                   Lager aufnehmen
    werk.py        das Fachwerkmodell im Rechenwerk und sein Befund
    herleitung.py  wie es seine Rechnung aufschreibt
"""
