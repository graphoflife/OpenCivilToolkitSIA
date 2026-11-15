"""
opencivil/stabwerk3d -- was ein Stabwerk im Raum braucht.

Die App «3D Balkensysteme»: ein Rahmen im Raum, gerechnet mit
Euler-Bernoulli-Staeben und Torsion nach St. Venant, Theorie 1. Ordnung, mit
sechs Unbekannten je Knoten. Gerechnet wird im gemeinsamen Kern
(:mod:`opencivil.stabwerk.system`), der auch die Ebene rechnet -- hier steht,
was nur der Raum hat:

* :mod:`~opencivil.stabwerk3d.modell` -- was gerechnet wird, in SI.
* :mod:`~opencivil.stabwerk3d.raum` -- Vektoren, Richtungen und Strecken.
* :mod:`~opencivil.stabwerk3d.stab` -- der einzelne Stab: seine Achsen, und
  wie er aus drei ebenen Staeben besteht.
* :mod:`~opencivil.stabwerk3d.rechnung` und
  :mod:`~opencivil.stabwerk3d.herleitung` -- das 3D-Balkensystem im
  Rechenwerk und wie es seine Rechnung aufschreibt.

Nur die Standardbibliothek.
"""
