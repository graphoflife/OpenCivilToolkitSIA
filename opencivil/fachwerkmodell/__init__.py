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
    werk.py        das Fachwerkmodell im Rechenwerk und sein Befund
    herleitung.py  wie es seine Rechnung aufschreibt
"""
