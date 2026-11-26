---
erzeugt: bc693c1aab1b
art: formel
tags: [formel]
normstelle: "SIA 265:2012, 4.2.8.2, (30) und (31); 4.2.8.3"
---
> [!info] Normstelle
> SIA 265:2012, 4.2.8.2, (30) und (31); 4.2.8.3

*In der Herleitung: «Hilfswert um y, β\_c für Brettschichtholz aus Nadelholz»*

$$
k_y = 0.5 \cdot \left(1 + \beta_c \cdot \left(\lambda_{rel,y} - 0.3\right) + \lambda_{rel,y}^2\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\beta_c$ | Beiwert der Geradheit | – | Zwischenwert |
| $\lambda_{rel,y}$ | Relative Schlankheit beim Knicken | – | [[Relative Schlankheit beim Knicken von Holz]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  k_y &= 0.5 \cdot \left(1 + \beta_c \cdot \left(\lambda_{rel,y} - 0.3\right) + \lambda_{rel,y}^2\right) \\
  &= 0.5 \cdot \left(1 + 0.1 \cdot \left(0.557 - 0.3\right) + 0.557^2\right) \\
  &= 0.668
\end{aligned}
$$

## Gebraucht von

- [[Knickbeiwert des Holzes]]

## Im Code

- [[opencivil.nachweis.qa_holz_stabilitaet#_Herleitung|_Herleitung._knicken]]

## Themen

- [[Knicken und Kippen eines Holzstabs]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ein Zwischenwert der Knickkurve. $\beta_c$ sagt, wie gerade der Stab ist:
0.2 bei Vollholz, 0.1 bei Brettschichtholz, das gerader gefertigt wird.
Bis zur relativen Schlankheit 0.3 mindert nichts; siehe
[[Knickbeiwert des Holzes]].
