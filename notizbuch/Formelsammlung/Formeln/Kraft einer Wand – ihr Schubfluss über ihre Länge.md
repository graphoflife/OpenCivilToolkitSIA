---
erzeugt: 9f0deb17f4f1
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.5.2, (55); 4.3.5.5"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.5.2, (55); 4.3.5.5

*In der Herleitung: «Kraft einer Wand: ihr Schubfluss über ihre Länge»*

$$
V_{Ed} = |q| \cdot l
$$

## Im Code

- [[opencivil.nachweis.schubwandnachweis#Schubwandnachweis|Schubwandnachweis._protokoll_ansatz]]

## Themen

- [[Querkraft und Torsion]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Jede gezeichnete Wand ist dort geteilt, wo eine andere auf ihr endet oder
sie kreuzt: «Wand 1.1», «Wand 1.2». Jede so geteilte Wand bekommt aus der
Verteilung einen Schubfluss $q$ in kN/m, überall auf ihr derselbe: den
Anteil der Querkraft, $V_i/l$, und den Umlauf der Zellen, an die sie grenzt.
Mal ihre Länge $l$ wird daraus ihre Kraft, die ihr Fachwerk tragen muss
(siehe [[Widerstand einer Wand (Fachwerk, ihre Länge l als Hebelarm)]]).

Bei einer Zelle rechnet die Norm selbst so: (55) schreibt den Umlauf der
Torsion als Kraft je Wand, $T_d/(2 A_k) \cdot z_i$ mit der Länge $z_i$ der
Wand, und 4.3.5.5 zählt sie mit der Kraft aus der Querkraft zusammen. Ein
Deckel über zwei Zellen ist so zwei Wände, jede mit ihrem Fluss, ihrer
Kraft und ihrem Widerstand (Benutzer, 2026-11-18). Bis dahin war er eine
Wand, die mit ihrem stärkeren Fluss über die ganze Länge zählte.
