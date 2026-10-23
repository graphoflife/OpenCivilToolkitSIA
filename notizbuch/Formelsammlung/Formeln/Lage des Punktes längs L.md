---
erzeugt: 4e4dc6333035
art: formel
tags: [formel]
normstelle: ["Kap. 8.10, Bild 8.15", "Kap. 8.10"]
---
> [!info] Normstellen
> Kap. 8.10, Bild 8.15 · Kap. 8.10

*In der Herleitung: «Abstand des Punktes K von der Ecke, längs L»*

$$
x_K = 0.13 \cdot L
$$

*In der Herleitung: «Abstand der Mitte von der Ecke, längs L»*

$$
x_M = \frac{L}{2}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $L$ | Länge des Fundaments | m | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
x_K = 0.13 \cdot L = 0.13 \cdot 2.5\,\mathrm{m} = 0.33\,\mathrm{m}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
x_M = \frac{L}{2} = \frac{40\,\mathrm{m}}{2} = 20\,\mathrm{m}
$$

## Im Code

- [[opencivil.geotechnik.setzung#Setzung._punkt|Setzung._punkt]]

## Themen

- [[Setzung]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ein starres Fundament kann der Setzungsmulde nicht folgen: es setzt sich
eben, um die mittlere Setzung $s_m$, und sein Sohldruck verteilt sich
ungleich, mit Spitzen an den Rändern. Rechnet man die Last dagegen als
schlaff, mit gleichmässiger Pressung, setzt sich ein Punkt genau um $s_m$:
der kennzeichnende Punkt K, beim Rechteck $0.13\,L$ und $0.13\,B$ von einer
Ecke (Bild 8.15). Für ein starres Fundament wird darum unter K gerechnet.

Ein schlaffes Fundament -- eine Schüttung, ein Damm -- folgt der Mulde, und
am tiefsten ist sie unter der Mitte. Dort, bei $L/2$ und $B/2$, wird für ein
schlaffes gerechnet (Kap. 8.10).
