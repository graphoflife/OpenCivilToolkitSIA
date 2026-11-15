---
erzeugt: 4a1086f7f01f
art: modul
tags: [modul]
---
> [!abstract] opencivil/stabwerk3d/__init__.py
> was ein Stabwerk im Raum braucht.
> Paket [[opencivil]] · [Quelltext](../../opencivil/stabwerk3d/__init__.py)

Die App «3D Balkensysteme»: ein Rahmen im Raum, gerechnet mit
Euler-Bernoulli-Staeben und Torsion nach St. Venant, Theorie 1. Ordnung, mit
sechs Unbekannten je Knoten. Gerechnet wird im gemeinsamen Kern
([[opencivil.stabwerk.system]]), der auch die Ebene rechnet -- hier steht,
was nur der Raum hat:

* [[opencivil.stabwerk3d.modell|modell]] -- was gerechnet wird, in SI.
* [[opencivil.stabwerk3d.raum|raum]] -- Vektoren, Richtungen und Strecken.
* [[opencivil.stabwerk3d.stab|stab]] -- der einzelne Stab: seine Achsen, und
  wie er aus drei ebenen Staeben besteht.
* [[opencivil.stabwerk3d.rechnung|rechnung]] und
  [[opencivil.stabwerk3d.herleitung|herleitung]] -- das 3D-Balkensystem im
  Rechenwerk und wie es seine Rechnung aufschreibt.

Nur die Standardbibliothek.

## Module

- [[opencivil.stabwerk3d.herleitung]] – wie ein 3D-Balkensystem seine Rechnung aufschreibt.
- [[opencivil.stabwerk3d.modell]] – was gerechnet wird: das raeumliche Stabwerk in SI.
- [[opencivil.stabwerk3d.raum]] – Vektoren, Richtungen und Strecken im Raum.
- [[opencivil.stabwerk3d.rechnung]] – das 3D-Balkensystem im Rechenwerk.
- [[opencivil.stabwerk3d.stab]] – der raeumliche Stab: drei ebene in einem.
