---
erzeugt: 098e240b383c
art: formel
tags: [formel]
normstelle: "nach Vorgabe, nicht nachgeschlagen"
---
> [!info] Normstelle
> nach Vorgabe, nicht nachgeschlagen

*In der Herleitung: «Trägheitsmomente des Kerns, je Teil um seinen Schwerpunkt»*

$$
I_y = \sum_k I_{y,k} \qquad I_z = \sum_k I_{z,k} \qquad I_{yz} = \sum_k I_{yz,k}
$$

## Im Code

- [[opencivil.erdbeben.kern#Kern.rechne|Kern.rechne]]

## Themen

- [[Erdbeben]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Was ein Stück Kante teilt, ist fest verbunden und biegt sich gemeinsam: ein
U oder ein Kasten aus mehreren Polygonen zählt um seinen gemeinsamen
Schwerpunkt, mit dem Steiner-Anteil jeder Wand – wie im Bruttoquerschnitt
der Analyse. Eine Ecke allein verbindet nicht; was in einem Polygon liegt,
etwa eine Aussparung, gehört zu ihm.

Getrennte Teile verbindet nur die Decke. Sie zwingt alle in dieselbe
Auslenkung, aber jeder biegt sich um seinen eigenen Schwerpunkt: ihre
Trägheitsmomente zählen zusammen, ohne Steiner-Anteil zwischen ihnen.
Zwei Wände von 5000 × 250 mm, ihre Achsen 5 m auseinander, haben quer so
nur $2 \cdot 5 \cdot 0.25^3 / 12 = 0.013\,\mathrm{m^4}$ – mit Steiner wären
es 15.6 m⁴, als wären sie durch eine steife Scheibe verbunden. Das ist nach
Vorgabe, nicht nachgeschlagen (Benutzer, 2026-11-27), ebenso, dass eine
Aussparung ein Polygon nie trennt, auch wo sie es ganz durchschneidet.

Am Fuss trägt jeder Teil nach seinem Anteil an $I$ – $E_{cm}$ und
$\eta_{EI}$ gelten für alle Teile gleich.
