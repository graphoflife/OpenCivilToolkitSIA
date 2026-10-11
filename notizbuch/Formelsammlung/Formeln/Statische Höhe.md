---
erzeugt: 9b9c3512d0eb
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Statische Höhe der x-Bewehrung unten»*

$$
d_{u} = z_{u}
$$

*In der Herleitung: «Statische Höhe der x-Bewehrung oben»*

$$
d_{o} = h - z_{3,x,g}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $z_{u}$ | – | mm | [[Schwerpunkt der zusammengefassten Lage]] |
| $h$ | Plattendicke | mm | Vorgabe, Zwischenwert |
| $z_{3,x,g}$ | Tiefe 3. Lage Grundbewehrung ab Oberkante | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
d_{u} = z_{u} = 248.1\,\mathrm{mm}
$$

Mit den Zahlen aus dem Beispielprojekt:

$$
d_{o} = h - z_{3,x,g} = 300\,\mathrm{mm} - 48\,\mathrm{mm} = 252\,\mathrm{mm}
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

- [[opencivil.querschnitt.platte#Lagenaufbau._vergroesserung|Lagenaufbau._vergroesserung]]
- [[opencivil.querschnitt.platte#protokoll_statische_hoehe|protokoll_statische_hoehe]]

## Themen

- [[Querschnitt]]
- [[Biegung und Normalkraft]]
- [[Querkraft]]
- [[Duktilität]]
- [[Zwängung auf Biegung]]
- [[Knicken]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Abstand vom gedrückten Rand bis zum Schwerpunkt der gezogenen
Bewehrung -- der Hebelarm, an dem die Stahlkraft gegen die Druckzone
arbeitet. Eine untere Lage misst ab der Oberkante, $d = z$; eine obere ab der
Unterkante, $d = h - z$, denn bei negativem Moment liegt die Druckzone unten.

$d$ steckt in fast jedem Widerstand: im Momentenwiderstand, im
Bewehrungsgehalt, in der Querkraft und in der Duktilität.
