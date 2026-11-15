---
erzeugt: c7ee82479b53
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Schnittgrössen in den Achsen des Stabs»*

$$
\sigma = \frac{N}{A} + \frac{M_y \cdot z}{I_y} + \frac{M_z \cdot y}{I_z} \qquad V_z = \frac{\mathrm{d}M_y}{\mathrm{d}x} \qquad V_y = \frac{\mathrm{d}M_z}{\mathrm{d}x}
$$

## Im Code

- [[opencivil.stabwerk3d.herleitung|_ansaetze]]

## Themen

- [[Steifigkeitsmethode]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Vorzeichen der sechs Schnittgrössen, in den Achsen des Stabs. $N$ ist
positiv als Zug. $M_y$ zieht an der Faser auf der Seite $+z$, $M_z$ an der
auf der Seite $+y$; darum stehen in der Spannung eines Punkts $(y, z)$ alle
drei Glieder mit Pluszeichen. Bei einem waagrechten Stab mit $\beta = 0$ zieht
ein positives $M_y$ unten, wie das Moment des 2D-Balkensystems an der
gestrichelten Faser.

Die Querkräfte sind die Ableitungen der Momente, solange kein verteiltes
Moment auf dem Stab liegt: $V_z$ gehört zu $M_y$, $V_y$ zu $M_z$. Das
Torsionsmoment $T$ ist positiv, wenn sein Vektor am Schnittufer nach aussen
zeigt -- wie der Zug bei $N$.

Nach der Rechtsschraube hätte $M_z$ das andere Vorzeichen; welches bleiben
soll, steht in [[TODO]].
