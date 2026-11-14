---
erzeugt: cba2d0928e56
art: formel
tags: [formel]
normstelle: "Kap. 12.5"
---
> [!info] Normstelle
> Kap. 12.5

*In der Herleitung: «Wirksame Spannung aus dem Gewicht des Bodens darüber»*

$$
\sigma'_v(z) = \sum \gamma_i \, t_i - u(z) \qquad u(z) = \gamma_w \cdot \max\left(0;\ z - t_w\right)
$$

## Im Code

- [[opencivil.pfahl.aussen#AeussererWiderstand._mantel|AeussererWiderstand._mantel]]

## Themen

- [[Äusserer Pfahlwiderstand]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die senkrechte Spannung im Korngerüst in der Tiefe z: das Gewicht des Bodens
darüber, weniger dem Druck des Porenwassers. Über dem Grundwasserspiegel
zählt die volle Raumlast γ, darunter bleibt γ − γ_w. Bei γ = 20 kN/m³ und
dem Wasser 4 m unter Terrain sind es in 8 m Tiefe 4 · 20 + 4 · 10 =
120 kN/m².

Für die Reibung am Mantel zählt die Spannung in der Mitte jedes Stücks. Ein
Stück liegt ganz in einer Schicht und ganz auf einer Seite des Wassers; darin
verläuft die Spannung linear, und ihr Wert in der Mitte ist ihr Mittel. Das
Buch nimmt die Spannung auf halber Einbindetiefe (Kap. 12.5) -- dasselbe,
solange kein Wasserspiegel die Schicht teilt.
