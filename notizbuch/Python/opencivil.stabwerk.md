---
erzeugt: c9b5829e6a27
art: modul
tags: [modul]
---
> [!abstract] opencivil/stabwerk/__init__.py
> ebene Stabwerke nach der Steifigkeitsmethode.
> Paket [[opencivil]] · [Quelltext](../../opencivil/stabwerk/__init__.py)

Der Rechenkern der App «2D Balkensysteme»: ein ebener Rahmen, belastet in
seiner Ebene, gerechnet mit Euler-Bernoulli-Staeben nach Theorie 1. Ordnung.
Heraus kommen Verschiebungen, Normalkraft, Querkraft, Moment und
Lagerkraefte -- je Lastfall und je Kombination.

* [[opencivil.stabwerk.matrix|matrix]] -- das Gleichungssystem: im Profil
  gespeichert, umgekehrt nach Cuthill-McKee nummeriert, und was geschieht,
  wenn es singulaer ist.
* [[opencivil.stabwerk.stab|stab]] -- der einzelne Stab: Steifigkeit,
  arbeitsgleiche Lasten, Bettung.
* [[opencivil.stabwerk.modell|modell]] -- was gerechnet wird, in SI: Knoten,
  Staebe, Lager, Lasten.
* [[opencivil.stabwerk.system|system]] -- das ganze System: Unbekannte,
  Zusammenbau, Loesen, Lagerkraefte.
* [[opencivil.stabwerk.verlauf|verlauf]] -- Schnittgroessen und Biegelinie
  laengs jedes Stabs.

Nur die Standardbibliothek: das Werkzeug rechnet auch im Browser.

## Module

- [[opencivil.stabwerk.herleitung]] – wie ein Balkensystem seine Rechnung aufschreibt.
- [[opencivil.stabwerk.matrix]] – das Gleichungssystem eines Stabwerks.
- [[opencivil.stabwerk.modell]] – was gerechnet wird: das ebene Stabwerk in SI.
- [[opencivil.stabwerk.querschnitte]] – die Querschnitte der Staebe, nach Vorlage.
- [[opencivil.stabwerk.rechnung]] – das Balkensystem im Rechenwerk.
- [[opencivil.stabwerk.stab]] – der ebene Stab: Steifigkeit, Lasten, Bettung.
- [[opencivil.stabwerk.system]] – das ganze Stabwerk: Unbekannte, Zusammenbau, Loesen.
- [[opencivil.stabwerk.verlauf]] – Schnittgroessen und Biegelinie laengs eines Stabs.
