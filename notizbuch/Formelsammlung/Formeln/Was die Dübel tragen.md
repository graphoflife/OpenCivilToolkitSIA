---
erzeugt: 46959ee39fa9
art: formel
tags: [formel]
normstelle: "SIA 264:2014, 6.1.1.6; 5.1.2.1"
---
> [!info] Normstelle
> SIA 264:2014, 6.1.1.6; 5.1.2.1

*In der Herleitung: «Was die Dübel tragen – weniger als N\_c,f»*

$$
F_D = N \cdot P_{Rd}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $N$ | Dübel zwischen dem Schnitt und dem Momentennullpunkt | – | Zwischenwert |
| $P_{Rd}$ | Schubwiderstand eines Kopfbolzendübels | kN | [[Schubwiderstand eines Kopfbolzendübels]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
F_D = N \cdot P_{Rd} = 25 \cdot 81.7\,\mathrm{kN} = 2041.4\,\mathrm{kN}
$$

## Im Code

- [[opencivil.nachweis.qa_verbund#VerbundBiegungQA._teilverduebelt|VerbundBiegungQA._teilverduebelt]]

## Themen

- [[Verbundquerschnitt]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Sind es weniger Dübel, als die [[Dübel für volle Verdübelung]] verlangen,
trägt der Beton ausserhalb der Profile nur, was die $N$ Dübel bis zum
Momentennullpunkt übertragen. Beton und Stahl haben dann je ihre eigene
Nulllinie, beide mit derselben Richtung, und zwischen ihnen gleitet die
Fuge. Der Biegewiderstand dieses Zustands ist kleiner als der mit voller
Verdübelung; am Momentennullpunkt trägt der Beton nichts (nach Vorgabe).
