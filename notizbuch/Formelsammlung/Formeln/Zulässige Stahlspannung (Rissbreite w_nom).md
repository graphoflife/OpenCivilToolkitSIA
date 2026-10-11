---
erzeugt: a4490f8d3d59
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.4.2"
---
> [!info] Normstelle
> SIA 262:2025, 4.4.2

$$
\sigma_{s,adm,2,x} = \min\left[\sqrt{\frac{9 \cdot E_s \cdot f_{ctm} \cdot w_{nom}}{\varnothing_{2,x}}};\ f_{yk}\right]
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $E_s$ | Elastizitätsmodul des Betonstahls | N/mm² | Vorgabe |
| $f_{ctm}$ | Mittelwert der Zugfestigkeit | N/mm² | Vorgabe |
| $w_{nom}$ | – | mm | Zwischenwert |
| $\varnothing_{2,x}$ | – | mm | [[Dickster Stab der Lage]] |
| $f_{yk}$ | Charakteristische Fliessgrenze | N/mm² | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  \sigma_{s,adm,2,x} &= \min\left[\sqrt{\frac{9 \cdot E_s \cdot f_{ctm} \cdot w_{nom}}{\varnothing_{2,x}}};\ f_{yk}\right] \\
  &= \min\left[\sqrt{\frac{9 \cdot 200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 2.9\,\mathrm{N}/\mathrm{mm}^{2} \cdot 0.5\,\mathrm{mm}}{18\,\mathrm{mm}}};\ 500\,\mathrm{N}/\mathrm{mm}^{2}\right] \\
  &= 381\,\mathrm{N}/\mathrm{mm}^{2}
\end{aligned}
$$

## Gebraucht von

- [[Aufnehmbare Risskraft]]
- [[Aufnehmbares Moment der Bewehrung]]

## Im Code

- [[opencivil.nachweis.mindestbewehrung#protokoll_zulaessige_stahlspannung|protokoll_zulaessige_stahlspannung]]

## Themen

- [[Zwängung auf Normalkraft]]
- [[Zwängung auf Biegung]]
- [[Stahlspannung aus Rissbreite]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie hoch der Stahl in einem Riss gespannt sein darf. Bei normaler Anforderung
gilt die Fliessgrenze $f_{yk}$: die Bewehrung muss nur da sein, sie darf
fliessen. Bei erhöhter Anforderung begrenzt zusätzlich eine nominelle
Rissbreite von 0.5 mm, bei hoher von 0.2 mm.

Die Wurzelformel verknüpft beides: eine Rissbreite $w$ entsteht aus der
Stahldehnung über die Länge, auf der der Verbund die Kraft wieder in den
Beton leitet -- und die wächst mit dem Durchmesser. Löst man nach der
Spannung auf, steht der Durchmesser im Nenner. Dimensionell stimmt die
Formel: $E_s \cdot f_{ctm}$ ist eine Spannung im Quadrat, $w/\varnothing$
dimensionslos.

Gerechnet wird mit $f_{yk}$, nicht $f_{yd}$: nachgewiesen wird, dass die
Bewehrung den Riss übersteht, nicht die Tragfähigkeit.
