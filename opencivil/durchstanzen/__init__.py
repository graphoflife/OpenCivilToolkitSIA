"""
opencivil/durchstanzen -- der Durchstanznachweis nach SIA 262:2025, 4.3.6.

* :mod:`~opencivil.durchstanzen.schnitt` -- der Nachweisschnitt um die
  gestützte Fläche: was von ihm zählt (Figur 22 und 23), seine Länge u, die
  Fläche darin und sein Schwerpunkt.
* :mod:`~opencivil.durchstanzen.stelle` -- die Durchstanzstelle: Platte,
  gestützte Fläche, Biegebewehrung und Einwirkung als Vorgaben im
  Rechenwerk, und die Wahlen dazu.
* :mod:`~opencivil.durchstanzen.nachweis` -- der Nachweis: statische Höhe,
  k_e, die Lasten im Schnitt, die Plattenrotation und der Widerstand ohne
  Durchstanzbewehrung.
* :mod:`~opencivil.durchstanzen.mit_bewehrung` -- reicht der Beton nicht:
  die vier Nachweise mit Durchstanzbewehrung (4.3.6.5).
* :mod:`~opencivil.durchstanzen.bewehrung` -- wo die Leisten liegen, der
  äussere Schnitt (Figur 26) und die Suche nach der kleinsten, die reicht.
* :mod:`~opencivil.durchstanzen.produkte` -- ancoPLUS und ZEUS von AncoTech:
  Typen, Höhen, Abstände und die Faktoren ihrer Gutachten.
"""
