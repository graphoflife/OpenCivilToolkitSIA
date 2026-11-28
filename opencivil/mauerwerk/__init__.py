"""
opencivil/mauerwerk -- Wände aus unbewehrtem Mauerwerk nach SIA 266:2015.

Eine Wand in der Ansicht mit ihren Türen und Fenstern, den Stürzen
darüber und den Pfeilern dazwischen, aus einem Mauerwerk des Projekts
(:mod:`opencivil.material.mauerwerk`). Die Nachweise kommen Schritt um
Schritt dazu (Plan vom 2026-11-27, Schritt 14).

    modell.py      die Wand in SI: Umriss, Öffnungen mit Stürzen, wie sie
                   gemauert ist, Ränder -- und wo die Pfeiler stehen
    kennwerte.py   mit welchen Werten ihres Mauerwerks sie rechnet
    pruefen.py     was der Zeichnung fehlt oder an ihr nicht stimmt
    lasten.py      wie ihre Lasten zu Pfeilern und Stürzen kommen
    knicken.py     k_N eines Pfeilers nach Theorie 2. Ordnung
    nachweise.py   die Nachweise: Normalkraft je Pfeiler, Teilflächen je Sturzauflager
    werk.py        die Wand im Rechenwerk und ihr Befund
    herleitung.py  wie sie ihre Rechnung aufschreibt
    uebersicht.py  ihre Angaben über den Nachweisen in der Zusammenfassung
"""
