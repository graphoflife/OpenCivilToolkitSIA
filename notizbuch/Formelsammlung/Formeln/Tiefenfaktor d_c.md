---
erzeugt: 93fe7978c688
art: formel
tags: [formel]
normstelle: ["Kap. 9.2.13", "Kap. 9.2.17"]
---
> [!info] Normstellen
> Kap. 9.2.13 · Kap. 9.2.17

*In der Herleitung: «Tiefenfaktor der Kohäsion»*

$$
d_c = 1 + 0.007 \cdot \vartheta_t
$$

*In der Herleitung: «Tiefenfaktor, undrainiert, t \< b»*

$$
d_c = 0.4 \cdot \frac{t}{b}
$$

*In der Herleitung: «Tiefenfaktor, undrainiert, t ≥ b»*

$$
d_c = 0.007 \cdot \vartheta_t
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\vartheta_t$ | Winkel der Einbindetiefe | ° | [[Winkel der Einbindetiefe]] |
| $t$ | Tiefe der Sohle unter Terrain | m | Vorgabe |
| $b$ | Breite des Fundaments | m | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
d_c = 1 + 0.007 \cdot \vartheta_t = 1 + 0.007 \cdot 31{}^{\circ} = 1.22
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
d_c = 0.4 \cdot \frac{t}{b} = 0.4 \cdot \frac{0.8\,\mathrm{m}}{1.5\,\mathrm{m}} = 0.21
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
d_c = 0.007 \cdot \vartheta_t = 0.007 \cdot 59{}^{\circ} = 0.41
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

Die Formel rechnet den Boden über der Sohle nur als Auflast. Dass er auch
Scherfestigkeit hat und der Gleitkörper durch ihn hindurch muss, erfasst der
Tiefenfaktor. Für die Kohäsion wächst er um 0.007 je Grad des
[[Winkel der Einbindetiefe|Winkels der Einbindetiefe]].

Undrainiert steht er als Summand in der Klammer: $0.4\,t/b$, solange
$t < b$; darüber $0.007 \arctan(t/b)$.
