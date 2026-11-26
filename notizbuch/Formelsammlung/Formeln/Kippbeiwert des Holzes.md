---
erzeugt: 26c1707c7683
art: formel
tags: [formel]
normstelle: "SIA 265:2012, 4.2.9.2, (39)"
---
> [!info] Normstelle
> SIA 265:2012, 4.2.9.2, (39)

*In der Herleitung: «λ\_rel,m zwischen 0.75 und 1.4»*

$$
k_m = 1.56 - 0.75 \cdot \lambda_{rel,m}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\lambda_{rel,m}$ | Relative Schlankheit beim Kippen | – | [[Relative Schlankheit beim Kippen von Holz]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
k_m = 1.56 - 0.75 \cdot \lambda_{rel,m} = 1.56 - 0.75 \cdot 0.799 = 0.961
$$

## Im Code

- [[opencivil.nachweis.qa_holz_stabilitaet#_Herleitung|_Herleitung._kippen]]

## Themen

- [[Knicken und Kippen eines Holzstabs]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ein hoher, schmaler Träger weicht unter Biegung seitlich aus und verdreht
sich dabei. $k_m$ mindert die Biegefestigkeit dafür, wie $k_c$ die
Druckfestigkeit beim Knicken: eins bis $\lambda_{rel,m} = 0.75$, dann
linear fallend bis 1.4, darüber $1/\lambda_{rel,m}^2$ – dort entscheidet
allein die [[Kippspannung eines Rechtecks aus Holz|Kippspannung]].
