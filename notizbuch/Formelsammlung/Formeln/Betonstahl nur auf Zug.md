---
erzeugt: 46a991359149
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Werkstoffgesetze im Gebrauchszustand: Stahl, nur auf Zug»*

$$
\sigma_s(\varepsilon_s) = \begin{cases} \min(E_s\,\varepsilon_s;\ f_{yk}) & 0 < \varepsilon_s \le \varepsilon_{ud} \\[1ex] 0 & \varepsilon_s \le 0 \quad (\text{gedrückt: weggelassen}) \\[1ex] 0 & \varepsilon_s > \varepsilon_{ud} \quad (\text{jenseits der Bruchdehnung}) \end{cases}
$$

## Im Code

- [[opencivil.querschnitt.werkstoffgesetz#Gesetz.protokoll|Gesetz.protokoll]]

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

Jenseits von $\varepsilon_{ud}$ trägt er auch auf Zug nichts mehr, wie die
[[Bilineare Beziehung des Betonstahls|bilineare Beziehung]].
