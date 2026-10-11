---
erzeugt: 4b4b158a2132
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
\bar{R}_{d,x} = \bar{E}_{d,x} + a
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\bar{E}_{d,x}$ | Einwirkung | – | [[Einwirkung im normierten Diagramm]] |
| $a$ | – | – | [[Kürzester Abstand zur Resistenzlinie]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\bar{R}_{d,x} = \bar{E}_{d,x} + a = 0.195 + 0.141 = 0.336
$$

## Im Code

- [[opencivil.nachweis.biegung_normalkraft#BiegungNormalkraft._protokoll_naechster|BiegungNormalkraft._protokoll_naechster]]

## Themen

- [[Biegung und Normalkraft]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Liegt die Einwirkung innerhalb der Linie, ist der Rand um den
[[Kürzester Abstand zur Resistenzlinie|kürzesten Abstand]] $a$ weiter aussen:
$\bar R = \bar E + a$. Liegt sie ausserhalb, ist er um $a$ weiter innen,
höchstens bis null. Der Erfüllungsgrad ist $\bar R / \bar E$ -- grösser als 1
mit Reserve, kleiner als 1 ohne.

Anders als die beiden anderen Massstäbe misst dieser in keine feste
Richtung: er sagt, wie nahe die Einwirkung dem Rand überhaupt kommt.
