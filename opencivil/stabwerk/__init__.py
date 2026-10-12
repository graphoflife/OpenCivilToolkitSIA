"""
opencivil/stabwerk -- ebene Stabwerke nach der Steifigkeitsmethode.

Der Rechenkern der App «2D Balkensysteme»: ein ebener Rahmen, belastet in
seiner Ebene, gerechnet mit Euler-Bernoulli-Staeben nach Theorie 1. Ordnung.
Heraus kommen Verschiebungen, Normalkraft, Querkraft, Moment und
Lagerkraefte -- je Lastfall und je Kombination.

* :mod:`~opencivil.stabwerk.matrix` -- das Gleichungssystem: im Profil
  gespeichert, umgekehrt nach Cuthill-McKee nummeriert, und was geschieht,
  wenn es singulaer ist.
* :mod:`~opencivil.stabwerk.stab` -- der einzelne Stab: Steifigkeit,
  arbeitsgleiche Lasten, Bettung.
* :mod:`~opencivil.stabwerk.modell` -- was gerechnet wird, in SI: Knoten,
  Staebe, Lager, Lasten.
* :mod:`~opencivil.stabwerk.system` -- das ganze System: Unbekannte,
  Zusammenbau, Loesen, Lagerkraefte.
* :mod:`~opencivil.stabwerk.verlauf` -- Schnittgroessen und Biegelinie
  laengs jedes Stabs.

Nur die Standardbibliothek: das Werkzeug rechnet auch im Browser.
"""
