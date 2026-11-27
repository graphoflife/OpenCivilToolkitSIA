---
erzeugt: a6fd44c4d9c0
art: formel
tags: [formel]
normstelle: "SIA 264:2014, 5.4.4.3"
---
> [!info] Normstelle
> SIA 264:2014, 5.4.4.3

*In der Herleitung: «Schlankheit der Decke»*

$$
L/d_p = \frac{L}{d_p}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $L$ | Spannweite | m | Zwischenwert |
| $d_p$ | Statische Höhe der Decke | mm | [[Statische Höhe einer Blechverbunddecke]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
L/d_p = \frac{L}{d_p} = \frac{3\,\mathrm{m}}{108.9\,\mathrm{mm}} = 27.5
$$

## Im Code

- [[opencivil.nachweis.qa_blechverbund#KennzahlenBlechQA|KennzahlenBlechQA._schlankheit]]

## Themen

- [[Blechverbunddecke]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Bis $L/d_p = 26$ muss die Durchbiegung einer Blechverbunddecke nicht
gerechnet werden (SIA 264, 5.4.4.3). Darüber ist sie zu rechnen, mit einer
Steifigkeit zwischen der des gerissenen und der des ungerissenen
Querschnitts; das tut das Werkzeug für die Decke noch nicht und sagt es
grau.

$L$ ist die Spannweite des Felds, wie sie eingegeben ist – auch in einem
durchlaufenden Feld, nicht die verkürzte der
[[Schublänge einer Blechverbunddecke|Schublänge]].
