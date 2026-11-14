---
erzeugt: f50c0fcece48
art: formel
tags: [formel]
normstelle: "SIA 267:2013, 9.5.2.4.1, (50)"
---
> [!info] Normstelle
> SIA 267:2013, 9.5.2.4.1, (50)

*In der Herleitung: «Innerer Widerstand auf Druck, Bemessungswert»*

$$
R_{i,d} = \eta_i \cdot R_{mat,d}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\eta_i$ | Umrechnungsfaktor des inneren Widerstands | – | Vorgabe |
| $R_{mat,d}$ | Materialwiderstand auf Druck | kN | [[Materialwiderstand auf Druck]], [[Materialwiderstand des Stahls]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
R_{i,d} = \eta_i \cdot R_{mat,d} = 0.8 \cdot 14156\,\mathrm{kN} = 11325\,\mathrm{kN}
$$

## Im Code

- [[opencivil.pfahl.innen#InnererWiderstand._bemessung|InnererWiderstand._bemessung]]

## Themen

- [[Innerer Pfahlwiderstand]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Bemessungswert des Querschnitts, abgemindert um den Umrechnungsfaktor η_i
(SIA 267:2013, 9.5.2.4.1, (50)). η_i deckt, was die Herstellung im Boden dem
Pfahl antun kann, ohne dass man es sieht: in der Regel höchstens 0.8
(9.5.2.4.4, (51)), mit einer verlässlichen Prüfung der Integrität des ganzen
Pfahls bis 0.9 (9.5.2.4.9). Massgebend ist der kleinste Querschnitt längs des
Pfahls (9.5.2.4.5).
