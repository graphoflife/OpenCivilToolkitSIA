---
erzeugt: fc2d54e23b6e
art: formel
tags: [formel]
normstelle: "SIA 264:2014, 5.1.2.2, Figur 1"
---
> [!info] Normstelle
> SIA 264:2014, 5.1.2.2, Figur 1

*In der Herleitung: «Abminderung für S420 und S460, x\_p/h über 0.15»*

$$
\beta = 1 - 0.15 \cdot \frac{x_p / h - 0.15}{0.4 - 0.15}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $x_p$ | Abstand der Nulllinie vom gedrückten Rand des Betons | mm | Zwischenwert |
| $h$ | Höhe des Querschnitts quer zur Nulllinie | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\beta = 1 - 0.15 \cdot \frac{x_p / h - 0.15}{0.4 - 0.15} = 1 - 0.15 \cdot \frac{125.3\,\mathrm{mm} / 410\,\mathrm{mm} - 0.15}{0.4 - 0.15} = 0.907
$$

## Gebraucht von

- [[Plastischer Biegewiderstand mit β]]

## Im Code

- [[opencivil.nachweis.qa_verbund_werte#beta|beta]]

## Themen

- [[Kennzahlen]]
- [[Verbundquerschnitt]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Plastisch zu rechnen setzt voraus, dass der Stahl weit fliesst, bevor der
Beton am gedrückten Rand versagt. S420 und S460 fliessen erst bei einer
grösseren Dehnung; liegt die Nulllinie tief, erreicht der Beton seine
Grenze, bevor der Stahl auf der Zugseite ganz fliesst. Darum mindert β
den plastischen Biegewiderstand, sobald die Druckzone $x_p$ mehr als 15 %
der Höhe $h$ misst: geradlinig von 1 bei $x_p/h = 0.15$ bis 0.85 bei 0.4.

Über 0.4 endet die Figur. Dort rechnet das Werkzeug den Biegewiderstand
nicht, und der Fall bleibt grau (nach Vorgabe). $x_p$ misst es senkrecht
zur Nulllinie, vom gedrücktesten Punkt des Betons bis zu ihr, $h$ quer zu
ihr über den ganzen Querschnitt – auch bei schiefer Biegung und bei
negativem Moment, wo der gedrückte Beton zwischen den Flanschen liegt
(nach Vorgabe: die Figur zeigt den Träger mit gedrückter Platte).

Mit S235 bis S355 ist β = 1, und die Formel steht nicht in der Herleitung.
