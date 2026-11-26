---
erzeugt: 1e64a35645d9
art: formel
tags: [formel]
normstelle: ["SIA 262:2025, 2.4.2.5, (4)", "SIA 262:2025, 2.4.2.5, (5); 4.2.3.1, Tabelle 10"]
---
> [!info] Normstellen
> SIA 262:2025, 2.4.2.5, (4) · SIA 262:2025, 2.4.2.5, (5); 4.2.3.1, Tabelle 10

*In der Herleitung: «Bemessungswert der Fliessgrenze»*

$$
f_{yd} = \frac{f_{yk}}{\gamma_s}
$$

*In der Herleitung: «Bemessungswert der Fliessgrenze»*

$$
f_{pd} = \frac{f_{p0.1k}}{\gamma_s}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $f_{yk}$ | Charakteristische Fliessgrenze | N/mm² | Vorgabe |
| $\gamma_s$ | Teilsicherheitsbeiwert für Betonstahl | – | Vorgabe |
| $f_{p0.1k}$ | Fliessgrenze (0.1-%-Dehngrenze) | N/mm² | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
f_{yd} = \frac{f_{yk}}{\gamma_s} = \frac{500\,\mathrm{N}/\mathrm{mm}^{2}}{1.15} = 435\,\mathrm{N}/\mathrm{mm}^{2}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
f_{pd} = \frac{f_{p0.1k}}{\gamma_s} = \frac{1600\,\mathrm{N}/\mathrm{mm}^{2}}{1.15} = 1391\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Gebraucht von

- [[Biegewiderstand im Stützstreifen]]
- [[Druckzonenhöhe aus dem Kräftegleichgewicht]]
- [[Druckzonenhöhe im Stützstreifen]]
- [[Durchstanzbewehrung an der Fliessgrenze]]
- [[Fliessdehnung]]
- [[Grenze der bezogenen Druckzonenhöhe]]
- [[Grösste Kraft eines geneigten Spannglieds]]
- [[Nominelle Dehnung der Zugbewehrung]]
- [[Plattenrotation]]
- [[Querkraftwiderstand des Tragglieds]]
- [[Spannung in der Durchstanzbewehrung]]
- [[Widerstand der Bügel]]
- [[Widerstand der Wendel]]
- [[Zulässige Stahlspannung]]

## Im Code

- [[opencivil.material.betonstahl]]
- [[opencivil.material.spannstahl]]

## Themen

- [[Betonstahl]]
- [[Spannstahl]]

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
