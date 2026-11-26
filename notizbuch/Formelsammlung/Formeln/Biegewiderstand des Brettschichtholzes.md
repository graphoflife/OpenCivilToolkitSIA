---
erzeugt: 53ade4ec9631
art: formel
tags: [formel]
normstelle: "SIA 265:2012, 4.2.3.1, (14)"
---
> [!info] Normstelle
> SIA 265:2012, 4.2.3.1, (14)

*In der Herleitung: «Biegewiderstand um y, mit dem Höhenbeiwert»*

$$
M_{y,Rd} = \eta_w \cdot k_h \cdot f_{m,d} \cdot W_y
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\eta_w$ | Beiwert der Holzfeuchte | – | Zwischenwert |
| $k_h$ | Höhenbeiwert des Brettschichtholzes | – | [[Höhenbeiwert des Brettschichtholzes]] |
| $f_{m,d}$ | Bemessungswert der Biegefestigkeit | N/mm² | Vorgabe |
| $W_y$ | Widerstandsmoment um y, bis zur weitesten Faser | cm³ | [[Widerstandsmoment bis zur weitesten Faser]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
M_{y,Rd} = \eta_w \cdot k_h \cdot f_{m,d} \cdot W_y = 0.8 \cdot 1.041 \cdot 16\,\mathrm{N}/\mathrm{mm}^{2} \cdot 4266.7\,\mathrm{cm}^{3} = 56.9\,\mathrm{kNm}
$$

## Im Code

- [[opencivil.nachweis.qa_holz_kennzahlen#KennzahlenHolzQA.rechne|KennzahlenHolzQA.rechne]]

## Themen

- [[Kennzahlen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das Moment, bei dem die Biegespannung an der weitesten Faser die
Biegefestigkeit erreicht – ohne Normalkraft und ohne Kippen. Beim
Brettschichtholz unter 600 mm Höhe hebt der
[[Höhenbeiwert des Brettschichtholzes]] die Biegefestigkeit um y.
