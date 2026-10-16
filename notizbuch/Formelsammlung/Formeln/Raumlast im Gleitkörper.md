---
erzeugt: 149c69889342
art: formel
tags: [formel]
normstelle: "Kap. 9.2.8"
---
> [!info] Normstelle
> Kap. 9.2.8

*In der Herleitung: «Raumlast im Gleitkörper, über dem Wasser»*

$$
\gamma_G = \gamma
$$

*In der Herleitung: «Raumlast im Gleitkörper, unter Wasser»*

$$
\gamma_G = \gamma'
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\gamma$ | Raumlast des Bodens | kN/m³ | Vorgabe |
| $\gamma'$ | Raumlast des Bodens unter Auftrieb | kN/m³ | [[Raumlast unter Auftrieb]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\gamma_G = \gamma = 21\,\mathrm{kN}/\mathrm{m}^{3}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\gamma_G = \gamma' = 11\,\mathrm{kN}/\mathrm{m}^{3}
$$

## Gebraucht von

- [[Bruchspannung in der Sohle]]

## Im Code

- [[opencivil.geotechnik.grundbruch#Grundbruch._grundwasser|Grundbruch._grundwasser]]

## Themen

- [[Grundbruch]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Raumlast, mit der das Gewicht des Gleitkörpers zählt: $\gamma'$, wenn
Wasser in ihm steht oder über ihm, sonst $\gamma$.

Liegt der Spiegel unter der Sohle, aber höher als die
[[Tiefe des Gleitkörpers]], rechnet das Werkzeug mit $\gamma'$ wie in
Lage 2 -- auf der sicheren Seite.
