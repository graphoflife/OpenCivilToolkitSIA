---
erzeugt: 305f64343c74
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
M_{Rd}(N_{Ed}=0)^{+} = A_{s,2,x} \cdot f_{yd} \cdot \left(d_{2,x} - \frac{0.85 \cdot x^{+}}{2}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $A_{s,2,x}$ | – | mm² | Zwischenwert |
| $f_{yd}$ | – | N/mm² | Zwischenwert |
| $d_{2,x}$ | – | mm | [[Statische Höhe]] |
| $x^{+}$ | Höhe der Druckzone | mm | [[Druckzonenhöhe aus dem Kräftegleichgewicht]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\begin{aligned}
  M_{Rd}(N_{Ed}=0)^{+} &= A_{s,2,x} \cdot f_{yd} \cdot \left(d_{2,x} - \frac{0.85 \cdot x^{+}}{2}\right) \\
  &= 2450\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(248.1\,\mathrm{mm} - \frac{0.85 \cdot 62.7\,\mathrm{mm}}{2}\right) \\
  &= 235.9\,\mathrm{kNm}
\end{aligned}
$$

## Im Code

- `opencivil.nachweis.handrechnung:Handrechnung._bei_n_null`

## Themen

- [[Biegung und Normalkraft]]
- [[Knicken]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->
