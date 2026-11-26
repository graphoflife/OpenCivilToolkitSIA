---
erzeugt: 408285bbbbea
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.3.4.8, (50); SIA 262:2025, 4.3.3.4.9; nach Vorgabe, nicht nachgeschlagen"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.3.4.8, (50); SIA 262:2025, 4.3.3.4.9; nach Vorgabe, nicht nachgeschlagen

*In der Herleitung: «Was die Wände tragen: die Last ohne die lotrechte Kraft der Glieder»*

$$
V_{z,w} = V_{z,Ed} - V_p \qquad T_w = T_{Ed} - \sum_i F_i \cdot \sin\beta_{p,i} \cdot (y_i - y_S)
$$

*In der Herleitung: «Was die Wände von V\_z tragen»*

$$
V_{z,w} = V_{z,Ed} - V_p
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $V_{z,Ed}$ | – | kN | Zwischenwert |
| $V_p$ | Lotrechte Kraft der geneigten Spannglieder | kN | [[Lotrechte Kraft der geneigten Spannglieder]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
V_{z,w} = V_{z,Ed} - V_p = 450\,\mathrm{kN} - 31.5\,\mathrm{kN} = 418.5\,\mathrm{kN}
$$

## Im Code

- [[opencivil.nachweis.schubwandnachweis#Schubwandnachweis._ohne_glieder|Schubwandnachweis._ohne_glieder]]
- [[opencivil.nachweis.schubwandnachweis#Schubwandnachweis._protokoll_glieder|Schubwandnachweis._protokoll_glieder]]

## Themen

- [[Querkraft und Torsion]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Was die [[Lotrechte Kraft der geneigten Spannglieder|geneigten Glieder]]
nicht tragen, bleibt den Schubwänden: $V_{z,w} = V_{z,Ed} - V_p$. Diese
Kraft wird nach den Federn der Wände verteilt, und jede Wand vergleicht
ihren Teil mit ihrem Fachwerkwiderstand.

Gl. 50 der Norm schreibt den mitgetragenen Teil dem Widerstand zu:
$V_{Rd} + \Delta V_{Rd,p}$ gegen $V_{Ed}$ (SIA 262:2025, 4.3.3.4.8). Hier
mindert er die Einwirkung. An der Grenze ist das dasselbe, und nur so
verteilt er sich auf mehrere Wände. Der Erfüllungsgrad ist dann
$V_{Rd} / (V_{Ed} - V_p)$, nicht $(V_{Rd} + V_p) / V_{Ed}$ – nach Vorgabe.

Wirkt ein Glied entgegen, ist $V_p$ negativ, und die Wände tragen mehr
als $V_{z,Ed}$ (SIA 262:2025, 4.3.3.4.9).

Rechteck 300 × 600 mm, eine Wand, $V_{z,Ed}$ = 300 kN, vier Litzen um 5°
geneigt: 300 − 57.9 = 242.1 kN. Um −5° geneigt, mit Verbund: 300 +
834.8 · sin 5° = 372.8 kN.
