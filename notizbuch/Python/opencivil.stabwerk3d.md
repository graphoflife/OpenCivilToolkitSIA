---
erzeugt: 765e341ed4a5
art: modul
tags: [modul]
---
> [!abstract] opencivil/stabwerk3d/__init__.py
> raeumliche Stabwerke nach der Steifigkeitsmethode.
> Paket [[opencivil]] · [Quelltext](../../opencivil/stabwerk3d/__init__.py)

Der Rechenkern der App «3D Balkensysteme»: ein Rahmen im Raum, gerechnet mit
Euler-Bernoulli-Staeben und Torsion nach St. Venant, Theorie 1. Ordnung --
wie [[opencivil.stabwerk]] in der Ebene, mit sechs Unbekannten je Knoten.
Heraus kommen Verschiebungen und Drehungen, Normalkraft, zwei Querkraefte,
Torsionsmoment, zwei Biegemomente und Lagerkraefte -- je Lastfall und je
Kombination.

* [[opencivil.stabwerk3d.modell|modell]] -- was gerechnet wird, in SI.
* [[opencivil.stabwerk3d.raum|raum]] -- Vektoren, Richtungen und Strecken.
* [[opencivil.stabwerk3d.stab|stab]] -- der einzelne Stab: seine Achsen, und
  wie er aus drei ebenen Staeben besteht.
* [[opencivil.stabwerk3d.system|system]] -- das ganze System: Unbekannte,
  Zusammenbau, Loesen, Lagerkraefte.
* [[opencivil.stabwerk3d.verlauf|verlauf]] -- Schnittgroessen und Biegelinien
  laengs jedes Stabs.

Was die Ebene schon kann, kommt von dort: das Gleichungssystem
([[opencivil.stabwerk.matrix]]), der ebene Stab mit Lasten und Bettung,
der Verlauf laengs eines Stabs. Nur die Standardbibliothek.

## Module

- [[opencivil.stabwerk3d.modell]] – was gerechnet wird: das raeumliche Stabwerk in SI.
- [[opencivil.stabwerk3d.raum]] – Vektoren, Richtungen und Strecken im Raum.
- [[opencivil.stabwerk3d.stab]] – der raeumliche Stab: drei ebene in einem.
- [[opencivil.stabwerk3d.system]] – das raeumliche Stabwerk: Unbekannte, Zusammenbau, Loesen.
- [[opencivil.stabwerk3d.verlauf]] – Schnittgroessen und Biegelinien laengs eines Stabs im Raum.
