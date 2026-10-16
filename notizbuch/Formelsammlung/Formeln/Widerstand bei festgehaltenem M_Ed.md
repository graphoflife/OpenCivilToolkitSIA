---
erzeugt: 79b4e6ee9b61
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Zugwiderstand bei M\_Ed = 0»*

$$
N_{Rd}^{+}(M_{Ed} = 0) = N_1 + \frac{M_{Ed} - M_1}{M_2 - M_1} \cdot \left(N_2 - N_1\right)
$$

*In der Herleitung: «Druckwiderstand bei M\_Ed = 0»*

$$
N_{Rd}^{-}(M_{Ed} = 0) = N_{Rd}^{-}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $N_1$ | – | kN | Zwischenwert |
| $M_{Ed}$ | – | kNm | Zwischenwert |
| $M_1$ | – | kNm | Zwischenwert |
| $M_2$ | – | kNm | Zwischenwert |
| $N_2$ | – | kN | Zwischenwert |
| $N_{Rd}^{-}$ | – | kN | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\begin{aligned}
  N_{Rd}^{+}(M_{Ed} = 0) &= N_1 + \frac{M_{Ed} - M_1}{M_2 - M_1} \cdot \left(N_2 - N_1\right) \\
  &= 1393.2\,\mathrm{kN} + \frac{0\,\mathrm{kNm} - 71.1\,\mathrm{kNm}}{-79.9\,\mathrm{kNm} - 71.1\,\mathrm{kNm}} \cdot \left(0\,\mathrm{kN} - 1393.2\,\mathrm{kN}\right) \\
  &= 737.5\,\mathrm{kN}
\end{aligned}
$$

Mit den Zahlen aus dem Beispielprojekt:

$$
N_{Rd}^{-}(M_{Ed} = 0) = N_{Rd}^{-} = -6000\,\mathrm{kN}
$$

## Im Code

- [[opencivil.nachweis.resistenzlinie#Handlinie.protokoll_treffer|Handlinie.protokoll_treffer]]

## Themen

- [[Kennzahlen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie viel Normalkraft der Querschnitt bei einem festen Moment aufnimmt --
das Gegenstück zum [[Widerstand bei festgehaltenem N_Ed]]. Auf der Linie der
Handrechnung liegt er zwischen den beiden Eckpunkten, zwischen denen das
Moment liegt, und folgt durch lineare Interpolation; fällt das Moment genau
auf einen Eckpunkt, ist es dessen Normalkraft.

Die Kennzahlen der Platte fragen so nach $N_{Rd}^{+}$ und $N_{Rd}^{-}$ bei
$M_{Ed} = 0$. Bei ungleicher Bewehrung oben und unten ist der Zugwiderstand
dort kleiner als die grösste Zugkraft: diese hat ein Moment, weil die
Resultierende der beiden Lagen nicht auf halber Höhe liegt.
