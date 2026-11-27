---
erzeugt: 5930d0da2431
art: formel
tags: [formel]
normstelle: "SIA 261:2020, 16.5.2.3, (40); nach Vorgabe, nicht nachgeschlagen"
---
> [!info] Normstelle
> SIA 261:2020, 16.5.2.3, (40); nach Vorgabe, nicht nachgeschlagen

*In der Herleitung: «Auslenkung des Dachs aus einem Geschoss – nach dem Arbeitssatz, M aus den Gewichten, a aus einer Kraft 1 am Dach»*

$$
\Delta u_i = \frac{h_i}{6 \cdot EI_i} \cdot \left(M_{u,i} \cdot (2 \cdot a_{u,i} + a_{o,i}) + M_{o,i} \cdot (a_{u,i} + 2 \cdot a_{o,i})\right) \qquad a = H - z
$$

## Im Code

- [[opencivil.erdbeben.ersatzkraft#Lauf._schwingzeit|Lauf._schwingzeit]]

## Themen

- [[Erdbeben]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die [[Auslenkung des Dachs]] folgt aus dem Arbeitssatz: das Integral von
$M \cdot a / EI$ über die Höhe. $M$ ist das Moment aus den Gewichten,
waagrecht auf ihren Decken, $a = H - z$ das aus einer Kraft 1 am Dach.
Zwischen zwei Decken greift keine Kraft an, beide Momente laufen dort
gerade, und $EI$ ist das [[Biegesteifigkeit des Kerns|des Geschosses]].
Das Integral eines Geschosses ist darum genau die Formel oben, mit den
Werten unten, an der Decke darunter, und oben, an seiner.

Mit einem $EI$ über die ganze Höhe gibt die Summe die geschlossene Formel
eines Kragarms, $\sum W_i \cdot z_i^2 \cdot (3H - z_i) / (6\,EI)$ – so
wurde bis 2026-11-27 gerechnet. Ein Beispiel von Hand: eine Kraft 1 am Dach
auf 6 m, unten $EI = 2$, oben $EI = 1$, gibt
$\int_0^3 (6 - z)^2/2\,dz + \int_3^6 (6 - z)^2\,dz = 31.5 + 9 = 40.5$.
