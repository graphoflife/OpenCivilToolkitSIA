---
erzeugt: 98e9cadd79f5
art: formel
tags: [formel]
normstelle: "SIA 267:2013, 9.5.4.5, (53)"
---
> [!info] Normstelle
> SIA 267:2013, 9.5.4.5, (53)

*In der Herleitung: «Bettung quer, je Meter Pfahl»*

$$
k_s = \frac{E_{s,k}}{D} \qquad k_s \cdot D = E_{s,k}
$$

## Im Code

- [[opencivil.pfahl.steifigkeit#Pfahlsteifigkeit._bettung|Pfahlsteifigkeit._bettung]]

## Themen

- [[Pfahlsteifigkeit]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie stark der Boden quer gegen den Pfahl drückt, wenn dieser sich seitlich
verschiebt: im elastischen Bereich ungefähr der Verformungsmodul durch den
Durchmesser (SIA 267:2013, 9.5.4.5, (53)). Je Meter Pfahl zählt
k_s · D = E_s,k -- der Durchmesser fällt heraus. ⌀ 900 mm in
E_s,k = 30 MN/m²: k_s = 33 MN/m³, je Meter Pfahl 30 MN/m².

Das Buch nennt einen etwas grösseren Wert, rund 1.4 · E_s / D
(Kap. 12.10); das Werkzeug folgt der Norm. Die Bettung ist linear und ohne
Grenze. Ob der Boden den Druck auch aufnehmen kann, ist nach der Norm über
die Tiefe, in der der Pfahl die Querlast abgibt, mit seinem Widerstand zu
vergleichen (9.5.4.5) -- das rechnet das Werkzeug noch nicht.
