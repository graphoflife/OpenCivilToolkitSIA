---
erzeugt: 6c24e57eeb90
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
lasten.py      wie ihre lotrechten Lasten zu Pfeilern und Stürzen kommen
scheibe.py     wie ihre waagrechten Lasten zu den Pfeilern kommen
knicken.py     k_N eines Pfeilers nach Theorie 2. Ordnung
nachweise.py   die Nachweise: Normalkraft je Pfeiler, Teilflächen je Sturzauflager
schub.py       die Nachweise des Schubs je Pfeiler: Druckstrebe und Gleiten
werk.py        die Wand im Rechenwerk und ihr Befund
herleitung.py  wie sie ihre Rechnung aufschreibt
uebersicht.py  ihre Angaben über den Nachweisen in der Zusammenfassung
```

## Module

- [[opencivil.mauerwerk.herleitung]] – wie eine Mauerwerkswand ihre Rechnung aufschreibt.
- [[opencivil.mauerwerk.kennwerte]] – mit welchen Werten ihres Mauerwerks eine Wand rechnet.
- [[opencivil.mauerwerk.knicken]] – ein Pfeiler unter Normalkraft nach Theorie 2. Ordnung.
- [[opencivil.mauerwerk.lasten]] – wie die Lasten einer Wand zu ihren Pfeilern kommen.
- [[opencivil.mauerwerk.modell]] – eine Mauerwerkswand in der Ansicht, in SI.
- [[opencivil.mauerwerk.nachweise]] – die Nachweise einer Wand: Normalkraft und Teilflächen.
- [[opencivil.mauerwerk.pruefen]] – was einer Wand fehlt oder an ihr nicht stimmt.
- [[opencivil.mauerwerk.scheibe]] – wie die waagrechten Lasten einer Wand zu ihren Pfeilern kommen.
- [[opencivil.mauerwerk.schub]] – die Nachweise des Schubs in der Ebene einer Wand.
- [[opencivil.mauerwerk.uebersicht]] – was die Zusammenfassung einer Wand über ihren Nachweisen zeigt.
- [[opencivil.mauerwerk.werk]] – eine Mauerwerkswand im Rechenwerk.
