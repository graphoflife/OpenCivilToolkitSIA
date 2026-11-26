---
erzeugt: e2ed47f1f06d
art: formel
tags: [formel]
normstelle: "SIA 263:2013, 4.5.2.2, (9); 4.5.2.3, (10)"
---
> [!info] Normstelle
> SIA 263:2013, 4.5.2.2, (9); 4.5.2.3, (10)

*In der Herleitung: «Beiwert beim Kippen»*

$$
\Phi_{D} = 0.5 \cdot \left(1 + \alpha_{D} \cdot \left(\bar{\lambda}_{D} - 0.4\right) + \bar{\lambda}_{D}^2\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\alpha_{D}$ | Imperfektionsbeiwert beim Kippen | – | Zwischenwert |
| $\bar{\lambda}_{D}$ | Schlankheit beim Kippen | – | [[Schlankheit beim Kippen]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  \Phi_{D} &= 0.5 \cdot \left(1 + \alpha_{D} \cdot \left(\bar{\lambda}_{D} - 0.4\right) + \bar{\lambda}_{D}^2\right) \\
  &= 0.5 \cdot \left(1 + 0.21 \cdot \left(0.537 - 0.4\right) + 0.537^2\right) \\
  &= 0.659
\end{aligned}
$$

## Im Code

- [[opencivil.nachweis.qa_stahl_stabilitaet#_Herleitung.kippen|_Herleitung.kippen]]

## Themen

- [[Knicken und Kippen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie beim Knicken – siehe [[Beiwert Φ beim Knicken]] –, aber mit zwei
anderen Zahlen: abgemindert wird erst über $\bar{\lambda}_D = 0.4$, und
die Imperfektion ist die eines Walzprofils, $\alpha_D = 0.21$. Ein
gewalzter Träger kippt also gutmütiger, als ein gedrückter Stab
gleicher Schlankheit knickt.

Kippen lässt das Werkzeug nur Walzprofile und Rohre; ein geschweisster
Träger hätte ein grösseres $\alpha_D$.
