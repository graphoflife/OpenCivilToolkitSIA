---
erzeugt: dfb689f6fe2d
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
m_{Dd} = \frac{\left|\min(N_{Ed};\ 0)\right| \cdot h}{6} \qquad \varepsilon_v = \frac{f_{yd} \cdot \left(\left|m_{Ed}\right| - m_{Dd}\right)}{E_s \cdot \left(\left|m_{Rd}(N_{Ed})\right| - m_{Dd}\right)}
$$

## Im Code

- [[opencivil.nachweis.querkraft_ohne_buegel#QuerkraftOhneBuegel|QuerkraftOhneBuegel._protokoll_ansatz]]

## Themen

- [[Querkraft]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Ansatz, nach dem die [[Dehnung auf halber Höhe]] gerechnet wird. Eine
Druckkraft drückt den Querschnitt vor, bevor er reissen kann: erst das
[[Dekompressionsmoment]] $m_{Dd}$ hebt diesen Druck am Rand auf. Was an Moment
darüber liegt, dehnt die Bewehrung -- linear bis zum Fliessen beim
Biegewiderstand $m_{Rd}$.
