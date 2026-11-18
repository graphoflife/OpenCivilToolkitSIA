---
erzeugt: c3ccc41ee46c
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.5.2, (55); 4.3.5.5"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.5.2, (55); 4.3.5.5

*In der Herleitung: «Kraft einer Wand: ihr stärkster Schubfluss über die ganze Länge»*

$$
V_{Ed} = \max |q| \cdot l
$$

## Im Code

- [[opencivil.nachweis.schubwandnachweis#Schubwandnachweis|Schubwandnachweis._protokoll_ansatz]]

## Themen

- [[Querkraft und Torsion]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Verteilung gibt jedem Stück einer Wand einen Schubfluss $q$ in kN/m:
den Anteil der Querkraft, $V_i/l$, und den Umlauf der Zellen, an die das
Stück grenzt. Mal die Länge $l$ der Wand wird daraus ihre Kraft, die ihr
Fachwerk tragen muss (siehe
[[Widerstand einer Wand (Fachwerk, ihre Länge l als Hebelarm)]]).

Bei einer Zelle rechnet die Norm selbst so: (55) schreibt den Umlauf der
Torsion als Kraft je Wand, $T_d/(2 A_k) \cdot z_i$ mit der Länge $z_i$ der
Wand, und 4.3.5.5 zählt sie mit der Kraft aus der Querkraft zusammen.
Zerfällt eine Wand zwischen zwei Zellen in Stücke mit verschiedenem Fluss,
zählt der stärkste über die ganze Länge -- nach Vorgabe, nicht
nachgeschlagen. Das liegt auf der sicheren Seite und gibt denselben
Erfüllungsgrad wie der Vergleich je Meter, der bis 2026-11-18 galt.
