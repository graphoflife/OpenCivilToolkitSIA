---
erzeugt: 40e958415343
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Bewehrungsgehalt unten»*

$$
\rho_{u} = \frac{A_{s,2,x}}{b \cdot d_{2,x}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $A_{s,2,x}$ | – | mm² | [[Bewehrung der Lage]] |
| $b$ | Betrachtete Breite (x) | mm | Vorgabe |
| $d_{2,x}$ | – | mm | [[Statische Höhe]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\rho_{u} = \frac{A_{s,2,x}}{b \cdot d_{2,x}} = \frac{2450\,\mathrm{mm}^{2}}{1000\,\mathrm{mm} \cdot 248.1\,\mathrm{mm}} = 0.00988
$$

## Gebraucht von

- [[Vergrösserungsfaktor der Durchbiegung]]

## Im Code

- [[opencivil.nachweis.verformung#Vergroesserungsfaktor._bewehrungsgehalte|Vergroesserungsfaktor._bewehrungsgehalte]]

## Themen

- [[Verformung]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Bewehrung im Verhältnis zur Betonfläche bis zur statischen Höhe,
$\rho = A_s / (b \cdot d)$ -- eine dimensionslose Zahl, gewöhnlich zwischen
0.2 % und 1.5 %. Sie sagt, wie stark der gerissene Querschnitt ist, und geht
so in den [[Vergrösserungsfaktor der Durchbiegung]] ein: als $\rho$ der
gezogenen Seite und als $\rho'$ der Gegenseite.
