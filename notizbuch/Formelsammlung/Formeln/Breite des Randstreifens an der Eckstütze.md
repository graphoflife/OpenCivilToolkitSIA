---
erzeugt: d31466706a6d
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.6.4.6, Figur 25"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.6.4.6, Figur 25

*In der Herleitung: «Breite des Randstreifens in x: innen die halbe, aussen bis zum zweiten Plattenrand»*

$$
b_{s,x} = \frac{\min\left[b_s;\ b_{sr,x}\right]}{2} + \min\left[\frac{\min\left[b_s;\ b_{sr,x}\right]}{2};\ \frac{b_y}{2} + a_y\right]
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $b_s$ | Breite des Stützstreifens | mm | [[Breite des Stützstreifens]] |
| $b_{sr,x}$ | Grenze der Breite des Stützstreifens am Plattenrand | mm | [[Breite des Stützstreifens am Plattenrand]] |
| $b_y$ | Abmessung der Stütze | mm | Zwischenwert |
| $a_y$ | Abstand der Stütze vom Plattenrand | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  b_{s,x} &= \frac{\min\left[b_s;\ b_{sr,x}\right]}{2} + \min\left[\frac{\min\left[b_s;\ b_{sr,x}\right]}{2};\ \frac{b_y}{2} + a_y\right] \\
  &= \frac{\min\left[2310\,\mathrm{mm};\ 900\,\mathrm{mm}\right]}{2} + \min\left[\frac{\min\left[2310\,\mathrm{mm};\ 900\,\mathrm{mm}\right]}{2};\ \frac{300\,\mathrm{mm}}{2} + 0\,\mathrm{mm}\right] \\
  &= 600\,\mathrm{mm}
\end{aligned}
$$

## Gebraucht von

- [[Mittleres Moment im Stützstreifen]]

## Im Code

- [[opencivil.durchstanzen.nachweis#Durchstanzen._breite_am_rand|Durchstanzen._breite_am_rand]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

An einer Eckstütze begrenzen beide Ränder jeden der zwei Streifen (Figur 25).
Zur Platte hin reicht er die halbe Breite, höchstens $b_{sr}/2$; zum zweiten
Rand hin nur bis zu diesem Rand, also die halbe Stütze und ihr Abstand zum
Rand, und auch das höchstens $b_{sr}/2$.

Beispiel: Eckstütze 300 × 300 mm direkt in der Ecke. $b_{sr}$ = 900 mm, zur
Platte hin 450 mm, zum zweiten Rand 150 + 0 mm: der Streifen ist 600 mm breit.
Bis 2026-11-14 lag er symmetrisch um die Stützenachse und war 900 mm breit --
das mittlere Moment kam dabei bis zu einem Drittel zu klein heraus.
