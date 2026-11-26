---
erzeugt: 8bd93cc8c8d8
art: formel
tags: [formel]
normstelle: "SIA 265:2012, 4.2.2.1, (10)"
---
> [!info] Normstelle
> SIA 265:2012, 4.2.2.1, (10)

*In der Herleitung: «Druckwiderstand, ohne Knicken»*

$$
N_{Rd}^{-} = -\eta_w \cdot f_{c,0,d} \cdot A
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\eta_w$ | Beiwert der Holzfeuchte | – | Zwischenwert |
| $f_{c,0,d}$ | Bemessungswert der Druckfestigkeit in Faserrichtung | N/mm² | Vorgabe |
| $A$ | Fläche des Bruttoquerschnitts | mm² | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
N_{Rd}^{-} = -\eta_w \cdot f_{c,0,d} \cdot A = -0.8 \cdot 14.5\,\mathrm{N}/\mathrm{mm}^{2} \cdot 64000\,\mathrm{mm}^{2} = -742.4\,\mathrm{kN}
$$

## Im Code

- [[opencivil.nachweis.qa_holz#HolzBiegungQA._normalkraftwiderstand|HolzBiegungQA._normalkraftwiderstand]]
- [[opencivil.nachweis.qa_holz_kennzahlen#KennzahlenHolzQA.rechne|KennzahlenHolzQA.rechne]]

## Themen

- [[Holzquerschnitt]]
- [[Kennzahlen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Normalkraft, bei der die Druckspannung die Druckfestigkeit erreicht –
negativ, wie jeder Druck im Werkzeug, und ohne Knicken. Was ein Stab mit
seiner Länge trägt, sagt der [[Knickwiderstand eines Holzstabs]].
