---
erzeugt: 92cfd050a0b8
art: formel
tags: [formel]
normstelle: "SIA 261:2020, 16.2.4.1, (32)"
---
> [!info] Normstelle
> SIA 261:2020, 16.2.4.1, (32)

*In der Herleitung: «Bemessungsspektrum bei T₁ in x»*

$$
S_{d,x} = 2.5 \cdot \gamma_f \cdot \frac{a_{gd}}{g} \cdot \frac{S}{q_x}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\gamma_f$ | Bedeutungsbeiwert | – | Zwischenwert |
| $a_{gd}$ | Bemessungswert der Bodenbeschleunigung | m/s² | Zwischenwert |
| $g$ | Erdbeschleunigung | m/s² | Zwischenwert |
| $S$ | Bodenparameter | – | Zwischenwert |
| $q_x$ | Verhaltensbeiwert in x | – | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
S_{d,x} = 2.5 \cdot \gamma_f \cdot \frac{a_{gd}}{g} \cdot \frac{S}{q_x} = 2.5 \cdot 1 \cdot \frac{0.8\,\mathrm{m}/\mathrm{s}^{2}}{10\,\mathrm{m}/\mathrm{s}^{2}} \cdot \frac{1.45}{1.5} = 0.193
$$

## Gebraucht von

- [[Ersatzkraft]]

## Im Code

- [[opencivil.erdbeben.ersatzkraft#Lauf._spektrum|Lauf._spektrum]]

## Themen

- [[Erdbeben]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das Plateau zwischen $T_B$ und $T_C$: das 2.5-Fache der Bodenbeschleunigung,
mal $S$ und $\gamma_f$, geteilt durch $q$. Hier liegen die meisten niedrigen,
steifen Gebäude, auch das Wohnhaus des Beispiels. Wie die vier Äste
zusammenhängen, steht beim kurzen Ast, [[Bemessungsspektrum (31)|(31)]].
