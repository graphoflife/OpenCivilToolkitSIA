---
erzeugt: 20f2519c1737
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
x^{+} = \frac{A_{s,2,x} \cdot f_{yd}}{0.85 \cdot b \cdot f_{cd}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $A_{s,2,x}$ | – | mm² | Zwischenwert |
| $f_{yd}$ | – | N/mm² | Zwischenwert |
| $b$ | – | mm | Zwischenwert |
| $f_{cd}$ | – | N/mm² | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
x^{+} = \frac{A_{s,2,x} \cdot f_{yd}}{0.85 \cdot b \cdot f_{cd}} = \frac{2450\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2}}{0.85 \cdot 1000\,\mathrm{mm} \cdot 20\,\mathrm{N}/\mathrm{mm}^{2}} = 62.7\,\mathrm{mm}
$$

## Gebraucht von

- [[Bezogene Druckzonenhöhe]]
- [[Momentenwiderstand bei reiner Biegung]]

## Im Code

- [[opencivil.nachweis.handrechnung#Handrechnung._bei_n_null|Handrechnung._bei_n_null]]

## Themen

- [[Biegung und Normalkraft]]
- [[Kennzahlen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Bei reiner Biegung halten sich Druck im Beton und Zug im Stahl die Waage.
Der Stahl fliesst und zieht mit $A_s \cdot f_{yd}$; der Beton drückt als
Spannungsblock der Höhe $0.85\,x$ mit $f_{cd}$. Aus der Gleichheit beider
Kräfte folgt $x$ -- die Lage der Nulllinie, ab dem gedrückten Rand.

Dass der Stahl dabei fliesst, setzt die Rechnung voraus. Bei üblicher
Bewehrung trifft das zu; ob die Druckzone dafür klein genug ist, prüft die
[[Bedingung der Duktilität]].
