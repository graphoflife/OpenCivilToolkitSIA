---
erzeugt: 8b96b6dae898
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.6.4.6, Figur 25"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.6.4.6, Figur 25

*In der Herleitung: «Breite des Stützstreifens in y, durch den Plattenrand begrenzt»*

$$
b_{sr,y} = \min\left[b_s;\ D + 2 \cdot \left(D + a_y\right)\right]
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $b_s$ | – | mm | [[Breite des Stützstreifens]] |
| $D$ | – | mm | Zwischenwert |
| $a_y$ | – | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  b_{sr,y} &= \min\left[b_s;\ D + 2 \cdot \left(D + a_y\right)\right] \\
  &= \min\left[2310\,\mathrm{mm};\ 450\,\mathrm{mm} + 2 \cdot \left(450\,\mathrm{mm} + 100\,\mathrm{mm}\right)\right] \\
  &= 1550\,\mathrm{mm}
\end{aligned}
$$

## Gebraucht von

- [[Mittleres Moment im Stützstreifen]]

## Im Code

- [[opencivil.durchstanzen.nachweis#Durchstanzen._b_sr|Durchstanzen._b_sr]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

An einer Randstütze ist der Stützstreifen senkrecht zum Rand durch den Rand
begrenzt, an einer Eckstütze sind es beide (Figur 25). Eingebaut ist die
Breite, die zwei Linien unter 45° von den inneren Ecken der Stütze bis zum
Plattenrand einschliessen, höchstens die
[[Breite des Stützstreifens]]. Das ist aus der Figur gelesen und nicht
nachgeschlagen; die Frage steht unter den offenen Normfragen.
