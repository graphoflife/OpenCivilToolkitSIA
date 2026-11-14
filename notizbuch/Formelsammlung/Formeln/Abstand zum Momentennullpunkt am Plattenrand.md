---
erzeugt: 4f567e74b473
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.6.4.8"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.6.4.8

*In der Herleitung: «Abstand zum Momentennullpunkt in y: am Plattenrand mindestens 2/3 · b\_sr»*

$$
r_{sy} = \max\left[r_{sy};\ \frac{2}{3} \cdot b_{sr,y}\right]
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $r_{sy}$ | Abstand zum Momentennullpunkt in y | m | Vorgabe |
| $b_{sr,y}$ | Grenze der Breite des Stützstreifens am Plattenrand | mm | [[Breite des Stützstreifens am Plattenrand]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
r_{sy} = \max\left[r_{sy};\ \frac{2}{3} \cdot b_{sr,y}\right] = \max\left[0.4\,\mathrm{m};\ \frac{2}{3} \cdot 900\,\mathrm{mm}\right] = 600\,\mathrm{mm}
$$

## Im Code

- [[opencivil.durchstanzen.nachweis#Durchstanzen._r_s_am_rand|Durchstanzen._r_s_am_rand]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

In Stufe 3 kommt $r_s$ aus einer Berechnung nach der Elastizitätstheorie. An
Rand- und Eckstützen verlangt 4.3.6.4.8 senkrecht zum Rand mindestens
$\tfrac{2}{3} \cdot b_{sr}$, mit $b_{sr}$ aus der
[[Breite des Stützstreifens am Plattenrand]]. Ein kleinerer eingegebener
Wert wird darum angehoben, und die Herleitung zeigt es; der Streifen parallel
zum Rand behält den eingegebenen Wert.

Beispiel: Randstütze 300 × 300 mm direkt am Rand, eingegeben $r_{sy}$ =
400 mm. $b_{sr}$ = 900 mm, also gilt $r_{sy}$ = 600 mm.
