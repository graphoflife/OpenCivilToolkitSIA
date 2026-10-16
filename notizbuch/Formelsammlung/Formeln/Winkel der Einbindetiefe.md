---
erzeugt: f1620f0e7146
art: formel
tags: [formel]
normstelle: "Kap. 9.2.13"
---
> [!info] Normstelle
> Kap. 9.2.13

*In der Herleitung: «Winkel der Einbindetiefe, in Grad»*

$$
\vartheta_t = \arctan\frac{t}{b}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $t$ | Tiefe der Sohle unter Terrain | m | Vorgabe |
| $b$ | Breite des Fundaments | m | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\vartheta_t = \arctan\frac{t}{b} = \arctan\frac{1.2\,\mathrm{m}}{2\,\mathrm{m}} = 31{}^{\circ}
$$

## Gebraucht von

- [[Tiefenfaktor d_c]]
- [[Tiefenfaktor d_q]]

## Im Code

- [[opencivil.geotechnik.grundbruch#Grundbruch._einbindewinkel|Grundbruch._einbindewinkel]]

## Themen

- [[Grundbruch]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie tief das Fundament im Verhältnis zu seiner Breite eingebunden ist, als
Winkel: $\arctan(t/b)$. Er geht in die Tiefenfaktoren ein und begrenzt sie
zugleich -- auch ein sehr tief eingebundenes Fundament kommt nicht über
90°.

Die Tiefenfaktoren rechnen mit seinem Zahlenwert in Grad, wie das Kapitel
sie schreibt.
