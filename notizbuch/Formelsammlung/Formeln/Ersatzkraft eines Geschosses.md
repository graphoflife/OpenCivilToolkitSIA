---
erzeugt: 2f5a6996f70d
art: formel
tags: [formel]
normstelle: "SIA 261:2020, 16.5.2.5, (42)"
---
> [!info] Normstelle
> SIA 261:2020, 16.5.2.5, (42)

*In der Herleitung: «Verteilung auf die Geschosse»*

$$
F_{d,i} = \frac{z_i \cdot W_i}{\sum_j z_j \cdot W_j} \cdot F_d
$$

## Im Code

- [[opencivil.erdbeben.ersatzkraft#Lauf._kraefte|Lauf._kraefte]]

## Themen

- [[Erdbeben]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Verteilt wird nach $z_i \cdot W_i$: je höher und schwerer ein Geschoss,
desto mehr Kraft. Dahinter steht eine erste Schwingungsform, die gerade mit
der Höhe wächst -- und die Annahme, dass höhere Formen wenig beitragen
(16.5.2.1). Die Kräfte zusammen ergeben wieder $F_d$; unter jedem Geschoss
wirkt als Querkraft die Summe der Kräfte darüber, am Fuss die ganze
[[Ersatzkraft]].

Die Wände teilen sich jede Kraft nach ihrem Anteil an der
[[Biegesteifigkeit der Wände|Biegesteifigkeit]] -- nach Vorgabe, nicht
nachgeschlagen. Die Torsion aus einer Exzentrizität der Massen (16.5.2.7)
gehört dazu und wird nicht gerechnet.
