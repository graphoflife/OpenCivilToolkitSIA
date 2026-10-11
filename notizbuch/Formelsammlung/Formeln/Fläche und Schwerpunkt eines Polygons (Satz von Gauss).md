---
erzeugt: 376c506a3a2a
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
A = \frac{1}{2} \sum_i c_i \qquad y_S = \frac{1}{6A} \sum_i (y_i + y_{i+1})\, c_i \qquad z_S = \frac{1}{6A} \sum_i (z_i + z_{i+1})\, c_i \qquad c_i = y_i\, z_{i+1} - y_{i+1}\, z_i
$$

## Im Code

- [[opencivil.querschnitt.analyse#Querschnittsanalyse.aufbau_protokollieren|Querschnittsanalyse.aufbau_protokollieren]]

## Themen

- [[Querschnittsanalyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Fläche und Schwerpunkt eines beliebigen Polygons aus seinen Ecken allein: der
Satz von Gauss verwandelt das Flächenintegral in eine Summe über die Kanten.
Jede Kante trägt mit dem Kreuzprodukt $c_i$ ihrer beiden Ecken bei -- das ist
die doppelte Fläche des Dreiecks aus Ursprung und Kante. Gegen den Uhrzeiger
umlaufen ergibt sich eine positive Fläche.

Die Formel ist exakt, wie fein oder grob das Polygon auch gezeichnet ist.
