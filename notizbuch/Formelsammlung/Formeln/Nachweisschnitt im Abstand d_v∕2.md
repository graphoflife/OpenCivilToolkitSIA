---
erzeugt: 2c2a3efe886b
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.6.2.2, Figur 22b"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.6.2.2, Figur 22b

*In der Herleitung: «Nachweisschnitt im Abstand d\_v/2»*

$$
u_0 = 2 \cdot \left(b_x + b_y\right) + \pi \cdot d_v
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $b_x$ | Abmessung der Stütze in x | mm | Vorgabe |
| $b_y$ | Abmessung der Stütze in y | mm | Vorgabe |
| $d_v$ | – | mm | [[Wirksame Höhe ohne Abzug]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
u_0 = 2 \cdot \left(b_x + b_y\right) + \pi \cdot d_v = 2 \cdot \left(400\,\mathrm{mm} + 400\,\mathrm{mm}\right) + \pi \cdot 234\,\mathrm{mm} = 2335\,\mathrm{mm}
$$

## Gebraucht von

- [[Nachweisschnitt ohne das, was nicht zählt]]

## Im Code

- [[opencivil.durchstanzen.nachweis#Durchstanzen._nachweisschnitt|Durchstanzen._nachweisschnitt]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Nachweisschnitt umschliesst die gestützte Fläche im Abstand $d_v/2$
(Figur 22). An einer Rechteckstütze besteht er aus vier Geraden und vier
Viertelkreisen, an einer Rundstütze aus einem Kreis, an einer Ovalstütze aus
zwei Geraden und zwei Halbkreisen. Liegt ein Plattenrand nahe, endet der
Schnitt am Rand, wenn er so kürzer ist. Was davon nicht zählt, steht in
[[Nachweisschnitt ohne das, was nicht zählt]].
