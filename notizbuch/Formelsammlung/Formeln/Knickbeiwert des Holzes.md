---
erzeugt: 0a6733b31c0a
art: formel
tags: [formel]
normstelle: "SIA 265:2012, 4.2.8.2, (30) und (31); 4.2.8.3"
---
> [!info] Normstelle
> SIA 265:2012, 4.2.8.2, (30) und (31); 4.2.8.3

*In der Herleitung: «Knickbeiwert um y»*

$$
k_{c,y} = \frac{1}{k_y + \sqrt{k_y^2 - \lambda_{rel,y}^2}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $k_y$ | Hilfswert beim Knicken | – | [[Hilfswert beim Knicken von Holz]] |
| $\lambda_{rel,y}$ | Relative Schlankheit beim Knicken | – | [[Relative Schlankheit beim Knicken von Holz]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
k_{c,y} = \frac{1}{k_y + \sqrt{k_y^2 - \lambda_{rel,y}^2}} = \frac{1}{0.668 + \sqrt{0.668^2 - 0.557^2}} = 0.965
$$

## Gebraucht von

- [[Knickwiderstand eines Holzstabs]]

## Im Code

- [[opencivil.nachweis.qa_holz_stabilitaet#_Herleitung|_Herleitung._knicken]]

## Themen

- [[Knicken und Kippen eines Holzstabs]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Anteil der Druckfestigkeit, den ein Stab mit seiner Schlankheit noch
erreicht – dieselbe Idee wie der
[[Abminderungsfaktor beim Knicken und Kippen]] beim Stahl. Gedrungene
Stäbe erreichen die volle Festigkeit, schlanke nähern sich der
[[Knicklast nach Euler]].
