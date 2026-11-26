---
erzeugt: 10f2265d2bed
art: formel
tags: [formel]
normstelle: "SIA 263:2013, 5.1.3, (40)"
---
> [!info] Normstelle
> SIA 263:2013, 5.1.3, (40)

*In der Herleitung: «Plastischer Widerstand in Klasse 1»*

$$
M_{y,Rd}^{+} = \frac{f_y \cdot W_{pl}}{\gamma_{M1}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $f_y$ | Streckgrenze | N/mm² | Vorgabe |
| $W_{pl}$ | Plastisches Widerstandsmoment | cm³ | Zwischenwert |
| $\gamma_{M1}$ | Widerstandsbeiwert für Festigkeits- und Stabilitätsnachweise | – | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
M_{y,Rd}^{+} = \frac{f_y \cdot W_{pl}}{\gamma_{M1}} = \frac{355\,\mathrm{N}/\mathrm{mm}^{2} \cdot 3513.8\,\mathrm{cm}^{3}}{1.05} = 1188\,\mathrm{kNm}
$$

## Im Code

- [[opencivil.nachweis.qa_stahl_kennzahlen#KennzahlenStahlQA._summe|KennzahlenStahlQA._summe]]

## Themen

- [[Kennzahlen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

In den Klassen 1 und 2 halten die gedrückten Bleche, bis der ganze
Querschnitt fliesst. Dann ist jede Faser auf der einen Seite der
plastischen Nulllinie ganz gezogen, auf der anderen ganz gedrückt. Ohne
Normalkraft liegt diese Linie so, dass gleich viel Kraft gezogen wie
gedrückt ist; das Moment der beiden Kräfte ist $f_y \cdot W_{pl}$.

$W_{pl}$ ist die Summe der Flächen mal ihr Abstand von dieser Nulllinie.
Bei gewalzten I-Profilen um die starke Achse ist es 10 bis 15 % grösser
als $W_{el}$ – um so viel trägt der Querschnitt mehr als bis zum ersten
Fliessen ([[Biegewiderstand bis zum ersten Fliessen]]).

Mit Normalkraft und Querkraft sucht die Tragsicherheit je Lastfall den
plastischen Zustand selbst: [[Widerstand in der Richtung der Einwirkung]].
