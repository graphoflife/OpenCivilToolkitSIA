---
erzeugt: 7126d82800c7
art: modul
tags: [modul]
---
> [!abstract] opencivil/mauerwerk/__init__.py
> Wände aus unbewehrtem Mauerwerk nach SIA 266:2015.
> Paket [[opencivil]] · [Quelltext](../../opencivil/mauerwerk/__init__.py)

Eine Wand in der Ansicht mit ihren Türen und Fenstern, den Stürzen
darüber und den Pfeilern dazwischen, aus einem Mauerwerk des Projekts
([[opencivil.material.mauerwerk]]). Die Nachweise kommen Schritt um
Schritt dazu (Plan vom 2026-11-27, Schritt 14).

```
modell.py      die Wand in SI: Umriss, Öffnungen mit Stürzen, wie sie
               gemauert ist, Ränder -- und wo die Pfeiler stehen
kennwerte.py   mit welchen Werten ihres Mauerwerks sie rechnet
pruefen.py     was der Zeichnung fehlt oder an ihr nicht stimmt
werk.py        die Wand im Rechenwerk und ihr Befund
herleitung.py  wie sie ihre Rechnung aufschreibt
```

## Module

- [[opencivil.mauerwerk.herleitung]] – wie eine Mauerwerkswand ihre Rechnung aufschreibt.
- [[opencivil.mauerwerk.kennwerte]] – mit welchen Werten ihres Mauerwerks eine Wand rechnet.
- [[opencivil.mauerwerk.modell]] – eine Mauerwerkswand in der Ansicht, in SI.
- [[opencivil.mauerwerk.pruefen]] – was einer Wand fehlt oder an ihr nicht stimmt.
- [[opencivil.mauerwerk.werk]] – eine Mauerwerkswand im Rechenwerk.
