---
erzeugt: 505d73db3cd5
art: formel
tags: [formel]
normstelle: "SIA 261:2020, 16.5.5.2; nach Vorgabe, nicht nachgeschlagen"
---
> [!info] Normstelle
> SIA 261:2020, 16.5.5.2; nach Vorgabe, nicht nachgeschlagen

*In der Herleitung: «Biegesteifigkeit der Wände in x»*

$$
EI_x = \sum n \cdot \kappa \cdot E_{cm} \cdot I
$$

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
EI_x = \sum n \cdot \kappa \cdot E_{cm} \cdot I = 87770\,\mathrm{MNm}^{2}
$$

## Gebraucht von

- [[Auslenkung des Dachs]]

## Im Code

- [[opencivil.erdbeben.ersatzkraft#Lauf._steifigkeit|Lauf._steifigkeit]]

## Themen

- [[Erdbeben]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Wände tragen das Beben als Kragarme, am Fuss eingespannt; die Decken
verbinden sie, als wären sie in ihrer Ebene starr, und alle Wände einer
Richtung biegen sich gleich. Ihre Steifigkeiten zählen darum zusammen, $n$
gleiche Wände $n$-mal.

Jede Wand nimmt $E_{cm}$ ihres Betons und das Trägheitsmoment ihrer
Querschnittsanalyse um die Achse, um die sie in dieser Richtung biegt. Liegt
sie unter 0°, zeigt $y$ der Analyse in $x$ des Gebäudes: in $x$ gilt $I_z$,
in $y$ gilt $I_y$; unter 90° umgekehrt. Eine Wand von 5 m Länge trägt so in
ihrer Längsrichtung fast alles und quer kaum etwas.

Die Norm verlangt eine mittlere Steifigkeit bis zum Fliessbeginn (16.5.1.1,
16.5.5.2), nicht die des ungerissenen Querschnitts. Wie viel davon bleibt,
sagt $\kappa$; der Startwert 0.5 ist nach Vorgabe, nicht nachgeschlagen,
ebenso, dass nur die Biegung zählt -- Schub und Torsion der Wände nicht.
