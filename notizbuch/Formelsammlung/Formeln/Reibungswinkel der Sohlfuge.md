---
erzeugt: dc3aab4d71a7
art: formel
tags: [formel]
normstelle: "SIA 267:2013, 8.4.1.1, (27), (28)"
---
> [!info] Normstelle
> SIA 267:2013, 8.4.1.1, (27), (28)

*In der Herleitung: «Sohlreibungswinkel, charakteristisch»*

$$
\delta_k = \min\left[k_{\delta} \cdot \varphi_k;\ 35^\circ\right]
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $k_{\delta}$ | Sohlreibungswinkel im Verhältnis zum Reibungswinkel, δ\_k/φ\_k | – | Vorgabe |
| $\varphi_k$ | Reibungswinkel, charakteristisch | ° | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\delta_k = \min\left[k_{\delta} \cdot \varphi_k;\ 35^\circ\right] = \min\left[1 \cdot 32{}^{\circ};\ 35^\circ\right] = 32{}^{\circ}
$$

## Gebraucht von

- [[Bemessungswert des Sohlreibungswinkels]]

## Im Code

- [[opencivil.geotechnik.grundbruch#Gleiten._sohlreibung|Gleiten._sohlreibung]]

## Themen

- [[Gleiten]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Sohlfuge reibt höchstens so gut wie der Boden selbst. SIA 267:2013
setzt den charakteristischen Sohlreibungswinkel $\delta_k$ darum als Teil
von $\varphi_k$ an (8.4.1.1): ganz bei einer rauen Sohle, unter der der
Bruch im Boden verläuft -- etwa bei einem auf den Boden betonierten
Fundament --, ½ bis ⅔ bei einer glatten, wo er in der Fuge selbst liegt. In
jedem Fall höchstens 35°. Das Buch nennt für $\delta^{*}$ etwa ⅔ bis
1 · φ, ohne Grenze (Kap. 9.2.18).

Das Werkzeug fragt nach dem Verhältnis $k_{\delta} = \delta_k/\varphi_k$,
Vorgabe 1, und begrenzt das Produkt auf 35°. Den Partialfaktor nimmt erst
der [[Bemessungswert des Sohlreibungswinkels]].
