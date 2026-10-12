---
erzeugt: 8d59a02ca1f8
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Arbeitsgleiche Knotenkräfte der Lasten auf einem Stab»*

$$
f_i = \int_0^L N_i(x) \cdot p(x)\,\mathrm{d}x + \int_0^L N_i'(x) \cdot m(x)\,\mathrm{d}x + \sum_j N_i(a_j) \cdot P_j + \sum_j N_i'(a_j) \cdot M_j
$$

## Im Code

- [[opencivil.stabwerk.herleitung|_ansaetze]]

## Themen

- [[Steifigkeitsmethode]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Eine Last zwischen den Enden eines Stabs wird durch Kräfte an seinen Enden
ersetzt, die bei jeder Verschiebung der Enden dieselbe Arbeit leisten wie die
Last selbst: man gewichtet sie mit den Formfunktionen $N_i$, ein verteiltes
oder einzelnes Moment mit deren Ableitung $N_i'$. Für eine Gleichlast $q$
gibt das die bekannten Einspannkräfte $qL/2$ und -momente $qL^2/12$.

Integriert wird mit drei Gauss-Punkten je Strecke, für lineare Lasten genau.
Die Verläufe zwischen den Enden rechnet danach
[[Schnittgrössen längs eines Stabs]] mit der Last selbst, nicht mit diesen
Ersatzkräften.
