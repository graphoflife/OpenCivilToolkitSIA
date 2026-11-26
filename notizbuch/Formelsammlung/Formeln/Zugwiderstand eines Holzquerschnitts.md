---
erzeugt: 79ad1882d150
art: formel
tags: [formel]
normstelle: "SIA 265:2012, 4.2.1.1, (6)"
---
> [!info] Normstelle
> SIA 265:2012, 4.2.1.1, (6)

*In der Herleitung: «Zugwiderstand»*

$$
N_{Rd}^{+} = \eta_w \cdot f_{t,0,d} \cdot A
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\eta_w$ | Beiwert der Holzfeuchte | – | Zwischenwert |
| $f_{t,0,d}$ | Bemessungswert der Zugfestigkeit in Faserrichtung | N/mm² | Vorgabe |
| $A$ | Fläche des Bruttoquerschnitts | mm² | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
N_{Rd}^{+} = \eta_w \cdot f_{t,0,d} \cdot A = 0.8 \cdot 12\,\mathrm{N}/\mathrm{mm}^{2} \cdot 64000\,\mathrm{mm}^{2} = 614.4\,\mathrm{kN}
$$

## Im Code

- [[opencivil.nachweis.qa_holz#HolzBiegungQA._normalkraftwiderstand|HolzBiegungQA._normalkraftwiderstand]]
- [[opencivil.nachweis.qa_holz_kennzahlen#KennzahlenHolzQA.rechne|KennzahlenHolzQA.rechne]]

## Themen

- [[Holzquerschnitt]]
- [[Kennzahlen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Normalkraft, bei der die Zugspannung die Zugfestigkeit erreicht – am
Bruttoquerschnitt, ohne Schwächung durch Verbindungen.
