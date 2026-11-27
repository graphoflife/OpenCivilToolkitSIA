---
erzeugt: 58e59b8ea5f8
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.3.4.8, (50); SIA 262:2025, 4.3.3.4.9"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.3.4.8, (50); SIA 262:2025, 4.3.3.4.9

*In der Herleitung: «Lotrechte Kraft der Glieder, und welche Kraft im Glied zählt»*

$$
V_p = \sum_i F_i \cdot \sin\beta_{p,i} \qquad F_i = P_{\infty,i}\ \text{wo sie}\ V_{z,Ed}\ \text{mitträgt} \qquad F_i = P_{max,i}\ \text{wo sie entgegen wirkt}
$$

*In der Herleitung: «Lotrechte Kraft der geneigten Spannglieder»*

$$
V_p = P_{\infty,1} \cdot \sin \beta_{p,1} + P_{max,2} \cdot \sin \beta_{p,2}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $P_{\infty,1}$ | Spannkraft nach allen Verlusten, Spannglied 1 | kN | [[Spannkraft eines Spannglieds]] |
| $\beta_{p,1}$ | Neigung, Spannglied 1 | ° | Zwischenwert |
| $P_{max,2}$ | Grösste Kraft im Glied, Spannglied 2 | kN | [[Grösste Kraft eines geneigten Spannglieds]] |
| $\beta_{p,2}$ | Neigung, Spannglied 2 | ° | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  V_p &= P_{\infty,1} \cdot \sin \beta_{p,1} + P_{max,2} \cdot \sin \beta_{p,2} \\
  &= 664\,\mathrm{kN} \cdot \sin 5{}^{\circ} + 380.2\,\mathrm{kN} \cdot \sin \left(-4{}^{\circ}\right) \\
  &= 31.4\,\mathrm{kN}
\end{aligned}
$$

## Gebraucht von

- [[Querkraft der Wände neben geneigten Spanngliedern]]

## Im Code

- [[opencivil.nachweis.schubwandnachweis#Schubwandnachweis._ohne_glieder|Schubwandnachweis._ohne_glieder]]
- [[opencivil.nachweis.schubwandnachweis#Schubwandnachweis._protokoll_glieder|Schubwandnachweis._protokoll_glieder]]

## Themen

- [[Querkraft und Torsion]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ein Spannglied, das gegen die Stabachse um $\beta_p$ geneigt ist, zieht am
Schnitt längs seiner Achse – mit einem lotrechten Anteil $F \cdot \sin
\beta_p$. Diesen Anteil trägt das Glied selbst, neben dem Druckfeld der
Stege (SIA 262:2025, Figur 18). Das Vorzeichen: $\beta_p > 0$ heisst, die
lotrechte Kraft wirkt wie ein positives $V_z$.

Welche Kraft $F$ zählt, hängt am Lastfall:

- wirkt die lotrechte Kraft wie dessen $V_{z,Ed}$, trägt sie es mit, mit
  der Kraft nach allen Verlusten $P_\infty$ (SIA 262:2025, 4.3.3.4.8,
  Gl. 50); mehr nur mit genaueren Untersuchungen;
- wirkt sie entgegen, kommt sie zur Querkraft dazu, mit der
  [[Grösste Kraft eines geneigten Spannglieds|grössten Kraft im Glied]]
  (SIA 262:2025, 4.3.3.4.9).

Dasselbe Glied kann so in einem Lastfall helfen und im nächsten, wo die
Querkraft das Vorzeichen wechselt, schaden. Schlaff angesetzte Glieder
zählen hier nicht: ihre Vorspannung steht samt Neigung schon in den
Lastfällen.

Vier Litzen mit $P_\infty$ = 664 kN, um 5° geneigt: 664 kN · sin 5° =
57.9 kN. Ein Glied ohne Verbund mit $P_{max}$ = 378 kN, um −4° geneigt:
378 kN · sin(−4°) = −26.4 kN. Zusammen $V_p$ = 31.5 kN.
