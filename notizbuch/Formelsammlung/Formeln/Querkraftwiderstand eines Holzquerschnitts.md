---
erzeugt: 7573caeccc19
art: formel
tags: [formel]
normstelle: "SIA 265:2012, 4.2.5.1, (23)"
---
> [!info] Normstelle
> SIA 265:2012, 4.2.5.1, (23)

*In der Herleitung: «Querkraftwiderstand in z»*

$$
V_{z,Rd} = \eta_w \cdot f_{v,d} \cdot A_{V,z}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\eta_w$ | Beiwert der Holzfeuchte | – | Zwischenwert |
| $f_{v,d}$ | Bemessungswert der Schubfestigkeit | N/mm² | Vorgabe |
| $A_{V,z}$ | Schubfläche für eine Querkraft in z | mm² | [[Schubfläche nach Jourawski]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
V_{z,Rd} = \eta_w \cdot f_{v,d} \cdot A_{V,z} = 0.8 \cdot 1.8\,\mathrm{N}/\mathrm{mm}^{2} \cdot 42667\,\mathrm{mm}^{2} = 61.4\,\mathrm{kN}
$$

## Im Code

- [[opencivil.nachweis.qa_holz_kennzahlen#KennzahlenHolzQA.rechne|KennzahlenHolzQA.rechne]]

## Themen

- [[Kennzahlen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Querkraft, bei der die grösste Schubspannung die Schubfestigkeit
erreicht – mit der [[Schubfläche nach Jourawski]], beim Rechteck zwei
Drittel der Fläche.
