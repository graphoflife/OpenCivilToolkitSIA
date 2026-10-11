---
erzeugt: 231244a1a16e
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
I_y = \frac{1}{12} \sum_i (z_i^2 + z_i z_{i+1} + z_{i+1}^2)\, c_i - A\, z_S^2\qquad I_z = \frac{1}{12} \sum_i (y_i^2 + y_i y_{i+1} + y_{i+1}^2)\, c_i - A\, y_S^2
$$

## Im Code

- [[opencivil.querschnitt.analyse#Querschnittsanalyse.aufbau_protokollieren|Querschnittsanalyse.aufbau_protokollieren]]

## Themen

- [[Querschnittsanalyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Dieselbe Idee wie bei der Fläche: das Flächenmoment zweiten Grades als Summe
über die Kanten, erst bezogen auf den Ursprung. Der Satz von Steiner rückt es
dann auf den Schwerpunkt: $I = I_0 - A \cdot e^2$. Für schiefe Biegung und
unsymmetrische Querschnitte kommt das Deviationsmoment $I_{yz}$ auf dieselbe
Weise dazu.
