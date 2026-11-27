---
erzeugt: 4054dbfe6432
art: formel
tags: [formel]
normstelle: "SIA 264:2014, 5.3.2.7, (16); 5.3.2.1"
---
> [!info] Normstelle
> SIA 264:2014, 5.3.2.7, (16); 5.3.2.1

*In der Herleitung: «Bezogene Schlankheit um z, höchstens 2»*

$$
\bar{\lambda}_{z} = \sqrt{\frac{N_{pl,Rk}}{N_{cr,z}}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $N_{pl,Rk}$ | Plastischer Normalkraftwiderstand mit γ = 1 | kN | Zwischenwert |
| $N_{cr,z}$ | Kritische Normalkraft | kN | [[Kritische Normalkraft einer Verbundstütze]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\bar{\lambda}_{z} = \sqrt{\frac{N_{pl,Rk}}{N_{cr,z}}} = \sqrt{\frac{11885.5\,\mathrm{kN}}{20438.6\,\mathrm{kN}}} = 0.763
$$

## Im Code

- [[opencivil.nachweis.qa_verbund_stuetze#_Fall|_Fall._knicken]]

## Themen

- [[Verbundstütze]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die bezogene Schlankheit vergleicht, was der Querschnitt plastisch trägt,
mit der idealen Knicklast (16). Der Widerstand rechnet dabei mit den
charakteristischen Festigkeiten, ohne Widerstandsbeiwerte, den Beton mit
demselben Faktor wie im Bemessungswert.

Das vereinfachte Verfahren gilt bis λ̄ = 2 (5.3.2.1); darüber rechnet das
Werkzeug die Stütze nicht und sagt es am Ort. Aus λ̄ folgt mit der Kurve der
Tabelle 7 die Abminderung: [[Beiwert Φ beim Knicken]] und
[[Abminderungsfaktor beim Knicken und Kippen]].
