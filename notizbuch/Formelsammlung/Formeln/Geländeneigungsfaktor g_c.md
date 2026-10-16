---
erzeugt: 626e102fccf9
art: formel
tags: [formel]
normstelle: ["Kap. 9.2.15", "Kap. 9.2.17"]
---
> [!info] Normstellen
> Kap. 9.2.15 · Kap. 9.2.17

*In der Herleitung: «Geländeneigungsfaktor der Kohäsion»*

$$
g_c = 1 - \frac{\beta}{147^\circ}
$$

*In der Herleitung: «Geländeneigungsfaktor, undrainiert»*

$$
g_c = \frac{\beta}{147^\circ}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\beta$ | Neigung des Geländes | ° | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
g_c = 1 - \frac{\beta}{147^\circ} = 1 - \frac{0{}^{\circ}}{147^\circ} = 1
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
g_c = \frac{\beta}{147^\circ} = \frac{10{}^{\circ}}{147^\circ} = 0.07
$$

## Gebraucht von

- [[Bruchspannung in der Sohle]]

## Im Code

- [[opencivil.geotechnik.grundbruch#Grundbruch|Grundbruch._drainiert]]
- [[opencivil.geotechnik.grundbruch#Grundbruch|Grundbruch._undrainiert]]

## Themen

- [[Grundbruch]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Fällt das Gelände neben dem Fundament ab, ist der Weg des Gleitkörpers an
die Oberfläche kürzer, und über ihm liegt weniger Boden -- die Tragfähigkeit
sinkt. $\beta$ ist positiv, wenn das Gelände auf der Seite abfällt, zu der
$T$ zeigt (Bild 9.2.15).

Der Faktor der Kohäsion sinkt linear mit $\beta/147°$. Undrainiert steht
$\beta/147°$ als Abzug in der Klammer.
