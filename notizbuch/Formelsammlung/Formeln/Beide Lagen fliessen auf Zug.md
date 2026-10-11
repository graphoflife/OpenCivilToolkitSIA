---
erzeugt: 7f5d1122460a
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
N_{Rd}^{+} = A_{s,2,x} \cdot f_{yd} + A_{s,3,x} \cdot f_{yd}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $A_{s,2,x}$ | – | mm² | Zwischenwert |
| $f_{yd}$ | – | N/mm² | Zwischenwert |
| $A_{s,3,x}$ | – | mm² | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\begin{aligned}
  N_{Rd}^{+} &= A_{s,2,x} \cdot f_{yd} + A_{s,3,x} \cdot f_{yd} \\
  &= 2450\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} + 754\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \\
  &= 1393.2\,\mathrm{kN}
\end{aligned}
$$

## Im Code

- [[opencivil.nachweis.handrechnung#Handrechnung._groesste_zugkraft|Handrechnung._groesste_zugkraft]]

## Themen

- [[Biegung und Normalkraft]]
- [[Knicken]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der rechte Eckpunkt: der Beton ist ganz gerissen und trägt nichts, beide
Bewehrungslagen fliessen. Die Zugkraft ist die Summe der Flächen mal $f_{yd}$.
Sind die Lagen verschieden stark, liegt die Kraft nicht in der halben Höhe --
dazu gehört ein Moment, siehe [[Kräfte mal Hebelarm um die halbe Höhe]].
