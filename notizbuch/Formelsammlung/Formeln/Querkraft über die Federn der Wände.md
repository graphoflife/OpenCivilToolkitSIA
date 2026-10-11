---
erzeugt: 9ddb59470a39
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
k_i = b_{w,i} \cdot l_i \qquad \sum_i k_i\, e_i e_i^T\, u = V \qquad V_i = k_i\, e_i \cdot u \qquad \Delta T = \sum_i V_i\, r_i
$$

## Im Code

- [[opencivil.nachweis.schubwandnachweis#Schubwandnachweis|Schubwandnachweis._protokoll_ansatz]]

## Themen

- [[Querkraft und Torsion]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das Federmodell: jede Wand $i$ trägt nur entlang ihrer Achse $e_i$, mit einer
Steifigkeit proportional zu ihrer Dicke mal Länge, $k_i = b_{w,i} \cdot l_i$.
Verschiebt sich der Querschnitt um $u$, nimmt jede Wand die Kraft
$k_i\, e_i \cdot u$ auf. Die Verschiebung ist die, bei der die Summe aller
Wandkräfte die Querkraft $V$ ergibt -- ein lineares Gleichungssystem mit zwei
Unbekannten.

Steife, lange Wände ziehen mehr Kraft an. Nach Vorgabe eingebaut, nicht
nachgeschlagen.
