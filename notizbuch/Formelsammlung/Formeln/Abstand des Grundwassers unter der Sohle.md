---
erzeugt: 05f6aacae5dd
art: formel
tags: [formel]
normstelle: "Kap. 9.2.8"
---
> [!info] Normstelle
> Kap. 9.2.8

$$
T = t_1 - t
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $t_1$ | Tiefe des höchsten Grundwasserspiegels unter Terrain | m | Vorgabe |
| $t$ | Tiefe der Sohle unter Terrain | m | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
T = t_1 - t = 5\,\mathrm{m} - 1.2\,\mathrm{m} = 3.8\,\mathrm{m}
$$

## Im Code

- [[opencivil.geotechnik.grundbruch#Grundbruch._grundwasser|Grundbruch._grundwasser]]

## Themen

- [[Grundbruch]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Liegt der Grundwasserspiegel unter der Sohle, entscheidet sein Abstand $T$,
ob er den Gleitkörper erreicht. Ist $T$ mindestens so gross wie die
[[Tiefe des Gleitkörpers]] $H$ (Bild 9.2.10, Lage 3), bleibt dieser trocken.

Dazwischen verlangt das Kapitel eine Stabilitätsberechnung. Das Werkzeug
rechnet dann so, als stünde das Wasser auf der Sohle -- auf der sicheren
Seite, aber eine eigene Annahme, im TODO vermerkt.
