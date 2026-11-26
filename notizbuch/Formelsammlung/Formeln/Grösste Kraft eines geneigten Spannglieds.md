---
erzeugt: 8b6478b344c6
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.3.4.9; nach Vorgabe, nicht nachgeschlagen"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.3.4.9; nach Vorgabe, nicht nachgeschlagen

*In der Herleitung: «Die grösste Kraft im Glied: mit Verbund bis zur Fliessgrenze, ohne Verbund die nach dem Spannen»*

$$
P_{max} = A_p \cdot f_{pd}\ \text{mit Verbund} \qquad P_{max} = A_p \cdot \sigma_{p0}\ \text{ohne Verbund}
$$

*In der Herleitung: «Spannglied 1: mit Verbund bis zur Fliessgrenze»*

$$
P_{max,1} = A_{p,1} \cdot f_{pd}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $A_{p,1}$ | Querschnitt des Spannstahls, Spannglied 1 | mm² | [[Querschnitt eines Spannglieds]] |
| $f_{pd}$ | Bemessungswert der Fliessgrenze | N/mm² | [[Bemessungswert der Fliessgrenze]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
P_{max,1} = A_{p,1} \cdot f_{pd} = 600\,\mathrm{mm}^{2} \cdot 1391\,\mathrm{N}/\mathrm{mm}^{2} = 834.8\,\mathrm{kN}
$$

## Gebraucht von

- [[Lotrechte Kraft der geneigten Spannglieder]]
- [[Torsion aus der lotrechten Kraft der Spannglieder]]

## Im Code

- [[opencivil.nachweis.schubwandnachweis#Schubwandnachweis._protokoll_glieder|Schubwandnachweis._protokoll_glieder]]

## Themen

- [[Querkraft und Torsion]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wirkt die lotrechte Kraft eines geneigten Glieds der Querkraft entgegen,
vergrössert sie die Querkraft, und zwar mit der grössten Kraft, die im
Spannstahl auftreten kann (SIA 262:2025, 4.3.3.4.9). Welche Kraft das ist,
legt die Norm nicht fest; hier gilt nach Vorgabe:

- mit Verbund $A_p$ mal die Fliessgrenze des gewählten Wertesatzes – so
  weit kann das Glied im Bruch zulegen;
- ohne Verbund $A_p \cdot \sigma_{p0}$, die Kraft gleich nach dem Spannen:
  ein Glied ohne Verbund legt unter Last nicht zu (SIA 262:2025, 4.1.5.1.6),
  und vor den Verlusten ist seine Kraft am grössten.

Vier Litzen ⌀15.7 aus Y1860 mit Verbund: 600 mm² · 1391 N/mm² = 834.8 kN,
gut ein Viertel mehr als $P_\infty$ = 664 kN.

Wirkt die Kraft wie die Querkraft, zählt dagegen nur
[[Spannkraft eines Spannglieds|P∞]] – siehe
[[Lotrechte Kraft der geneigten Spannglieder]].
