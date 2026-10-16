---
erzeugt: 002ddd13c03c
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Widerstand bei N\_Ed – ein Eckpunkt liegt genau dort»*

$$
M_{Rd} = M_{Rd}(N_{Ed}=0)^{+}
$$

*In der Herleitung: «Widerstand bei festgehaltenem N\_Ed»*

$$
M_{Rd} = M_1 + \frac{N_{Ed} - N_1}{N_2 - N_1} \cdot \left(M_2 - M_1\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $M_{Rd}(N_{Ed}=0)^{+}$ | – | kNm | Zwischenwert |
| $M_1$ | – | kNm | Zwischenwert |
| $N_{Ed}$ | – | kN | Zwischenwert |
| $N_1$ | – | kN | Zwischenwert |
| $N_2$ | – | kN | Zwischenwert |
| $M_2$ | – | kNm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
M_{Rd} = M_{Rd}(N_{Ed}=0)^{+} = 235.9\,\mathrm{kNm}
$$

Mit den Zahlen aus dem Beispielprojekt:

$$
\begin{aligned}
  M_{Rd} &= M_1 + \frac{N_{Ed} - N_1}{N_2 - N_1} \cdot \left(M_2 - M_1\right) \\
  &= 324.4\,\mathrm{kNm} + \frac{-300\,\mathrm{kN} - \left(-1484.6\,\mathrm{kN}\right)}{0\,\mathrm{kN} - \left(-1484.6\,\mathrm{kN}\right)} \cdot \left(235.9\,\mathrm{kNm} - 324.4\,\mathrm{kNm}\right) \\
  &= 253.8\,\mathrm{kNm}
\end{aligned}
$$

## Gebraucht von

- [[Erfüllungsgrad]]

## Im Code

- [[opencivil.nachweis.resistenzlinie#Handlinie.protokoll_treffer|Handlinie.protokoll_treffer]]

## Themen

- [[Biegung und Normalkraft]]
- [[Kennzahlen]]
- [[Querkraft]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie viel Moment der Querschnitt bei der wirkenden Normalkraft aufnimmt. Die
Handrechnung hat nur Eckpunkte; dazwischen ist ihre Linie gerade, und der
Widerstand bei $N_{Ed}$ folgt durch lineare Interpolation zwischen den beiden
Eckpunkten, zwischen denen $N_{Ed}$ liegt. Fällt $N_{Ed}$ genau auf einen
Eckpunkt, ist es dessen Moment.

Dieselbe Frage mit der Linie aus Dehnungsebenen beantwortet keine
Interpolation: dort wird die Ebene gesucht, deren Normalkraft genau $N_{Ed}$
ist, und die Probe zeigt sie.
