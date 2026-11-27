---
erzeugt: 410bbc041213
art: formel
tags: [formel]
normstelle: "SIA 264:2014, 5.3.1.2, (13)"
---
> [!info] Normstelle
> SIA 264:2014, 5.3.1.2, (13)

*In der Herleitung: «Querschnittsparameter, von 0.2 bis 0.9»*

$$
\delta = \frac{N_{pl,a,Rd}}{N_{pl,Rd}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $N_{pl,a,Rd}$ | Normalkraftwiderstand des Profils | kN | Zwischenwert |
| $N_{pl,Rd}$ | Plastischer Normalkraftwiderstand | kN | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\delta = \frac{N_{pl,a,Rd}}{N_{pl,Rd}} = \frac{5042.4\,\mathrm{kN}}{9563.9\,\mathrm{kN}} = 0.527
$$

## Im Code

- [[opencivil.nachweis.qa_verbund_stuetze#_Querschnitt|_Querschnitt._normalkraft]]

## Themen

- [[Verbundstütze]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Querschnittsparameter sagt, welchen Teil des plastischen
Normalkraftwiderstands das Profil allein trägt. Unter 0.2 trägt fast nur
der Beton: die Stütze ist dann eine Stahlbetonstütze mit einem Profil darin
und wird so nachgewiesen. Über 0.9 trägt fast nur das Profil: dann ist sie
eine Stahlstütze. Nur dazwischen gelten die Regeln der Verbundstütze
(SIA 264, 5.3.1.2); ausserhalb rechnet das Werkzeug nicht weiter und sagt
am Ort, wie die Stütze nachzuweisen ist. Den Nenner gibt
[[Plastischer Normalkraftwiderstand im Verbund]] oder, im gefüllten Rohr,
[[Plastischer Normalkraftwiderstand eines gefüllten Rohrs]].
