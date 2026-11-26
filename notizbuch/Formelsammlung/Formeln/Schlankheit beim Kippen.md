---
erzeugt: 7c928f514b6a
art: formel
tags: [formel]
normstelle: "SIA 263:2013, 4.5.2.2, (9); 4.5.2.3, (10)"
---
> [!info] Normstelle
> SIA 263:2013, 4.5.2.2, (9); 4.5.2.3, (10)

*In der Herleitung: «Schlankheit beim Kippen, W nach der Klasse»*

$$
\bar{\lambda}_{D} = \sqrt{\frac{W_{pl} \cdot f_{y}}{M_{cr}}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $W_{pl}$ | Plastisches Widerstandsmoment | cm³ | Zwischenwert |
| $f_{y}$ | Streckgrenze | N/mm² | Vorgabe |
| $M_{cr}$ | Ideelles Kippmoment | kNm | [[Ideelles Kippmoment]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\bar{\lambda}_{D} = \sqrt{\frac{W_{pl} \cdot f_{y,\text{S355}}}{M_{cr}}} = \sqrt{\frac{3513.8\,\mathrm{cm}^{3} \cdot 355\,\mathrm{N}/\mathrm{mm}^{2}}{4323.1\,\mathrm{kNm}}} = 0.537
$$

## Gebraucht von

- [[Beiwert Φ beim Kippen]]

## Im Code

- [[opencivil.nachweis.qa_stahl_stabilitaet#_Herleitung.kippen|_Herleitung.kippen]]

## Themen

- [[Knicken und Kippen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie die [[Schlankheit beim Knicken]], nur mit Momenten: die Wurzel aus
dem Moment, bei dem der Querschnitt fliesst, durch das
[[Ideelles Kippmoment|ideelle Kippmoment]]. $W$ folgt der Klasse –
plastisch, elastisch oder wirksam –, gerechnet mit $f_y$, ohne
$\gamma_{M1}$.
