---
erzeugt: 26632d8a7d13
art: formel
tags: [formel]
normstelle: "SIA 261:2020, 16.5.5.2; nach Vorgabe, nicht nachgeschlagen"
---
> [!info] Normstelle
> SIA 261:2020, 16.5.5.2; nach Vorgabe, nicht nachgeschlagen

*In der Herleitung: «Biegesteifigkeit des Kerns in einem Geschoss»*

$$
EI_i = \eta_{EI,i} \cdot E_{cm,i} \cdot I_i
$$

## Im Code

- [[opencivil.erdbeben.ersatzkraft#Lauf._steifigkeit|Lauf._steifigkeit]]

## Themen

- [[Erdbeben]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Kern trägt das Beben als Kragarm, am Fuss eingespannt; die Decken
verbinden seine Wände, als wären sie in ihrer Ebene starr. Je Geschoss
nimmt er die Querschnittsanalyse, die dort gewählt ist: den ganzen Kern mit
allen Wänden in $x$ und in $y$, gezeichnet, wie er im Grundriss liegt –
$y$ der Analyse zeigt in $x$ des Gebäudes. So darf er oben dünner werden
oder ein Geschoss einen anderen haben.

Eine Kraft in $x$ biegt den Kern um seine $z$-Achse: in $x$ gilt
[[Trägheitsmomente des Kerns|$I_z$]], in $y$ gilt $I_y$. Eine Wand von 5 m
Länge trägt so in ihrer Längsrichtung fast alles und quer kaum etwas.
$E_{cm}$ kommt vom Beton der Analyse; eine Analyse mit mehr als einem Beton
oder aus Holz, Stahl oder im Verbund rechnet hier nicht.

Die Norm verlangt eine mittlere Steifigkeit bis zum Fliessbeginn (16.5.1.1,
16.5.5.2), nicht die des ungerissenen Querschnitts. Wie viel davon bleibt,
sagt $\eta_{EI}$, je Geschoss; der Startwert 0.5 ist nach Vorgabe, nicht
nachgeschlagen, ebenso, dass nur die Biegung zählt – Schub und Torsion des
Kerns nicht.

Bis 2026-11-27 nahm jede Wand ihre eigene Analyse, mit Anzahl $n$ und Lage
0° oder 90°, über die ganze Höhe: $EI = \sum n \cdot \eta_{EI} \cdot E_{cm}
\cdot I$.
