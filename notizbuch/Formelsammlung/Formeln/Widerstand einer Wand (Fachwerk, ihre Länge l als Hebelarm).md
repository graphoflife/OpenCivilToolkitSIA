---
erzeugt: f34e922945fe
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.3.4.3, (45); 4.3.3.4.6, (47)"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.3.4.3, (45); 4.3.3.4.6, (47)

$$
V_{Rd,s} = \frac{A_{sw}}{s}\, l\, f_{yd} \cot\alpha \qquad V_{Rd,c} = b_w\, l\, k_c\, f_{cd} \sin\alpha \cos\alpha \qquad V_{Rd} = \max_\alpha \min(V_{Rd,s};\ V_{Rd,c})
$$

## Im Code

- [[opencivil.nachweis.schubwandnachweis#Schubwandnachweis|Schubwandnachweis._protokoll_ansatz]]

## Themen

- [[Querkraft und Torsion]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Dasselbe Fachwerk wie bei der Platte (siehe
[[Querkraftwiderstand mit Querkraftbewehrung]]), mit der Länge $l$ der
Wand als Hebelarm: die Bügel mit $A_{sw}/s \cdot l \cdot f_{yd} \cot\alpha$,
die Druckdiagonalen mit $b_w\, l\, k_c f_{cd} \sin\alpha\cos\alpha$. Bis
2026-11-18 stand es je Länge der Wand, ohne $l$. Die Neigung wird
so gewählt, dass das Kleinere der beiden am grössten ist.
