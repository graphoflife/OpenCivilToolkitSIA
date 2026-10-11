---
erzeugt: 5e0822ada68b
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
M_{Rd}^{+} = \left[f_{cd} \cdot b \cdot 0.85 \cdot x^{+} \cdot \left(\tfrac{h}{2} - \tfrac{0.85 \cdot x^{+}}{2}\right) + A_{s,2,x} \cdot \sigma_{sd} \cdot \left(d_{2,x} - \tfrac{h}{2}\right)\right]
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $f_{cd}$ | – | N/mm² | Zwischenwert |
| $b$ | – | mm | Zwischenwert |
| $x^{+}$ | Druckzonenhöhe | mm | [[Nulllinie auf halber Höhe]] |
| $h$ | – | mm | Zwischenwert |
| $A_{s,2,x}$ | – | mm² | Zwischenwert |
| $\sigma_{sd}$ | Stahlspannung | N/mm² | [[Stahlspannung, höchstens die Fliessgrenze]] |
| $d_{2,x}$ | – | mm | [[Statische Höhe]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\begin{aligned}
  M_{Rd}^{+} &= \left[f_{cd} \cdot b \cdot 0.85 \cdot x^{+} \cdot \left(\tfrac{h}{2} - \tfrac{0.85 \cdot x^{+}}{2}\right) + A_{s,2,x} \cdot \sigma_{sd} \cdot \left(d_{2,x} - \tfrac{h}{2}\right)\right] \\
  &= \left[20\,\mathrm{N}/\mathrm{mm}^{2} \cdot 1000\,\mathrm{mm} \cdot 0.85 \cdot 150\,\mathrm{mm} \cdot \left(\tfrac{300\,\mathrm{mm}}{2} - \tfrac{0.85 \cdot 150\,\mathrm{mm}}{2}\right) + 2450\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(248.1\,\mathrm{mm} - \tfrac{300\,\mathrm{mm}}{2}\right)\right] \\
  &= 324.4\,\mathrm{kNm}
\end{aligned}
$$

## Im Code

- `opencivil.nachweis.handrechnung:Handrechnung._halbe_hoehe`

## Themen

- [[Biegung und Normalkraft]]
- [[Knicken]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->
