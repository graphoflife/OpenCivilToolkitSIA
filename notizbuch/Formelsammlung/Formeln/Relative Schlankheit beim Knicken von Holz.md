---
erzeugt: a2cb74ad642d
art: formel
tags: [formel]
normstelle: "SIA 265:2012, 4.2.8.4, (34); Anhang B"
---
> [!info] Normstelle
> SIA 265:2012, 4.2.8.4, (34); Anhang B

*In der Herleitung: «Relative Schlankheit um y»*

$$
\lambda_{rel,y} = \frac{\lambda_y}{\pi} \cdot \sqrt{\frac{f_{c,0,k}}{E_{0,05}}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\lambda_y$ | Schlankheit | – | [[Schlankheit eines Holzstabs]] |
| $f_{c,0,k}$ | Druckfestigkeit in Faserrichtung, kennzeichnend | N/mm² | Vorgabe |
| $E_{0,05}$ | Elastizitätsmodul in Faserrichtung, 5%-Fraktil | N/mm² | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\lambda_{rel,y} = \frac{\lambda_y}{\pi} \cdot \sqrt{\frac{f_{c,0,k}}{E_{0,05}}} = \frac{34.6}{\pi} \cdot \sqrt{\frac{24\,\mathrm{N}/\mathrm{mm}^{2}}{9400\,\mathrm{N}/\mathrm{mm}^{2}}} = 0.557
$$

## Gebraucht von

- [[Hilfswert beim Knicken von Holz]]
- [[Knickbeiwert des Holzes]]

## Im Code

- [[opencivil.nachweis.qa_holz_stabilitaet#_Herleitung|_Herleitung._knicken]]

## Themen

- [[Knicken und Kippen eines Holzstabs]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Schlankheit, bezogen auf die, bei der die Knickspannung nach Euler die
Druckfestigkeit erreicht. Mit $E_{0,05}$, dem 5%-Fraktil, statt dem
Mittelwert: wer knickt, folgt der Steifigkeit, und die streut. Das
Werkzeug rechnet sie ohne $\eta_w$ – nach Vorgabe, nicht nachgeschlagen.
