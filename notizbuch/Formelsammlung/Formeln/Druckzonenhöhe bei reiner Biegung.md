---
erzeugt: 9fec1952fa5c
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
x = \frac{A_{s,2,x} \cdot f_{sd}}{0.85 \cdot b \cdot f_{cd}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $A_{s,2,x}$ | – | mm² | [[Bewehrung der Lage]] |
| $f_{sd}$ | – | N/mm² | Zwischenwert |
| $b$ | Betrachtete Breite (x) | mm | Vorgabe |
| $f_{cd}$ | Bemessungswert der Betondruckfestigkeit | N/mm² | [[Bemessungswert der Betondruckfestigkeit]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
x = \frac{A_{s,2,x} \cdot f_{sd}}{0.85 \cdot b \cdot f_{cd}} = \frac{2450\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2}}{0.85 \cdot 1000\,\mathrm{mm} \cdot 20\,\mathrm{N}/\mathrm{mm}^{2}} = 62.7\,\mathrm{mm}
$$

## Im Code

- [[opencivil.nachweis.duktilitaet#Duktilitaet._protokoll_lage|Duktilitaet._protokoll_lage]]

## Themen

- [[Duktilität]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Druckzonenhöhe, die die Duktilität prüft -- je Lage gerechnet, als trüge
sie allein: ihre Fläche mal der Stahlspannung, im Gleichgewicht mit dem
Spannungsblock. Dieselbe Rechnung wie die
[[Druckzonenhöhe aus dem Kräftegleichgewicht]] der Handrechnung, hier für
jede Lage einzeln.
