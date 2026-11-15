---
erzeugt: 6370cc02a37d
art: modul
tags: [modul]
---
> [!abstract] opencivil/stabwerk/__init__.py
> Stabwerke nach der Steifigkeitsmethode, eben und im Raum.
> Paket [[opencivil]] · [Quelltext](../../opencivil/stabwerk/__init__.py)

Der Rechenkern der Apps «2D Balkensysteme» und «3D Balkensysteme»: ein
Rahmen in der Ebene oder im Raum, gerechnet mit Euler-Bernoulli-Staeben --
im Raum dazu Torsion nach St. Venant -- nach Theorie 1. Ordnung. Heraus
kommen Verschiebungen und Drehungen, Schnittgroessen und Lagerkraefte, je
Lastfall und je Kombination. Ein ebenes System rechnet derselbe Kern wie
eines im Raum: als System im Raum, das in seiner x-z-Ebene liegt.

* [[opencivil.stabwerk.matrix|matrix]] -- das Gleichungssystem: im Profil
  gespeichert, umgekehrt nach Cuthill-McKee nummeriert, und was geschieht,
  wenn es singulaer ist.
* [[opencivil.stabwerk.stab|stab]] -- der ebene Stab: Steifigkeit,
  arbeitsgleiche Lasten, Bettung. Ein Stab im Raum besteht aus drei solchen
  ([[opencivil.stabwerk3d.stab]]).
* [[opencivil.stabwerk.modell|modell]] -- was in der Ebene gerechnet wird, in
  SI: Knoten, Staebe, Lager, Lasten. Im Raum [[opencivil.stabwerk3d.modell]].
* [[opencivil.stabwerk.art|art]] -- eben oder im Raum: was die beiden
  unterscheidet, und wie ein ebenes System eines im Raum wird.
* [[opencivil.stabwerk.system|system]] -- das ganze System, eben oder im Raum:
  Unbekannte, Zusammenbau, Loesen, Lagerkraefte.
* [[opencivil.stabwerk.verlauf|verlauf]] -- Schnittgroessen und Biegelinien
  laengs jedes Stabs.

Nur die Standardbibliothek: das Werkzeug rechnet auch im Browser.

## Module

- [[opencivil.stabwerk.art]] – eben oder im Raum: was die beiden Balkensysteme unterscheidet.
- [[opencivil.stabwerk.herleitung]] – wie ein Balkensystem seine Rechnung aufschreibt.
- [[opencivil.stabwerk.matrix]] – das Gleichungssystem eines Stabwerks.
- [[opencivil.stabwerk.modell]] – was gerechnet wird: das ebene Stabwerk in SI.
- [[opencivil.stabwerk.profilformen]] – die Formen der Stahlprofile, mit ihren Formeln.
- [[opencivil.stabwerk.profiltabelle]] – welche Stahlprofile es gibt, mit ihren Massen.
- [[opencivil.stabwerk.querschnitte]] – die Querschnitte der Staebe, nach Vorlage.
- [[opencivil.stabwerk.rechnung]] – das Balkensystem im Rechenwerk.
- [[opencivil.stabwerk.stab]] – der ebene Stab: Steifigkeit, Lasten, Bettung.
- [[opencivil.stabwerk.stabquerschnitt]] – woher A und I eines Stabs kommen.
- [[opencivil.stabwerk.system]] – das Stabwerk, eben und im Raum: Unbekannte, Zusammenbau, Loesen.
- [[opencivil.stabwerk.verlauf]] – Schnittgroessen und Biegelinien laengs eines Stabs, eben und im Raum.
