---
erzeugt: e12954124419
art: formel
tags: [formel]
normstelle: "SIA 266:2015, 4.3.2.2, Gl. (14)"
---
> [!info] Normstelle
> SIA 266:2015, 4.3.2.2, Gl. (14)

*In der Herleitung: «Widerstand gegen Gleiten: Gl. (14), V\_d / N\_xd ≤ μ\_d, nach V\_d aufgelöst»*

$$
V_{Rd} = \mu_d \cdot N_{xd}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\mu_d$ | Reibungsbeiwert der Lagerfugen | – | Zwischenwert |
| $N_{xd}$ | Normalkraft am Fuss des Pfeilers | kN | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
V_{Rd} = \mu_d \cdot N_{xd} = 0.6 \cdot 51.1\,\mathrm{kN} = 30.7\,\mathrm{kN}
$$

## Im Code

- [[opencivil.mauerwerk.schub#Gleiten.gedrueckt|Gleiten.gedrueckt]]

## Themen

- [[Mauerwerk]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

In einer Lagerfuge hält nur Reibung: sie gleitet, sobald die Querkraft
grösser wird als $\mu_d$ mal die Normalkraft, die sie zusammendrückt
(4.3.2.2, Gl. (14)). Kohäsion zählt nicht (4.1.2). Die Norm schreibt das
Verhältnis $V_d/N_{xd} \le \mu_d$; nach $V_d$ aufgelöst steht es als
Widerstand da, und der Erfüllungsgrad ist $\mu_d N_{xd}/V_d$.

Gerechnet wird am Fuss des Pfeilers, mit der Normalkraft dort samt dem
Gewicht des Pfeilers – nach Vorgabe, nicht nachgeschlagen; offen in
[[TODO]].
