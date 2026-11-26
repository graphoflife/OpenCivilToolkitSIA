---
erzeugt: fffcee42c564
art: formel
tags: [formel]
normstelle: "SIA 265:2012, 3.1.2.1"
---
> [!info] Normstelle
> SIA 265:2012, 3.1.2.1

$$
\varepsilon_{c,0,d} = \frac{f_{c,0,d}}{E_{0,mean}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $f_{c,0,d}$ | Bemessungswert der Druckfestigkeit in Faserrichtung | N/mm² | Vorgabe |
| $E_{0,mean}$ | Elastizitätsmodul in Faserrichtung, Mittelwert | N/mm² | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\varepsilon_{c,0,d} = \frac{f_{c,0,d}}{E_{0,mean}} = \frac{14.5\,\mathrm{N}/\mathrm{mm}^{2}}{11000\,\mathrm{N}/\mathrm{mm}^{2}} = 1.32\,\text{‰}
$$

## Gebraucht von

- [[Grenzstauchung des Holzes, elastisch-plastisch]]

## Im Code

- [[opencivil.material.holz]]

## Themen

- [[Holz]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Auf Druck steigt die Linie mit demselben $E_{0,mean}$ bis $f_{c,0,d}$: bei
C24 bis 12 / 11 000 = 1.09 ‰. Linear gerechnet bricht das Holz dort;
elastisch-plastisch beginnt hier das Fliessen, bis zur
[[Grenzstauchung des Holzes, elastisch-plastisch]].
