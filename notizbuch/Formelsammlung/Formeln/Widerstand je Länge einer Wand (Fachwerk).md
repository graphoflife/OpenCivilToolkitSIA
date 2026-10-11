---
erzeugt: dd696c368dda
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.3.4"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.3.4

$$
v_{Rd,s} = \frac{A_{sw}}{s}\, f_{sd} \cot\alpha \qquad v_{Rd,c} = b_w\, k_c\, f_{cd} \sin\alpha \cos\alpha \qquad v_{Rd} = \max_\alpha \min(v_{Rd,s};\ v_{Rd,c})
$$

## Im Code

- [[opencivil.nachweis.schubwandnachweis#Schubwandnachweis|Schubwandnachweis._protokoll_ansatz]]

## Themen

- [[Querkraft und Torsion]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Dasselbe Fachwerk wie bei der Platte (siehe
[[Querkraftwiderstand mit Querkraftbewehrung]]), je Länge der Wand
geschrieben: die Bügel mit $A_{sw}/s \cdot f_{sd} \cot\alpha$, die
Druckdiagonalen mit $b_w\, k_c f_{cd} \sin\alpha\cos\alpha$. Die Neigung wird
so gewählt, dass das Kleinere der beiden am grössten ist.
