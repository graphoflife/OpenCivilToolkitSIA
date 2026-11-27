---
erzeugt: cd30acf08b36
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Torsionsträgheitsmoment, «Rundrohr» (ROR 219.1 x 8)»*

$$
I_{T} = 2 \cdot I_{y}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $I_{y}$ | Flächenträgheitsmoment um y, Rundrohr | cm⁴ | [[Flächenträgheitsmoment eines Kreisrings]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
I_{T,\text{Q6}} = 2 \cdot I_{y,\text{Q6}} = 2 \cdot 2959.63\,\mathrm{cm}^{4} = 5919.27\,\mathrm{cm}^{4}
$$

## Im Code

- [[opencivil.stabwerk.querschnitte#_wie_um_y|_wie_um_y]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ein Kreisring unter Torsion verwölbt sich nicht: jeder Querschnitt bleibt
eben und dreht sich als Ganzes, und der Schub wächst linear mit dem Abstand
von der Mitte. Darum ist $I_T$ hier genau das polare Trägheitsmoment, die Summe der
beiden Flächenträgheitsmomente: $I_T = I_y + I_z = 2\,I_y$ – mit $I_y$ aus
dem [[Flächenträgheitsmoment eines Kreisrings]] und $I_z$ wie beim
[[Flächenträgheitsmoment eines Kreisrings um z]].

Bei jeder anderen Form verwölbt sich der Querschnitt, und $I_T$ ist kleiner
als das polare Trägheitsmoment: beim Quadrat um 16 %, beim schmalen
Rechteck um ein Vielfaches ([[Torsionsträgheitsmoment eines Rechtecks]]).
Das Rundrohr der Stahlprofile (ROR) ist ein solcher Kreisring und rechnet
ebenso.
