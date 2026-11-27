---
erzeugt: 43581c6bfb2f
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
grundstruktur.py  Ground Structure: die Knoten im Raster und die
               möglichen Stäbe, die ganz im Material liegen
optimierung.py die lineare Optimierung, ein primal-duales
               Innere-Punkte-Verfahren
suche.py       die Suche Runde um Runde, mit der Nachbearbeitung
nachrechnung.py  das Gleichgewicht des gefundenen Fachwerks und was die
               Lager aufnehmen
werk.py        das Fachwerkmodell im Rechenwerk und sein Befund
herleitung.py  wie es seine Rechnung aufschreibt
```

## Module

- [[opencivil.fachwerkmodell.grundstruktur]] – die Knoten und die möglichen Stäbe einer Scheibe.
- [[opencivil.fachwerkmodell.herleitung]] – wie ein Fachwerkmodell seine Rechnung aufschreibt.
- [[opencivil.fachwerkmodell.modell]] – die Scheibe eines Fachwerkmodells, in SI.
- [[opencivil.fachwerkmodell.nachrechnung]] – ein gefundenes Fachwerk, nachgerechnet.
- [[opencivil.fachwerkmodell.optimierung]] – das leichteste Fachwerk im Gleichgewicht, als lineare Optimierung.
- [[opencivil.fachwerkmodell.pruefen]] – was einem Fachwerkmodell fehlt oder an ihm nicht stimmt.
- [[opencivil.fachwerkmodell.suche]] – das leichteste Fachwerk, Runde um Runde.
- [[opencivil.fachwerkmodell.werk]] – das Fachwerkmodell im Rechenwerk.
