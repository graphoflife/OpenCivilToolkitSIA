---
erzeugt: 6c83e05e883b
art: formel
tags: [formel]
normstelle: ["SIA 263:2013, 4.5.1.4", "SIA 263:2013, 4.5.1.3; 5.3.8"]
---
> [!info] Normstellen
> SIA 263:2013, 4.5.1.4 · SIA 263:2013, 4.5.1.3; 5.3.8

*In der Herleitung: «Schlankheit um y»*

$$
\bar{\lambda}_{K,y} = \sqrt{\frac{f_{y} \cdot A}{N_{cr,y}}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $f_{y}$ | Streckgrenze | N/mm² | Vorgabe |
| $A$ | Fläche des Bruttoquerschnitts | mm² | Zwischenwert |
| $N_{cr,y}$ | Ideale Knicklast | kN | [[Knicklast nach Euler]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\bar{\lambda}_{K,y} = \sqrt{\frac{f_{y,\text{S355}} \cdot A}{N_{cr,y}}} = \sqrt{\frac{355\,\mathrm{N}/\mathrm{mm}^{2} \cdot 15604\,\mathrm{mm}^{2}}{53037\,\mathrm{kN}}} = 0.323
$$

## Gebraucht von

- [[Abminderungsfaktor beim Knicken und Kippen]]
- [[Beiwert Φ beim Knicken]]

## Im Code

- [[opencivil.nachweis.qa_stahl_stabilitaet#_Herleitung.knicken|_Herleitung.knicken]]

## Themen

- [[Knicken und Kippen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die bezogene Schlankheit vergleicht, was der Querschnitt trägt, mit dem,
was der Stab als Ganzes trägt: die Wurzel aus der Fliesslast durch die
[[Knicklast nach Euler]]. Bei eins sind beide gleich – dort fehlt dem
wirklichen Stab am meisten. Gerechnet mit $f_y$, ohne $\gamma_{M1}$; in
Klasse 4 mit der wirksamen Fläche (5.3.8). Mit mehreren Baustählen
steht die Summe $\sum f_y A$ unter der Wurzel.
