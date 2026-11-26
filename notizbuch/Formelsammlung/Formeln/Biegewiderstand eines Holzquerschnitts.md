---
erzeugt: 9bb25bf831a5
art: formel
tags: [formel]
normstelle: "SIA 265:2012, 4.2.3.1, (14)"
---
> [!info] Normstelle
> SIA 265:2012, 4.2.3.1, (14)

*In der Herleitung: «Biegewiderstand um z»*

$$
M_{z,Rd} = \eta_w \cdot f_{m,d} \cdot W_z
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\eta_w$ | Beiwert der Holzfeuchte | – | Zwischenwert |
| $f_{m,d}$ | Bemessungswert der Biegefestigkeit | N/mm² | Vorgabe |
| $W_z$ | Widerstandsmoment um z, bis zur weitesten Faser | cm³ | [[Widerstandsmoment bis zur weitesten Faser]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
M_{z,Rd} = \eta_w \cdot f_{m,d} \cdot W_z = 0.8 \cdot 16\,\mathrm{N}/\mathrm{mm}^{2} \cdot 1706.7\,\mathrm{cm}^{3} = 21.8\,\mathrm{kNm}
$$

## Im Code

- [[opencivil.nachweis.qa_holz_kennzahlen#KennzahlenHolzQA.rechne|KennzahlenHolzQA.rechne]]

## Themen

- [[Kennzahlen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das Moment, bei dem die Biegespannung an der weitesten Faser die
Biegefestigkeit erreicht – ohne Normalkraft und ohne Kippen. So bei
Vollholz und, beim Brettschichtholz, für die Biegung um z; um y hebt ihn
dort der Höhenbeiwert, siehe [[Biegewiderstand des Brettschichtholzes]].
