---
erzeugt: 2eb6b3c7fea1
art: formel
tags: [formel]
normstelle: "Kap. 9.2.15"
---
> [!info] Normstelle
> Kap. 9.2.15

*In der Herleitung: «Geländeneigungsfaktor der Auflast und des Gleitkörpers»*

$$
g_q = \left(1 - 0.5 \cdot \tan \beta\right)^{5}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\beta$ | Neigung des Geländes | ° | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
g_q = \left(1 - 0.5 \cdot \tan \beta\right)^{5} = \left(1 - 0.5 \cdot \tan 0{}^{\circ}\right)^{5} = 1
$$

## Gebraucht von

- [[Bruchspannung in der Sohle]]

## Im Code

- [[opencivil.geotechnik.grundbruch#Grundbruch|Grundbruch._drainiert]]

## Themen

- [[Grundbruch]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Für die Auflast und das Gewicht des Gleitkörpers gilt derselbe Faktor,
$g_{\gamma} = g_q$. Die fünfte Potenz macht ihn empfindlich: bei
$\beta = 15°$ bleibt knapp die Hälfte (0.49), bei 30° knapp ein Fünftel
(0.18).

Wird die Klammer kleiner als null -- erst bei sehr steilem Gelände --, gilt
null.
