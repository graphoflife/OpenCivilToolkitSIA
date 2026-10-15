---
erzeugt: 8072cdd127ce
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.7"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.7

$$
\alpha_i = \min\left[\max\left(\frac{0.01}{\sqrt{l}};\ \frac{1}{300}\right);\ \frac{1}{200}\right] \quad \left(l\ \text{in}\ \mathrm{m}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $l$ | – | m | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  \alpha_i &= \min\left[\max\left(\frac{0.01}{\sqrt{l}};\ \frac{1}{300}\right);\ \frac{1}{200}\right] \\
  &= \min\left[\max\left(\frac{0.01}{\sqrt{3}};\ \frac{1}{300}\right);\ \frac{1}{200}\right] \\
  &= 0.005 \quad \left(l\ \text{in}\ \mathrm{m}\right)
\end{aligned}
$$

## Gebraucht von

- [[Ungewollte Ausmitte]]

## Im Code

- [[opencivil.nachweis.knicken#Knickverfahren|Knickverfahren._protokoll_fall]]

## Themen

- [[Knicken]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die ungewollte Neigung eines Stabs, als Winkel: kurze Stäbe dürfen
verhältnismässig schiefer stehen als lange, darum der Faktor $1/\sqrt{l}$,
begrenzt zwischen 1/300 und 1/200. Die Formel ist empirisch: $l$ geht in
Metern ein.
