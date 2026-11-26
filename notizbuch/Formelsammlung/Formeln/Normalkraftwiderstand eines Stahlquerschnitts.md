---
erzeugt: 9ca2c1194989
art: formel
tags: [formel]
normstelle: ["SIA 263:2013, 5.1.2.1, (38)", "SIA 263:2013, 5.3.2, (55); 4.5.3"]
---
> [!info] Normstellen
> SIA 263:2013, 5.1.2.1, (38) · SIA 263:2013, 5.3.2, (55); 4.5.3

*In der Herleitung: «Zugwiderstand, am gezeichneten Querschnitt»*

$$
N_{Rd}^{+} = \frac{f_y \cdot A}{\gamma_{M1}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $f_y$ | Streckgrenze | N/mm² | Vorgabe |
| $A$ | Fläche aus Baustahl | mm² | Zwischenwert |
| $\gamma_{M1}$ | Widerstandsbeiwert für Festigkeits- und Stabilitätsnachweise | – | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
N_{Rd}^{+} = \frac{f_y \cdot A}{\gamma_{M1}} = \frac{355\,\mathrm{N}/\mathrm{mm}^{2} \cdot 15604\,\mathrm{mm}^{2}}{1.05} = 5275.5\,\mathrm{kN}
$$

## Im Code

- [[opencivil.nachweis.qa_stahl_kennzahlen#KennzahlenStahlQA._summe|KennzahlenStahlQA._summe]]

## Themen

- [[Kennzahlen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Gezogen oder gedrückt fliesst jede Faser bei $f_y$; zusammen trägt der
Querschnitt $f_y \cdot A$. Beim Zug ist das (38), am gezeichneten
Querschnitt: einen geschwächten Nettoquerschnitt nach (39) prüft das
Werkzeug nicht.

Beim Druck entscheidet die Klasse der gedrückten Bleche. In den Klassen 1
bis 3 trägt die ganze Fläche, in Klasse 4 nur die wirksame $A_{eff}$ nach
(55), ohne die Streifen, die beulen – siehe
[[Mitwirkende Breite eines Blechs]].

Das ist der Widerstand des Querschnitts. Knicken gehört dem Stab und steht
nicht hier. Mit mehreren Stählen rechnet jede Gruppe mit ihrer
Fliessgrenze; dann steht statt der Formel eine Tabelle.
