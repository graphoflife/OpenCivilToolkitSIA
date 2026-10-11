---
erzeugt: a82d12767e1f
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.3.2.1"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.3.2.1

$$
k_g = \max\left[1.20;\ \frac{48}{16 + D_{max} \cdot \min\left[1.0;\ \left(\frac{60}{f_{ck}}\right)^{2}\right]}\right] \quad \left(D_{max}\ \text{in}\ \mathrm{mm},\ f_{ck}\ \text{in}\ \mathrm{N}/\mathrm{mm}^{2}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $D_{max}$ | Grösstkorndurchmesser | mm | Vorgabe |
| $f_{ck}$ | Charakteristische Zylinderdruckfestigkeit | N/mm² | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  k_g &= \max\left[1.20;\ \frac{48}{16 + D_{max} \cdot \min\left[1.0;\ \left(\frac{60}{f_{ck}}\right)^{2}\right]}\right] \\
  &= \max\left[1.20;\ \frac{48}{16 + 32 \cdot \min\left[1.0;\ \left(\frac{60}{30}\right)^{2}\right]}\right] \\
  &= 1.2 \quad \left(D_{max}\ \text{in}\ \mathrm{mm},\ f_{ck}\ \text{in}\ \mathrm{N}/\mathrm{mm}^{2}\right)
\end{aligned}
$$

## Gebraucht von

- [[Beiwert für die statische Höhe]]

## Im Code

- [[opencivil.nachweis.querkraft#Querkraft|Querkraft._protokoll_k_g]]

## Themen

- [[Querkraft]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->
