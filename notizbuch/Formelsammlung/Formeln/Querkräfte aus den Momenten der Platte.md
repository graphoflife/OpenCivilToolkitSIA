---
erzeugt: 7e8b46ec2d5b
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Die Querkräfte aus dem Gefälle der Momente»*

$$
v_x = \frac{\partial m_x}{\partial x} + \frac{\partial m_{xy}}{\partial y} \qquad v_y = \frac{\partial m_{xy}}{\partial x} + \frac{\partial m_y}{\partial y} \qquad v_0 = \sqrt{v_x^2 + v_y^2}
$$

## Im Code

- [[opencivil.decke.fem.herleitung#_ansaetze|_ansaetze]]

## Themen

- [[FEM der Decke]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Im Gleichgewicht eines kleinen Stücks der Platte sind die Querkräfte das
Gefälle der Momente: $v_x$ ist, wie schnell $m_x$ in x und $m_{xy}$ in y
zunehmen, $v_y$ ebenso in der anderen Richtung. $v_0$ ist ihr Betrag, die
Querkraft in der Richtung, in der sie am grössten ist – sie zählt für den
Nachweis der Querkraft.

Das Dreieck DKT rechnet keine Querkraft selbst. Sie kommt aus den Momenten,
die an den Knoten schon gemittelt sind: über ein Dreieck sind sie linear,
ihr Gefälle ist dort fest, und an den Knoten wird es wieder gemittelt. Eine
Ableitung ist ungenauer als die Grösse selbst, am meisten an einem Rand
oder Lager mit grobem Netz. Ein feineres Netz hilft.

Beispiel: Steigt $m_x$ über 0.5 m von 10 auf 30 kNm/m und ist $m_{xy}$
dort fest, ist $v_x = 20 / 0.5 = 40\,\mathrm{kN/m}$.
