---
erzeugt: e1b5414a6d1f
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
M_{Rd}(N_{Rd}^{+}) = A_{s,2,x} \cdot f_{yd} \cdot \left(z_{2,x} - \tfrac{h}{2}\right) + A_{s,3,x} \cdot f_{yd} \cdot \left(z_{3,x} - \tfrac{h}{2}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $A_{s,2,x}$ | – | mm² | Zwischenwert |
| $f_{yd}$ | – | N/mm² | Zwischenwert |
| $z_{2,x}$ | – | mm | Zwischenwert |
| $h$ | – | mm | Zwischenwert |
| $A_{s,3,x}$ | – | mm² | Zwischenwert |
| $z_{3,x}$ | – | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\begin{aligned}
  M_{Rd}(N_{Rd}^{+}) &= A_{s,2,x} \cdot f_{yd} \cdot \left(z_{2,x} - \tfrac{h}{2}\right) + A_{s,3,x} \cdot f_{yd} \cdot \left(z_{3,x} - \tfrac{h}{2}\right) \\
  &= 2450\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(248.1\,\mathrm{mm} - \tfrac{300\,\mathrm{mm}}{2}\right) + 754\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(48\,\mathrm{mm} - \tfrac{300\,\mathrm{mm}}{2}\right) \\
  &= 71.1\,\mathrm{kNm}
\end{aligned}
$$

## Im Code

- [[opencivil.nachweis.handrechnung#Handrechnung._groesste_zugkraft|Handrechnung._groesste_zugkraft]]

## Themen

- [[Biegung und Normalkraft]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das Moment, das zum reinen Zug gehört. Jede Lage zieht mit $A_s f_{yd}$ an
ihrem Abstand zur halben Höhe; ist die untere Lage stärker als die obere,
bleibt ein positives Moment. Die Normalkraft greift im Werkzeug immer in der
halben Höhe an, und alle Momente beziehen sich darauf -- sonst hinge die
Linie davon ab, wo man die Kraft hinsetzt.
