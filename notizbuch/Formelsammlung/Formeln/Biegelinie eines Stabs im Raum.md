---
erzeugt: e5e5bb93e417
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Biegelinien, Längsverschiebung und Verdrillung»*

$$
w'' = -\frac{M_y}{EI_y} \qquad v'' = -\frac{M_z}{EI_z} \qquad u' = \frac{N}{EA} \qquad \theta_x' = \frac{T}{GI_T}
$$

## Im Code

- [[opencivil.stabwerk3d.herleitung|_ansaetze]]

## Themen

- [[Steifigkeitsmethode]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Vier Differentialgleichungen, die nichts voneinander wissen: die Biegelinie
$w$ in der Ebene $x$-$z$ mit $M_y$, die Biegelinie $v$ in der Ebene $x$-$y$
mit $M_z$, die Längsverschiebung $u$ mit $N$ und die Verdrillung $\theta_x$
mit dem Torsionsmoment $T$. Jede ist die des ebenen Stabs
([[Steifigkeitsmatrix eines Stabs]]). Getrennt gelten sie, wenn $y$ und $z$
die Hauptachsen des Querschnitts sind und die Last durch den
Schubmittelpunkt geht.

Ein positives Moment zieht an der Faser auf der positiven Seite seiner
Achse, und der Stab biegt sich zu dieser Seite hin durch: daher das
Minuszeichen. Ohne Schubverformung und nach Theorie 1. Ordnung, wie in der
Ebene. Die Verdrillung folgt St. Venant allein; die Wölbkrafttorsion, die
ein I-Profil mit gehaltenen Enden steifer macht, fehlt ([[TODO]]).
