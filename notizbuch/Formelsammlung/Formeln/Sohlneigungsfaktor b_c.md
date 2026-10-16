---
erzeugt: 03e0c6458789
art: formel
tags: [formel]
normstelle: ["Kap. 9.2.16", "Kap. 9.2.17"]
---
> [!info] Normstellen
> Kap. 9.2.16 · Kap. 9.2.17

*In der Herleitung: «Sohlneigungsfaktor der Kohäsion»*

$$
b_c = 1 - \frac{\alpha}{147^\circ}
$$

*In der Herleitung: «Sohlneigungsfaktor, undrainiert»*

$$
b_c = \frac{\alpha}{147^\circ}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\alpha$ | Neigung der Sohle | ° | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
b_c = 1 - \frac{\alpha}{147^\circ} = 1 - \frac{0{}^{\circ}}{147^\circ} = 1
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
b_c = \frac{\alpha}{147^\circ} = \frac{4{}^{\circ}}{147^\circ} = 0.03
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

Eine geneigte Sohle dreht den Gleitkörper: gemessen an der Sohle liegt das
Gelände auf der Bruchseite tiefer. Das wirkt wie eine Geländeneigung und
mindert die Tragfähigkeit. $\alpha$ ist positiv, wenn die Sohle in Richtung
von $T$ ansteigt (Bild 9.2.15).

Für die Kohäsion sinkt der Faktor linear mit $\alpha/147°$; undrainiert
steht $\alpha/147°$ als Abzug in der Klammer.
