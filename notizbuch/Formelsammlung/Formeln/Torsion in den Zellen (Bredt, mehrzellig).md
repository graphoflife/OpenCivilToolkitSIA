---
erzeugt: cd363518cb9a
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.5.2, (55), Figur 20"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.5.2, (55), Figur 20

$$
T - \Delta T = \sum_k 2 A_k\, q_k \qquad \oint_k \frac{q}{b_w}\, \mathrm{d}s = 2 A_k\, \theta
$$

## Im Code

- [[opencivil.nachweis.schubwandnachweis#Schubwandnachweis|Schubwandnachweis._protokoll_ansatz]]

## Themen

- [[Querkraft und Torsion]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Eine geschlossene Zelle trägt Torsion als Schubfluss $q$, der ringsum läuft:
das Moment ist $2 A_k\,q$, mit $A_k$ der umschlossenen Fläche (Bredt). Die
Norm misst $A_k$ bis zu den Längsstäben in den Ecken (SIA 262, 4.3.5.2):
die Wandachsen gehören darum durch die Eckstäbe. Bei mehreren Zellen teilt sich die Torsion so auf, dass sich alle
Zellen gleich verdrillen -- die zweite Gleichung, das Ringintegral, sagt das
für jede Zelle. Wände zwischen zwei Zellen tragen die Differenz beider
Schubflüsse.

Die Norm behandelt die einzelne Zelle. Die Aufteilung auf mehrere Zellen
ist nach Vorgabe eingebaut; in SIA 262:2025 steht sie nicht.
