---
erzeugt: ad9917a4cb59
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
| $\varnothing_{2,x}$ | Stabdurchmesser 3. Lage Grundbewehrung | mm | [[Dickster Stab der Lage]], Vorgabe, Zwischenwert |
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
- [[Erfüllungsgrad]]

## Im Code

- [[opencivil.nachweis.mindestbewehrung#protokoll_zulaessige_stahlspannung|protokoll_zulaessige_stahlspannung]]

## Themen

- [[Zwängung auf Normalkraft]]
- [[Zwängung auf Biegung]]
- [[Stahlspannung aus Rissbreite]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->
