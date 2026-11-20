---
erzeugt: 15909dde5e81
art: formel
tags: [formel]
normstelle: "SIA 261:2020, 16.2.4.1, (33)"
---
> [!info] Normstelle
> SIA 261:2020, 16.2.4.1, (33)

*In der Herleitung: «Bemessungsspektrum bei T₁ in y»*

$$
S_{d,y} = 2.5 \cdot \gamma_f \cdot \frac{a_{gd}}{g} \cdot S \cdot \frac{T_C}{T_{1,y} \cdot q_y}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\gamma_f$ | Bedeutungsbeiwert | – | Zwischenwert |
| $a_{gd}$ | Bemessungswert der Bodenbeschleunigung | m/s² | Zwischenwert |
| $g$ | Erdbeschleunigung | m/s² | Zwischenwert |
| $S$ | Bodenparameter | – | Zwischenwert |
| $T_C$ | Eckperiode T\_C | s | Zwischenwert |
| $T_{1,y}$ | Grundschwingzeit in y | s | Vorgabe |
| $q_y$ | Verhaltensbeiwert in y | – | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  S_{d,y} &= 2.5 \cdot \gamma_f \cdot \frac{a_{gd}}{g} \cdot S \cdot \frac{T_C}{T_{1,y} \cdot q_y} \\
  &= 2.5 \cdot 1.5 \cdot \frac{1.6\,\mathrm{m}/\mathrm{s}^{2}}{10\,\mathrm{m}/\mathrm{s}^{2}} \cdot 1.7 \cdot \frac{0.25\,\mathrm{s}}{1.2\,\mathrm{s} \cdot 1.5} \\
  &= 0.142
\end{aligned}
$$

## Gebraucht von

- [[Ersatzkraft]]

## Im Code

- [[opencivil.erdbeben.ersatzkraft#Lauf._spektrum|Lauf._spektrum]]

## Themen

- [[Erdbeben]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Zwischen $T_C$ und $T_D$ fällt das Spektrum mit $1/T_1$: ein weiches
Gebäude schwingt langsamer, als der Boden es antreibt, und antwortet mit
weniger Beschleunigung. Am Anfang des Asts schliesst es an das Plateau
[[Bemessungsspektrum (32)|(32)]] an, am Ende an
[[Bemessungsspektrum (34)|(34)]].
