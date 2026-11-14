---
erzeugt: adbe35ec2694
art: formel
tags: [formel]
normstelle: "SIA 267:2013, 9.5.4.5"
---
> [!info] Normstelle
> SIA 267:2013, 9.5.4.5

*In der Herleitung: «Bettung quer nahe dem Terrain abgemindert, z ab Terrain»*

$$
k_s(z) = k_s \cdot \min\left(1;\ \frac{z}{t_{red}}\right)
$$

## Im Code

- [[opencivil.pfahl.steifigkeit#Pfahlsteifigkeit._bettung|Pfahlsteifigkeit._bettung]]

## Themen

- [[Pfahlsteifigkeit]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Nahe der Oberfläche hält der Boden quer weniger: das Buch setzt die
Stützkraft an der Oberfläche null und lässt sie nach unten zunehmen
(Kap. 12.10), die Norm verlangt, die Bettung dort abzumindern
(SIA 267:2013, 9.5.4.5). Wie, sagt sie nicht. Das Werkzeug lässt die
Bettung von null am Terrain linear bis zur Tiefe t_red wachsen, vorgegeben
2 m -- nach Vorgabe, nicht nachgeschlagen. Mit t_red = 0 gibt es keine
Abminderung.

Steht der Kopf tiefer als das Terrain, beginnt der Pfahl schon mit einem
Teil der Bettung: bei t_K = 1.5 m und t_red = 2 m mit drei Vierteln. Die
Rechnung lässt die Bettung auch innerhalb jedes Elements linear wachsen,
ohne Stufen.
