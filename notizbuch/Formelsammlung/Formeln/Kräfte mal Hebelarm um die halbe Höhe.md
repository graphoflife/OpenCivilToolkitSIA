---
erzeugt: e9cf6009c4c2
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

- `opencivil.nachweis.handrechnung:Handrechnung._groesste_zugkraft`

## Themen

- [[Biegung und Normalkraft]]
- [[Knicken]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->
