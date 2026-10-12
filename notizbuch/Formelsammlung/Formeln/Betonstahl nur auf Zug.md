---
erzeugt: 471ee123299c
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Werkstoffgesetze im Gebrauchszustand: Stahl, nur auf Zug»*

$$
\sigma_s = \begin{cases} \min\left(E_s \cdot \varepsilon_s;\ f_{yk}\right) & \varepsilon_s > 0 \\[1ex] 0 & \varepsilon_s \le 0 \quad (\text{gedrückt: weggelassen}) \end{cases}
$$

## Im Code

- [[opencivil.nachweis.rechenwahl#protokoll_gesetze|protokoll_gesetze]]

## Themen

- [[Stahlspannung aus Rissbreite]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Stahl, wie die Handrechnung ihn sieht: auf Zug bilinear bis zum Plateau,
auf Druck gar nicht. Gedrückte Bewehrung wird weggelassen -- das ist die
Vereinfachung, mit der die Resistenzlinie aus Handrechnung entsteht, und auf
der sicheren Seite.

Wählt ein Kapitel die Rechenart «Handrechnung», rechnet auch sein
Querschnittslöser so -- das gibt es nur bei den Stahlspannungen im Gebrauch.
Beim Knicken und in den Spannung-Dehnung-Analysen steht die Handrechnung seit
2026-10-12 nicht mehr zur Wahl: dort wird die Normalkraft Ebene für Ebene
genau gerechnet, und ein Polygon aus Eckpunkten wäre nur eine schlechtere
0.85·x-Vereinfachung.
