---
erzeugt: 90fe9dc13446
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
N = \int_A \sigma\,\mathrm{d}A \qquad M = \int_A \sigma \cdot \left(z - \tfrac{h}{2}\right)\,\mathrm{d}A
$$

## Im Code

- [[opencivil.nachweis.resistenzlinie#Ebenenlinie.protokoll_ansatz|Ebenenlinie.protokoll_ansatz]]

## Themen

- [[Biegung und Normalkraft]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Zu einer Dehnungsebene gehört über die Werkstoffgesetze eine Spannung an
jeder Stelle des Querschnitts. Ihre Summe ist die Normalkraft, ihre Summe mal
dem Abstand zur halben Höhe das Moment. Das Werkzeug teilt den Beton dafür in
200 Fasern über die Höhe und zählt den Stahl Lage für Lage -- an der Stelle
einer Lage zählt der Stahl statt des Betons.

So entsteht jeder Punkt der Linie aus Dehnungsebenen: Ebene wählen,
Spannungen bestimmen, integrieren. Wo die Ebenen liegen dürfen, sagt der
Dehnungsfächer (siehe [[opencivil.nachweis.dehnungsfaecher]]).
