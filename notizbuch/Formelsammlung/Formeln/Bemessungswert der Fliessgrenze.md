---
erzeugt: f290d5ac5082
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 2.4.2.5"
---
> [!info] Normstelle
> SIA 262:2025, 2.4.2.5

$$
f_{yd} = \frac{f_{yk}}{\gamma_s}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $f_{yk}$ | Charakteristische Fliessgrenze | N/mm² | Vorgabe |
| $\gamma_s$ | Teilsicherheitsbeiwert für Betonstahl | – | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
f_{yd} = \frac{f_{yk}}{\gamma_s} = \frac{500\,\mathrm{N}/\mathrm{mm}^{2}}{1.15} = 435\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Gebraucht von

- [[Dehnung auf halber Höhe]]
- [[Fliessdehnung]]
- [[Widerstand der Bügel]]
- [[Zulässige Stahlspannung]]

## Im Code

- [[opencivil.material.betonstahl]]

## Themen

- [[Betonstahl]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Fliessgrenze trennt den elastischen Bereich, in dem der Stahl nach
Entlastung zurückfedert, vom Fliessen, in dem er sich bleibend dehnt. Für die
Tragsicherheit wird die charakteristische Fliessgrenze $f_{yk}$ -- auch sie ein
5-%-Fraktil -- durch den Teilsicherheitsbeiwert $\gamma_s$ geteilt. Stahl
streut weit weniger als Beton; darum ist $\gamma_s$ kleiner als $\gamma_c$.

$f_{yd}$ ist das Plateau der [[Bilineare Beziehung des Betonstahls|bilinearen Beziehung]]
und die Spannung der Zugbewehrung, sobald sie fliesst -- in der Handrechnung
der Resistenzlinie ebenso wie im Querschnittslöser.
