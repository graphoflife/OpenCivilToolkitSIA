---
erzeugt: d10fd6b7cf2e
art: formel
tags: [formel]
normstelle: "Kap. 10.8"
---
> [!info] Normstelle
> Kap. 10.8

*In der Herleitung: «Erdwiderstand je Meter Pfahl: vor dem schmalen Pfahl auf der dreifachen Breite»*

$$
p_{E,k} = b' \cdot \left(e_p - \max\left(0;\ e_a\right)\right) \qquad b' = 3 \cdot D
$$

## Im Code

- [[opencivil.pfahl.quer#AeussererQuerwiderstand._erdwiderstand|AeussererQuerwiderstand._erdwiderstand]]

## Themen

- [[Äusserer Pfahlwiderstand quer]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Vor einer schmalen Druckfläche bricht der Boden nicht nur auf deren Breite:
der Bruchkörper greift seitlich aus. Das Buch nimmt grob die dreifache
Breite an (Kap. 10.8). Hier gilt sie für beide Seiten, vorne passiv, hinten
aktiv: je Meter Pfahl p_E,k = 3 · D · (e_p − max(0; e_a)) -- nach Vorgabe,
nicht nachgeschlagen.

⌀ 900 mm im trockenen Kies mit φ'_k = 35°, in 5 m Tiefe:
3 · 0.9 m · (369 − 27) kPa = 923 kN/m. Undrainiert hebt sich σ_v vorne und
hinten auf, sobald e_a positiv ist; dann bleibt 3 · D · 4 · s_u = 12 · s_u · D,
für ⌀ 1200 mm in s_u,k = 25 kPa also 360 kN/m.

Genauer rechnet das Buch nach Weissenbach (Kap. 10.8, Tabelle 10.21): mit
einem räumlichen Gleitkeil und Reibung am Träger, und mit einer Abminderung,
wo die Fläche schmaler ist als etwa 0.3-mal ihre Tiefe. Die dreifache
Breite ohne Wandreibung bleibt darunter: ⌀ 900 mm in Kies mit φ'_k = 35°
gibt bis 6 m Tiefe 43 % der Kraft nach Weissenbach -- offen in [[TODO]].
Auf den passiven Druck gehört nach demselben Kapitel ein Faktor von
mindestens 2, damit die Verformungen klein bleiben; η_a,tr / γ_M,a =
0.7 / 1.4 gibt genau ihn.

In die Brüche geht p_E,k charakteristisch ein
([[Querbruch am frei drehbaren Kopf]]), gegen die Bettungskraft als
Bemessungswert ([[Bemessungswert des Erdwiderstands am Pfahl]]).
