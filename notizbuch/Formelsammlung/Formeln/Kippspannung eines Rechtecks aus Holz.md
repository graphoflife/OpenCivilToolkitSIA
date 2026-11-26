---
erzeugt: 5dbbed828466
art: formel
tags: [formel]
normstelle: "SIA 265:2012, 4.2.9.3, (40) und (41)"
---
> [!info] Normstelle
> SIA 265:2012, 4.2.9.3, (40) und (41)

*In der Herleitung: «Kippspannung des Rechtecks, Biegung um y»*

$$
\sigma_{m,crit} = \frac{0.75 \cdot E_{0,05} \cdot b^2}{a \cdot h}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $E_{0,05}$ | Elastizitätsmodul in Faserrichtung, 5%-Fraktil | N/mm² | Vorgabe |
| $b$ | Breite des Rechtecks | mm | Zwischenwert |
| $a$ | Abstand der seitlichen Halterungen | mm | Zwischenwert |
| $h$ | Höhe des Rechtecks | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\sigma_{m,crit} = \frac{0.75 \cdot E_{0,05} \cdot b^2}{a \cdot h} = \frac{0.75 \cdot 9400\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(160\,\mathrm{mm}\right)^2}{4000\,\mathrm{mm} \cdot 400\,\mathrm{mm}} = 112.8\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Gebraucht von

- [[Relative Schlankheit beim Kippen von Holz]]

## Im Code

- [[opencivil.nachweis.qa_holz_stabilitaet#_Herleitung|_Herleitung._kippen]]

## Themen

- [[Knicken und Kippen eines Holzstabs]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Biegespannung, bei der ein Rechteck $b \times h$ zwischen seitlichen
Halterungen im Abstand $a$ seitlich ausweicht. Sie wächst mit dem Quadrat
der Breite und fällt mit Höhe und Abstand. Mit $E_{0,05}$, dem
5%-Fraktil des Elastizitätsmoduls: die Stabilität hängt an der
Steifigkeit, und die streut.
