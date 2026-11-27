---
erzeugt: d34e744961cc
art: formel
tags: [formel]
normstelle: "SIA 261:2020, 16.2.4.1, (34)"
---
> [!info] Normstelle
> SIA 261:2020, 16.2.4.1, (34)

*In der Herleitung: «Bemessungsspektrum bei T₁ in y»*

$$
S_{d,y} = \max\left(2.5 \cdot \gamma_f \cdot \frac{a_{gd}}{g} \cdot S \cdot \frac{T_C \cdot T_D}{T_{1,y}^2 \cdot q_y};\ 0.1 \cdot \gamma_f \cdot \frac{a_{gd}}{g}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\gamma_f$ | Bedeutungsbeiwert | – | Zwischenwert |
| $a_{gd}$ | Bemessungswert der Bodenbeschleunigung | m/s² | Zwischenwert |
| $g$ | Erdbeschleunigung | m/s² | Zwischenwert |
| $S$ | Bodenparameter | – | Zwischenwert |
| $T_C$ | Eckperiode T\_C | s | Zwischenwert |
| $T_D$ | Eckperiode T\_D | s | Zwischenwert |
| $T_{1,y}$ | Grundschwingzeit in y | s | [[Grundschwingzeit]] |
| $q_y$ | Verhaltensbeiwert in y | – | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  S_{d,y} &= \max\left(2.5 \cdot \gamma_f \cdot \frac{a_{gd}}{g} \cdot S \cdot \frac{T_C \cdot T_D}{T_{1,y}^2 \cdot q_y};\ 0.1 \cdot \gamma_f \cdot \frac{a_{gd}}{g}\right) \\
  &= \max\left(2.5 \cdot 1 \cdot \frac{1\,\mathrm{m}/\mathrm{s}^{2}}{10\,\mathrm{m}/\mathrm{s}^{2}} \cdot 1.7 \cdot \frac{0.5\,\mathrm{s} \cdot 2\,\mathrm{s}}{\left(2.769\,\mathrm{s}\right)^2 \cdot 3};\ 0.1 \cdot 1 \cdot \frac{1\,\mathrm{m}/\mathrm{s}^{2}}{10\,\mathrm{m}/\mathrm{s}^{2}}\right) \\
  &= 0.018
\end{aligned}
$$

## Im Code

- [[opencivil.erdbeben.ersatzkraft#Lauf._spektrum|Lauf._spektrum]]

## Themen

- [[Erdbeben]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Über $T_D$ fällt das Spektrum mit $1/T_1^2$, aber nie unter
$0.1 \cdot \gamma_f \cdot a_{gd}/g$. Für das Ersatzkraftverfahren ist der
Ast ein Grenzfall: $4 \cdot T_C$ ist bei jeder Baugrundklasse höchstens
$T_D$, wer hier liegt, verfehlt also [[Grenze der Grundschwingzeit|(39)]].
Gerechnet wird trotzdem, damit die Zahlen zu sehen sind.
