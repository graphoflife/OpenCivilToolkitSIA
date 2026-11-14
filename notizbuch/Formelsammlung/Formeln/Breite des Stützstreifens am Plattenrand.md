---
erzeugt: cc5a1510cd54
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.6.4.6, Figur 25"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.6.4.6, Figur 25

*In der Herleitung: «Grenze der Breite des Stützstreifens in y am Plattenrand: zwischen den Linien unter 45° von den inneren Ecken der Stütze»*

$$
b_{sr,y} = D + 2 \cdot \left(D + a_y\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $D$ | Abmessung der Stütze | mm | Zwischenwert |
| $a_y$ | Abstand der Stütze vom Plattenrand | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
b_{sr,y} = D + 2 \cdot \left(D + a_y\right) = 450\,\mathrm{mm} + 2 \cdot \left(450\,\mathrm{mm} + 100\,\mathrm{mm}\right) = 1550\,\mathrm{mm}
$$

## Gebraucht von

- [[Abstand zum Momentennullpunkt am Plattenrand]]
- [[Breite des Randstreifens an der Eckstütze]]
- [[Breite des Stützstreifens senkrecht zum Rand]]

## Im Code

- [[opencivil.durchstanzen.nachweis#Durchstanzen._b_sr|Durchstanzen._b_sr]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

An einer Randstütze ist der Stützstreifen senkrecht zum Rand durch den Rand
begrenzt, an einer Eckstütze sind es beide (Figur 25). Die Grenze $b_{sr}$
ist die Breite am Plattenrand zwischen zwei Linien unter 45°, die von den
inneren Ecken der Stütze zum Rand laufen: die Stütze quer zum Streifen, dazu
auf jeder Seite ihre Länge längs des Streifens und ihr Abstand zum Rand.

$b_{sr}$ begrenzt die [[Breite des Stützstreifens senkrecht zum Rand]] und
die [[Breite des Randstreifens an der Eckstütze]]; in Stufe 3 gibt es den
[[Abstand zum Momentennullpunkt am Plattenrand]] vor. An einer Rundstütze
steht der Durchmesser für beide Abmessungen.
