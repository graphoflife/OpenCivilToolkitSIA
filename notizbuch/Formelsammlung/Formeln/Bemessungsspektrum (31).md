---
erzeugt: e816d23a6a8e
art: formel
tags: [formel]
normstelle: "SIA 261:2020, 16.2.4.1, (31)"
---
> [!info] Normstelle
> SIA 261:2020, 16.2.4.1, (31)

*In der Herleitung: «Bemessungsspektrum bei T₁ in x»*

$$
S_{d,x} = \gamma_f \cdot \frac{a_{gd}}{g} \cdot S \cdot \left(0.67 + \left(\frac{2.5}{q_x} - 0.67\right) \cdot \frac{T_{1,x}}{T_B}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\gamma_f$ | Bedeutungsbeiwert | – | Zwischenwert |
| $a_{gd}$ | Bemessungswert der Bodenbeschleunigung | m/s² | Zwischenwert |
| $g$ | Erdbeschleunigung | m/s² | Zwischenwert |
| $S$ | Bodenparameter | – | Zwischenwert |
| $q_x$ | Verhaltensbeiwert in x | – | Vorgabe |
| $T_{1,x}$ | Grundschwingzeit in x | s | Vorgabe |
| $T_B$ | Eckperiode T\_B | s | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  S_{d,x} &= \gamma_f \cdot \frac{a_{gd}}{g} \cdot S \cdot \left(0.67 + \left(\frac{2.5}{q_x} - 0.67\right) \cdot \frac{T_{1,x}}{T_B}\right) \\
  &= 1.5 \cdot \frac{1.6\,\mathrm{m}/\mathrm{s}^{2}}{10\,\mathrm{m}/\mathrm{s}^{2}} \cdot 1.7 \cdot \left(0.67 + \left(\frac{2.5}{2} - 0.67\right) \cdot \frac{0.05\,\mathrm{s}}{0.09\,\mathrm{s}}\right) \\
  &= 0.405
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

Das Bemessungsspektrum (16.2.4.1) gibt, als Bruchteil von $g$, die
waagrechte Beschleunigung, mit der ein Schwinger der Schwingzeit $T$ auf das
Beben antwortet: aus dem elastischen Spektrum mit 5 % Dämpfung, geteilt durch
den Verhaltensbeiwert $q$ und mal den Bedeutungsbeiwert $\gamma_f$
(Tabelle 25). $a_{gd}$ kommt aus der Zone (16.2.1.2), $S$, $T_B$, $T_C$ und
$T_D$ aus der Baugrundklasse (Tabelle 24). Vier Äste, je nach $T_1$: (31) bis
(34).

(31) ist der kurze Ast, $T_1 < T_B$: eine Gerade vom Wert bei $T = 0$,
$0.67 \cdot \gamma_f \cdot a_{gd}/g \cdot S$ ohne $q$, bis zum Plateau
[[Bemessungsspektrum (32)|(32)]] bei $T_B$. Ist $q$ gross, fällt die Gerade
zum Plateau hin, statt zu steigen.
