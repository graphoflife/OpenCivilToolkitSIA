---
erzeugt: 5d84ecfb21b9
art: formel
tags: [formel]
normstelle: "SIA 265:2012, 4.2.5.2, (24)"
---
> [!info] Normstelle
> SIA 265:2012, 4.2.5.2, (24)

*In der Herleitung: «Torsionswiderstand»*

$$
T_{Rd} = \eta_w \cdot f_{v,d} \cdot W_T
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\eta_w$ | Beiwert der Holzfeuchte | – | Zwischenwert |
| $f_{v,d}$ | Bemessungswert der Schubfestigkeit | N/mm² | Vorgabe |
| $W_T$ | Torsionswiderstandsmoment des Rechtecks | cm³ | [[Torsionswiderstandsmoment des Rechtecks]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
T_{Rd} = \eta_w \cdot f_{v,d} \cdot W_T = 0.8 \cdot 1.8\,\mathrm{N}/\mathrm{mm}^{2} \cdot 2637.7\,\mathrm{cm}^{3} = 3.8\,\mathrm{kNm}
$$

## Im Code

- [[opencivil.nachweis.qa_holz_kennzahlen#KennzahlenHolzQA.rechne|KennzahlenHolzQA.rechne]]

## Themen

- [[Kennzahlen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das Torsionsmoment, bei dem die grösste Schubspannung die Schubfestigkeit
erreicht, ohne Querkraft – nur für ein Rechteck.
