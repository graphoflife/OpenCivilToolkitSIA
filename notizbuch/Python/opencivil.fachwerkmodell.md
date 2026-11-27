---
erzeugt: 6bb47111755a
art: modul
tags: [modul]
---
> [!abstract] opencivil/fachwerkmodell/__init__.py
> Fachwerkmodelle einer Scheibe, eben.
> Paket [[opencivil]] · [Quelltext](../../opencivil/fachwerkmodell/__init__.py)

Eine Scheibe aus Umrissen und Löchern, gehalten an Lagern und belastet mit
Punktlasten: das Werkzeug sucht ein Fachwerk, das die Lasten im
Gleichgewicht zu den Lagern trägt – ohne Material und ohne Dicke, nur aus
Form, Lagern und Lasten (Plan vom 2026-11-27, Entscheid 11).

```
modell.py      die Scheibe in SI: Umrisse, Löcher, Lager, Lasten und
               wo Material ist
pruefen.py     was der Beschreibung fehlt oder an ihr nicht stimmt --
               ohne Lager, ohne Last, ein Lager im Loch, eine Scheibe,
               die sich noch bewegen kann
werk.py        das Fachwerkmodell im Rechenwerk und sein Befund
herleitung.py  wie es seine Rechnung aufschreibt
```

## Module

- [[opencivil.fachwerkmodell.herleitung]] – wie ein Fachwerkmodell seine Rechnung aufschreibt.
- [[opencivil.fachwerkmodell.modell]] – die Scheibe eines Fachwerkmodells, in SI.
- [[opencivil.fachwerkmodell.pruefen]] – was einem Fachwerkmodell fehlt oder an ihm nicht stimmt.
- [[opencivil.fachwerkmodell.werk]] – das Fachwerkmodell im Rechenwerk.
