"""
opencivil/stabwerk3d -- raeumliche Stabwerke nach der Steifigkeitsmethode.

Der Rechenkern der App «3D Balkensysteme»: ein Rahmen im Raum, gerechnet mit
Euler-Bernoulli-Staeben und Torsion nach St. Venant, Theorie 1. Ordnung --
wie :mod:`opencivil.stabwerk` in der Ebene, mit sechs Unbekannten je Knoten.
Heraus kommen Verschiebungen und Drehungen, Normalkraft, zwei Querkraefte,
Torsionsmoment, zwei Biegemomente und Lagerkraefte -- je Lastfall und je
Kombination.

* :mod:`~opencivil.stabwerk3d.modell` -- was gerechnet wird, in SI.
* :mod:`~opencivil.stabwerk3d.raum` -- Vektoren, Richtungen und Strecken.
* :mod:`~opencivil.stabwerk3d.stab` -- der einzelne Stab: seine Achsen, und
  wie er aus drei ebenen Staeben besteht.
* :mod:`~opencivil.stabwerk3d.system` -- das ganze System: Unbekannte,
  Zusammenbau, Loesen, Lagerkraefte.
* :mod:`~opencivil.stabwerk3d.verlauf` -- Schnittgroessen und Biegelinien
  laengs jedes Stabs.

Was die Ebene schon kann, kommt von dort: das Gleichungssystem
(:mod:`opencivil.stabwerk.matrix`), der ebene Stab mit Lasten und Bettung,
der Verlauf laengs eines Stabs. Nur die Standardbibliothek.
"""
