---
erzeugt: 7e8544182388
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
N_{Riss} = \frac{h_{eff}}{2} \cdot b \cdot f_{ct,eff}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $h_{eff}$ | – | mm | [[Rissaktive Plattendicke]] |
| $b$ | Betrachtete Breite (x) | mm | Vorgabe |
| $f_{ct,eff}$ | – | N/mm² | [[Wirksame Zugfestigkeit]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
N_{Riss} = \frac{h_{eff}}{2} \cdot b \cdot f_{ct,eff} = \frac{300\,\mathrm{mm}}{2} \cdot 1000\,\mathrm{mm} \cdot 2.52\,\mathrm{N}/\mathrm{mm}^{2} = 378.3\,\mathrm{kN}
$$

## Im Code

- [[opencivil.nachweis.mindestbewehrung#Rissnormalkraft|Rissnormalkraft._protokoll_ansatz]]

## Themen

- [[Zwängung auf Normalkraft]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->
