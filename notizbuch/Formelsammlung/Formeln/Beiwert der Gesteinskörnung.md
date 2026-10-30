---
erzeugt: 99a2faa31ea1
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

Mit den Zahlen aus dem Beispielprojekt:

$$
\begin{aligned}
  k_g &= \max\left[1.20;\ \frac{48}{16 + D_{max} \cdot \min\left[1.0;\ \left(\frac{60}{f_{ck}}\right)^{2}\right]}\right] \\
  &= \max\left[1.20;\ \frac{48}{16 + 32 \cdot \min\left[1.0;\ \left(\frac{60}{30}\right)^{2}\right]}\right] \\
  &= 1.2 \quad \left(D_{max}\ \text{in}\ \mathrm{mm},\ f_{ck}\ \text{in}\ \mathrm{N}/\mathrm{mm}^{2}\right)
\end{aligned}
$$

## Gebraucht von

- [[Beiwert für die statische Höhe]]
- [[Beiwert k_r]]

## Im Code

- [[opencivil.nachweis.querkraft_ohne_buegel#beiwert_k_g|beiwert_k_g]]

## Themen

- [[Kennzahlen]]
- [[Querkraft]]
- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie gut sich die Ufer eines Risses verzahnen, hängt an der Gesteinskörnung:
grobe Körner greifen besser ineinander. Bei sehr festem Beton laufen die
Risse durch die Körner statt um sie herum, und ihre Grösse zählt weniger --
daher der Faktor $\min[1;\ (60/f_{ck})^2]$ am Grösstkorn. Der Beiwert hat
eine untere Grenze von 1.2.

Die Formel ist empirisch: $D_{max}$ in mm und $f_{ck}$ in N/mm² gehen als
blosse Zahlen ein.
