---
erzeugt: c2c3abe3865a
art: formel
tags: [formel]
normstelle: "SIA 264:2014, 5.3.2.4, (14); 5.3.2.5"
---
> [!info] Normstelle
> SIA 264:2014, 5.3.2.4, (14); 5.3.2.5

*In der Herleitung: «Plastischer Normalkraftwiderstand, Teil für Teil – der Beton im gefüllten Rohr mit 1.0»*

$$
N_{pl,Rd} = A_a\, f_{yd} + A_c\, 1.0\, f_{cd} + A_s\, f_{sd}
$$

## Im Code

- [[opencivil.nachweis.qa_verbund_stuetze#_Querschnitt|_Querschnitt._normalkraft]]

## Themen

- [[Verbundstütze]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Im gefüllten Rohr ist der Beton rundum eingeschlossen. (14) darf seinen
Beton darum mit 1.0 statt 0.85 rechnen (5.3.2.5), und ebenso die
Spannungsblöcke für μ_d (5.3.4.4). Das gilt für die Verbundstütze; die
Kennzahlen des Querschnitts rechnen weiter mit 0.85, siehe
[[Plastischer Normalkraftwiderstand im Verbund]].
