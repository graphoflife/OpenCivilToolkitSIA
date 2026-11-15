"""
opencivil/stabwerk -- Stabwerke nach der Steifigkeitsmethode, eben und im Raum.

Der Rechenkern der Apps «2D Balkensysteme» und «3D Balkensysteme»: ein
Rahmen in der Ebene oder im Raum, gerechnet mit Euler-Bernoulli-Staeben --
im Raum dazu Torsion nach St. Venant -- nach Theorie 1. Ordnung. Heraus
kommen Verschiebungen und Drehungen, Schnittgroessen und Lagerkraefte, je
Lastfall und je Kombination. Ein ebenes System rechnet derselbe Kern wie
eines im Raum: als System im Raum, das in seiner x-z-Ebene liegt.

* :mod:`~opencivil.stabwerk.matrix` -- das Gleichungssystem: im Profil
  gespeichert, umgekehrt nach Cuthill-McKee nummeriert, und was geschieht,
  wenn es singulaer ist.
* :mod:`~opencivil.stabwerk.stab` -- der ebene Stab: Steifigkeit,
  arbeitsgleiche Lasten, Bettung. Ein Stab im Raum besteht aus drei solchen
  (:mod:`opencivil.stabwerk3d.stab`).
* :mod:`~opencivil.stabwerk.modell` -- was in der Ebene gerechnet wird, in
  SI: Knoten, Staebe, Lager, Lasten. Im Raum :mod:`opencivil.stabwerk3d.modell`.
* :mod:`~opencivil.stabwerk.art` -- eben oder im Raum: was die beiden
  unterscheidet, und wie ein ebenes System eines im Raum wird.
* :mod:`~opencivil.stabwerk.system` -- das ganze System, eben oder im Raum:
  Unbekannte, Zusammenbau, Loesen, Lagerkraefte.
* :mod:`~opencivil.stabwerk.verlauf` -- Schnittgroessen und Biegelinien
  laengs jedes Stabs.

Nur die Standardbibliothek: das Werkzeug rechnet auch im Browser.
"""
