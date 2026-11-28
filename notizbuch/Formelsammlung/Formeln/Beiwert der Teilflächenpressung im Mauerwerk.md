---
erzeugt: b899192ef035
art: formel
tags: [formel]
normstelle: "SIA 266:2015, 4.2.1.2, Gl. (4), Figur 2"
---
> [!info] Normstelle
> SIA 266:2015, 4.2.1.2, Gl. (4), Figur 2

*In der Herleitung: «Beiwert der Teilflächenpressung»*

$$
k_m = \min\left[0.5 \cdot \left(1 + \sqrt{\frac{A_1}{A_0}}\right);\ 1.5\right]
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $A_1$ | Fläche mit demselben Schwerpunkt | mm² | Zwischenwert |
| $A_0$ | Fläche des Auflagers | mm² | [[Fläche des Auflagers]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
k_m = \min\left[0.5 \cdot \left(1 + \sqrt{\frac{A_1}{A_0}}\right);\ 1.5\right] = \min\left[0.5 \cdot \left(1 + \sqrt{\frac{26250\,\mathrm{mm}^{2}}{26250\,\mathrm{mm}^{2}}}\right);\ 1.5\right] = 1
$$

## Gebraucht von

- [[Widerstand eines Sturzauflagers]]

## Im Code

- [[opencivil.mauerwerk.nachweise#Teilflaechen.stelle|Teilflaechen.stelle]]

## Themen

- [[Mauerwerk]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Drückt eine Last nur auf einen Teil $A_0$ einer Fläche, verteilt sie sich
darunter auf eine grössere Fläche $A_1$, und das Mauerwerk um die
Lastfläche hält sie seitlich zusammen: dort trägt es mehr als $f_{xd}$.
Gl. (4) gibt dafür den Faktor $k_m = 0.5 \cdot (1 + \sqrt{A_1/A_0})$,
höchstens 1.5, für eine Last, die mittig auf der grösseren Fläche steht –
so zeigt sie Figur 2.

Am Auflager eines Sturzes fehlt das Mauerwerk auf einer Seite, dort ist
die Öffnung. Das Werkzeug setzt darum $A_1 = A_0$ und rechnet mit
$k_m = 1$ – nach Vorgabe, nicht nachgeschlagen.
