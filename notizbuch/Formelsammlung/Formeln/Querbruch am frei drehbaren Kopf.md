---
erzeugt: 352d5df20fd2
art: formel
tags: [formel]
normstelle: "SIA 267:2013, 9.4.4.2.2"
---
> [!info] Normstelle
> SIA 267:2013, 9.4.4.2.2

*In der Herleitung: «Frei drehbarer Kopf: der ganze Pfahl um s\_r gedreht, oder ein Gelenk in s\_h; s ab Kopf, e = M\_Ed / H\_Ed»*

$$
H \cdot \left|s_r + e\right| = \int_0^L p_{E,k} \cdot \left|s - s_r\right| ds \qquad H \cdot \left|s_h + e\right| = M_R + \int_0^{s_h} p_{E,k} \cdot \left(s_h - s\right) ds
$$

## Im Code

- [[opencivil.pfahl.quer#AeussererQuerwiderstand._brueche|AeussererQuerwiderstand._brueche]]

## Themen

- [[Äusserer Pfahlwiderstand quer]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Norm verlangt den Widerstand quer aus dem Erdwiderstand und dem inneren
Widerstand des Pfahls (SIA 267:2013, 9.4.4.2.2), ohne einen Weg
vorzugeben. Das Werkzeug sucht ihn mit Bruchmechanismen, wie sie für kurze
und lange Pfähle üblich sind -- nach Vorgabe, nicht nachgeschlagen:

- Kurz dreht sich der ganze Pfahl starr um einen Punkt s_r: darüber drückt
  er vorne gegen den Boden, darunter hinten.
- Lang knickt er in einem Gelenk s_h, wo das Moment den Biegewiderstand
  M_R erreicht; darunter steht er still.

Je Mechanismus leistet die Last dieselbe Arbeit, die Boden und Gelenk
verzehren; gilt die Lage, bei der H am kleinsten wird. Ein Moment am Kopf
zählt als Hebel e = M_Ed / H_Ed ([[Hebel des Moments am Pfahlkopf]]).

Mit p_E überall gleich c und e = 0 wird lang H = √(2 · M_R · c), kurz
H = (√2 − 1) · c · L mit s_r = L / √2. Für c = 200 kN/m und M_R = 500 kNm:
s_h = 2.24 m und H = 447 kN -- genau dort wird die Querkraft im Pfahl null,
das Moment also am grössten.

Der kleinste Wert aller Mechanismen, mit [[Querbruch durch Verschieben]],
ist R_tr,k.
