---
erzeugt: 1bf083e4dcd3
art: formel
tags: [formel]
normstelle: "SIA 265:2012, 3.1.2.1"
---
> [!info] Normstelle
> SIA 265:2012, 3.1.2.1

$$
\varepsilon_{t,0,d} = \frac{f_{t,0,d}}{E_{0,mean}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $f_{t,0,d}$ | Bemessungswert der Zugfestigkeit in Faserrichtung | N/mm² | Vorgabe |
| $E_{0,mean}$ | Elastizitätsmodul in Faserrichtung, Mittelwert | N/mm² | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\varepsilon_{t,0,d} = \frac{f_{t,0,d}}{E_{0,mean}} = \frac{12\,\mathrm{N}/\mathrm{mm}^{2}}{11000\,\mathrm{N}/\mathrm{mm}^{2}} = 1.09\,\text{‰}
$$

## Im Code

- [[opencivil.material.holz]]

## Themen

- [[Holz]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Auf Zug bricht Holz spröd: die Linie steigt mit $E_{0,mean}$ bis
$f_{t,0,d}$ und endet dort. Bei C24 sind das 8 / 11 000 = 0.73 ‰, bei
GL24h 12 / 11 000 = 1.09 ‰. Eine Faser, die weiter gedehnt wird, trägt
nichts mehr.
