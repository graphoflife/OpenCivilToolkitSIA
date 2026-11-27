---
erzeugt: 887e5dd9ae98
art: formel
tags: [formel]
normstelle: "SIA 264:2014, 5.3.4.1, (24); SIA 263:2013, 5.1.9.1"
---
> [!info] Normstelle
> SIA 264:2014, 5.3.4.1, (24); SIA 263:2013, 5.1.9.1

*In der Herleitung: «Dasselbe für die Imperfektion, mit ω = 1»*

$$
k_{0,y} = \frac{1}{1 - |N_{Ed}| / N_{cr,eff,y}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\vert N_{Ed}\vert $ | Druckkraft | kN | Zwischenwert |
| $N_{cr,eff,y}$ | Kritische Normalkraft für die Bemessung | kN | [[Kritische Normalkraft einer Verbundstütze]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
k_{0,y} = \frac{1}{1 - |N_{Ed}| / N_{cr,eff,y}} = \frac{1}{1 - 6000\,\mathrm{kN} / 24776.6\,\mathrm{kN}} = 1.32
$$

## Gebraucht von

- [[Moment 2. Ordnung einer Verbundstütze]]

## Im Code

- [[opencivil.nachweis.qa_verbund_stuetze#_Fall._zweite_ordnung|_Fall._zweite_ordnung]]

## Themen

- [[Verbundstütze]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die [[Ersatzimperfektion einer Verbundstütze|Ersatzimperfektion]] ist eine
Vorkrümmung über die ganze Länge. Ihr Moment N_Ed · e₀ ist in der Mitte am
grössten, wie unter einer Querlast; darum wächst es mit ω = 1. Diese
Unterscheidung trifft das Werkzeug nach Vorgabe; sie steht im [[TODO]].
