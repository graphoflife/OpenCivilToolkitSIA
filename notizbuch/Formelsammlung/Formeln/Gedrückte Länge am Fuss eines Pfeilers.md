---
erzeugt: bc0c1dafe087
art: formel
tags: [formel]
normstelle: "SIA 266:2015, 4.3.3.1, Gl. (17)"
---
> [!info] Normstelle
> SIA 266:2015, 4.3.3.1, Gl. (17)

*In der Herleitung: «Gedrückte Länge am Fuss»*

$$
l_2 = l_w - \frac{2 \cdot M_{z2d}}{N_{xd}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $l_w$ | Breite des Pfeilers | mm | Zwischenwert |
| $M_{z2d}$ | Moment in der Wandebene am Fuss, Betrag | kNm | Zwischenwert |
| $N_{xd}$ | Normalkraft am Fuss des Pfeilers | kN | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
l_2 = l_w - \frac{2 \cdot M_{z2d}}{N_{xd}} = 800\,\mathrm{mm} - \frac{2 \cdot 8\,\mathrm{kNm}}{51.1\,\mathrm{kN}} = 487\,\mathrm{mm}
$$

## Gebraucht von

- [[Widerstand der Druckstrebe in einem Pfeiler]]

## Im Code

- [[opencivil.mauerwerk.nachweise#gedrueckte_laenge|gedrueckte_laenge]]

## Themen

- [[Mauerwerk]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ein Moment in der Ebene der Wand schiebt die Resultierende der Normalkraft
am Fuss des Pfeilers um $M_{z2d}/N_{xd}$ aus seiner Mitte. Gedrückt ist
dann nur die Länge, über der die Resultierende mittig steht – ein
Spannungsblock, wie quer zur Wand bei einer Ausmitte: $l_2$ (4.3.2.2,
Figur 8). Ist $l_2$ null oder kleiner, liegt die Resultierende ausserhalb
des Pfeilers: er kippt, und es bleibt kein Widerstand.

Das Moment kommt aus der Scheibe: die waagrechten Lasten über den
Öffnungen und das Moment der lotrechten Lasten neben den Mitten der
Pfeiler. Gerechnet wird am Fuss des Pfeilers, wo das Moment eines
Kragarms am grössten ist – nach Vorgabe, nicht nachgeschlagen; offen in
[[TODO]].
