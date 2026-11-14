---
erzeugt: 397f5a36f2ad
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.3.2.2, (39); 4.3.3.2.6"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.3.2.2, (39); 4.3.3.2.6

$$
m_{Dd} = -\frac{N_{Ed} \cdot h}{6} \qquad \varepsilon_v = \frac{f_{yd} \cdot \left(\left|m_{Ed}\right| - m_{Dd}\right)}{E_s \cdot \left(\left|m_{Rd}(N_{Ed})\right| - m_{Dd}\right)}
$$

## Im Code

- [[opencivil.nachweis.querkraft_ohne_buegel#QuerkraftOhneBuegel|QuerkraftOhneBuegel._protokoll_ansatz]]

## Themen

- [[Querkraft]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Ansatz, nach dem die
[[Nominelle Dehnung der Zugbewehrung|nominelle Dehnung der Zugbewehrung]]
gerechnet wird. Eine Druckkraft drückt den Querschnitt vor, bevor er reissen
kann: erst das [[Dekompressionsmoment]] $m_{Dd}$ hebt diesen Druck am Rand
auf. Was an Moment darüber liegt, dehnt die Bewehrung -- linear bis zum
Fliessen beim Biegewiderstand $m_{Rd}$. Eine Zugkraft macht $m_{Dd}$
negativ: die Bewehrung ist dann schon ohne Moment gedehnt.
