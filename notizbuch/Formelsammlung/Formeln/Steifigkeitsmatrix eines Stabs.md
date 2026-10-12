---
erzeugt: 828fef2740a8
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Steifigkeitsmatrix eines Stabs, in seinen Achsen»*

$$
\mathbf{k} = \begin{bmatrix} \frac{EA}{L} & 0 & 0 & -\frac{EA}{L} & 0 & 0 \\ 0 & \frac{12EI}{L^3} & \frac{6EI}{L^2} & 0 & -\frac{12EI}{L^3} & \frac{6EI}{L^2} \\ 0 & \frac{6EI}{L^2} & \frac{4EI}{L} & 0 & -\frac{6EI}{L^2} & \frac{2EI}{L} \\ -\frac{EA}{L} & 0 & 0 & \frac{EA}{L} & 0 & 0 \\ 0 & -\frac{12EI}{L^3} & -\frac{6EI}{L^2} & 0 & \frac{12EI}{L^3} & -\frac{6EI}{L^2} \\ 0 & \frac{6EI}{L^2} & \frac{2EI}{L} & 0 & -\frac{6EI}{L^2} & \frac{4EI}{L} \end{bmatrix}
$$

## Im Code

- [[opencivil.stabwerk.herleitung|_ansaetze]]

## Themen

- [[Steifigkeitsmethode]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Kräfte an den Enden eines geraden Stabs, wenn diese sich verschieben und
drehen: $\mathbf{s} = \mathbf{k} \cdot \mathbf{d}$, je Ende die
Längsverschiebung $u$, die Querverschiebung $v$ und die Drehung $\theta$, in
den Achsen des Stabs.

Die Zeilen in Längsrichtung sind die einer Feder $EA/L$. Die übrigen kommen
aus der Biegelinie nach Euler-Bernoulli, ohne Schubverformung: mit
kubischen Formfunktionen, die für einen Stab ohne Last zwischen den Enden
genau sind. Theorie 1. Ordnung -- die Normalkraft ändert die
Biegesteifigkeit nicht.
