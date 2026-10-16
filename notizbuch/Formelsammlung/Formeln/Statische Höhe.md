---
erzeugt: 548eb25c2f94
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Statische Höhe der Lage unten, ab dem gedrückten Rand oben»*

$$
d_{2,x} = z_{2,x}
$$

*In der Herleitung: «Statische Höhe der Lage oben, ab dem gedrückten Rand unten»*

$$
d_{3,x} = h - z_{3,x}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $z_{2,x}$ | – | mm | Zwischenwert, [[Schwerpunkt der zusammengefassten Lage]] |
| $h$ | Plattendicke | mm | Zwischenwert, Vorgabe |
| $z_{3,x}$ | – | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
d_{2,x} = z_{2,x} = 248.1\,\mathrm{mm}
$$

Mit den Zahlen aus dem Beispielprojekt:

$$
d_{3,x} = h - z_{3,x} = 300\,\mathrm{mm} - 48\,\mathrm{mm} = 252\,\mathrm{mm}
$$

## Gebraucht von

- [[Beiwert für die statische Höhe]]
- [[Bewehrungsgehalt]]
- [[Bezogene Druckzonenhöhe]]
- [[Dehnung der Zugbewehrung]]
- [[Innerer Hebelarm]]
- [[Momentengleichgewicht um die halbe Höhe]]
- [[Momentenwiderstand bei reiner Biegung]]
- [[Nulllinie des gerissenen Querschnitts]]
- [[Vergrösserungsfaktor der Durchbiegung]]
- [[Widerstand der Bügel]]
- [[Widerstand der Druckdiagonalen]]
- [[Wirksame Höhe (Einlage nicht massgebend)]]
- [[Wirksame Höhe, um die Einlage vermindert]]

## Im Code

- [[opencivil.nachweis.verformung#Vergroesserungsfaktor._bewehrungsgehalte|Vergroesserungsfaktor._bewehrungsgehalte]]
- [[opencivil.querschnitt.platte#protokoll_statische_hoehe|protokoll_statische_hoehe]]

## Themen

- [[Biegung und Normalkraft]]
- [[Verformung]]
- [[Kennzahlen]]
- [[Querkraft]]
- [[Duktilität]]
- [[Zwängung auf Biegung]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Abstand vom gedrückten Rand bis zum Schwerpunkt der gezogenen
Bewehrung -- der Hebelarm, an dem die Stahlkraft gegen die Druckzone
arbeitet. Eine untere Lage misst ab der Oberkante, $d = z$; eine obere ab der
Unterkante, $d = h - z$, denn bei negativem Moment liegt die Druckzone unten.

$d$ steckt in fast jedem Widerstand: im Momentenwiderstand, im
Bewehrungsgehalt, in der Querkraft und in der Duktilität.
