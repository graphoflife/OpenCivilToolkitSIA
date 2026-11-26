---
erzeugt: 87bfab3900a1
art: formel
tags: [formel]
normstelle: "SIA 263:2013, Anhang B.5, (93)"
---
> [!info] Normstelle
> SIA 263:2013, Anhang B.5, (93)

*In der Herleitung: «Wölbanteil: Knickspannung des Druckgurts nach Euler»*

$$
\sigma_{Dw} = \frac{\pi^2 \cdot E_{a}}{\left(L_{K} / i_{g}\right)^2}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $E_{a}$ | Elastizitätsmodul des Baustahls | N/mm² | Vorgabe |
| $L_{K}$ | Reduzierte Kipplänge | mm | [[Reduzierte Kipplänge]] |
| $i_{g}$ | Trägheitsradius des Druckgurts | mm | [[Trägheitsradius]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\sigma_{Dw} = \frac{\pi^2 \cdot E_{a,\text{S355}}}{\left(L_{K} / i_{g}\right)^2} = \frac{\pi^2 \cdot 210000\,\mathrm{N}/\mathrm{mm}^{2}}{\left(2267.8\,\mathrm{mm} / 56.4\,\mathrm{mm}\right)^2} = 1282\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Gebraucht von

- [[Ideelle Kippspannung]]

## Im Code

- [[opencivil.nachweis.qa_stahl_stabilitaet#_Herleitung.kippen|_Herleitung.kippen]]

## Themen

- [[Knicken und Kippen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Teil der [[Ideelle Kippspannung|ideellen Kippspannung]], den der
Druckgurt allein trägt, als wäre er ein Stab, der seitlich ausknickt:
die Knickspannung nach Euler mit der
[[Reduzierte Kipplänge|reduzierten Kipplänge]] und dem
[[Trägheitsradius|Trägheitsradius des Druckgurts]]. Er fällt mit dem Quadrat der
Kipplänge, der [[Saint-Venant-Anteil der Kippspannung|Saint-Venant-Anteil]]
nur mit ihr: in kurzen Feldern trägt vor allem der Druckgurt, in langen
vor allem die Torsion.
