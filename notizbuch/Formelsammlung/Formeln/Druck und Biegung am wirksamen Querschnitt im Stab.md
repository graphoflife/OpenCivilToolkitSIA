---
erzeugt: e8bf38391ea5
art: formel
tags: [formel]
normstelle: "SIA 263:2013, 5.3.9, (62), (63); 4.2.3.2, Figur 3"
---
> [!info] Normstelle
> SIA 263:2013, 5.3.9, (62), (63); 4.2.3.2, Figur 3

*In der Herleitung: «Klasse 4, (62) – in (63) steht der Faktor beim Glied um z»*

$$
\frac{N_{Ed}}{A_{eff}} + \frac{1}{1 - N_{Ed}/N_{cr,y}} \cdot \frac{M_{y,Ed} + N_{Ed}\,(e_{z} + w_{0,y})}{W_{y,eff}} + \frac{M_{z,Ed} + N_{Ed}\,(e_{y} + w_{0,z})}{W_{z,eff}} \le \frac{f_y}{\gamma_{M1}}
$$

## Im Code

- [[opencivil.nachweis.qa_stahl_stabilitaet#_Herleitung.gleichungen_62|_Herleitung.gleichungen_62]]

## Themen

- [[Knicken und Kippen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

In Klasse 4 beulen Teile des Querschnitts, bevor er fliesst; gerechnet
wird elastisch am wirksamen Querschnitt. (62) und (63) addieren die
Spannungen aus der Druckkraft und den beiden Momenten und vergleichen
sie mit der Fliessgrenze. Der Stab kommt auf zwei Wegen hinein: als
[[Ersatzimperfektion des Stabs]] $w_0$, an der die Druckkraft ein Moment
erzeugt, und als Vergrösserung $1/(1 - N_{Ed}/N_{cr})$ am ausgebogenen
Stab. (62) vergrössert das Glied um y, (63) das um z; beide müssen
erfüllt sein.

Dazu kommt der Versatz $e$: liegt der Schwerpunkt des wirksamen
Querschnitts neben dem des ganzen, erzeugt die Druckkraft auch damit
ein Moment.
