---
erzeugt: b5551b6f963d
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
z = d_{2,x} - \frac{x}{3}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $d_{2,x}$ | – | mm | [[Statische Höhe]] |
| $x$ | – | mm | [[Nulllinie des gerissenen Querschnitts]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
z = d_{2,x} - \frac{x}{3} = 243.1\,\mathrm{mm} - \frac{108.5\,\mathrm{mm}}{3} = 206.9\,\mathrm{mm}
$$

## Gebraucht von

- [[Aufnehmbares Moment der Bewehrung]]

## Im Code

- [[opencivil.nachweis.mindestbewehrung#ZwaengungBiegung.protokoll_lage|ZwaengungBiegung.protokoll_lage]]

## Themen

- [[Zwängung auf Biegung]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Betondruckspannung verläuft im gerissenen, elastischen Querschnitt
dreieckig – null in der Nulllinie, am grössten an der gedrückten Kante. Ihre
Resultierende liegt im Schwerpunkt des Dreiecks, bei $x/3$ vom Rand. Der
Hebelarm zur Bewehrung ist darum $d - x/3$.
