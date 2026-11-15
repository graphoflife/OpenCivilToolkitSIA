---
erzeugt: e6de088ae04b
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Flächenträgheitsmoment um z, «Rundrohr» (ROR 219.1 x 8, um z, die schwache Achse)»*

$$
I_{z} = I_{y}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $I_{y}$ | Flächenträgheitsmoment um y, Rundrohr | cm⁴ | [[Flächenträgheitsmoment eines Kreisrings]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
I_{z,\text{Q20}} = I_{y,\text{Q20}} = 2959.63\,\mathrm{cm}^{4}
$$

## Im Code

- [[opencivil.stabwerk.querschnitte#_wie_um_y|_wie_um_y]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ein Kreisring hat keine starke und keine schwache Achse: um jede Achse
durch die Mitte ist das Trägheitsmoment dasselbe. Darum ist $I_z = I_y$,
und $I_y$ rechnet wie beim [[Flächenträgheitsmoment eines Kreisrings]].
Das Rundrohr der Stahlprofile (ROR) ist ein solcher Kreisring und
rechnet ebenso, nur in cm⁴.
