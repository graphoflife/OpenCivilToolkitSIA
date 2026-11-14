---
erzeugt: 5390cfc7da77
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.6.4.6, Figur 25"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.6.4.6, Figur 25

*In der Herleitung: «Breite des Stützstreifens in y, senkrecht zum Rand»*

$$
b_{s,y} = \min\left[b_s;\ b_{sr,y}\right]
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $b_s$ | Breite des Stützstreifens | mm | [[Breite des Stützstreifens]] |
| $b_{sr,y}$ | Grenze der Breite des Stützstreifens am Plattenrand | mm | [[Breite des Stützstreifens am Plattenrand]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
b_{s,y} = \min\left[b_s;\ b_{sr,y}\right] = \min\left[2310\,\mathrm{mm};\ 1550\,\mathrm{mm}\right] = 1550\,\mathrm{mm}
$$

## Gebraucht von

- [[Mittleres Moment im Stützstreifen]]

## Im Code

- [[opencivil.durchstanzen.nachweis#Durchstanzen._breite_am_rand|Durchstanzen._breite_am_rand]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

An einer Randstütze begrenzt der Rand den Streifen, der senkrecht zu ihm
läuft (4.3.6.4.6, Figur 25): seine Breite ist die kleinere von
[[Breite des Stützstreifens|b_s]] und
[[Breite des Stützstreifens am Plattenrand|b_sr]]. Der Streifen parallel zum
Rand ist frei und behält $b_s$. Die Breite geht in das
[[Mittleres Moment im Stützstreifen|mittlere Moment]] ein: ein schmalerer
Streifen gibt bei gleicher Exzentrizität ein grösseres Moment.

Beispiel: Randstütze 300 × 300 mm direkt am Rand, $b_s$ = 2310 mm. Dann ist
$b_{sr}$ = 300 + 2 · (300 + 0) = 900 mm, und der Streifen senkrecht zum Rand
ist 900 mm breit.
