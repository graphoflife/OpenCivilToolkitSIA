---
erzeugt: a4f82ab4567f
art: formel
tags: [formel]
normstelle: "Kap. 9.2.14"
---
> [!info] Normstelle
> Kap. 9.2.14

$$
\delta_R = \arctan\frac{T_{Ed}}{N_{Ed}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $T_{Ed}$ | Einwirkung in der Sohle | kN | Zwischenwert |
| $N_{Ed}$ | Einwirkung normal zur Sohle | kN | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\delta_R = \arctan\frac{T_{Ed}}{N_{Ed}} = \arctan\frac{150\,\mathrm{kN}}{1500\,\mathrm{kN}} = 5.7{}^{\circ}
$$

## Im Code

- [[opencivil.geotechnik.grundbruch#Grundbruch|Grundbruch._drainierter_fall]]

## Themen

- [[Grundbruch]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie weit die Resultierende $R$ gegen die Normale der Sohle geneigt ist
(Bild 9.2.15). Eine geneigte Last schiebt den Gleitkörper zur Seite, zu der
$T$ zeigt, und verkleinert ihn; die Lastneigungsfaktoren nehmen das auf.

$\delta_R$ steht in der Herleitung zur Übersicht. Die Faktoren rechnen mit
$T$ und $N$ selbst, weil im Nenner auch die Kohäsion steht.
