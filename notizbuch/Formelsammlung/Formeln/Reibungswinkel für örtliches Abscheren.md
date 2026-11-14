---
erzeugt: 7051f663ff6b
art: formel
tags: [formel]
normstelle: "Kap. 9.2.7, 12.5"
---
> [!info] Normstelle
> Kap. 9.2.7, 12.5

$$
\varphi^{*} = \tfrac{2}{3} \cdot \varphi'_{k,3}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\varphi'_{k,3}$ | Reibungswinkel der Schicht 3, charakteristisch | ° | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\varphi^{*} = \tfrac{2}{3} \cdot \varphi'_{k,3} = \tfrac{2}{3} \cdot 36{}^{\circ} = 24{}^{\circ}
$$

## Im Code

- [[opencivil.pfahl.aussen#AeussererWiderstand|AeussererWiderstand._fuss_drainiert]]

## Themen

- [[Äusserer Pfahlwiderstand]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Bis der Boden unter dem Fuss ganz bricht, müsste sich der Pfahl stark setzen;
vorher schert der Boden nur rings um den Fuss ab. Das Buch rechnet dafür mit
zwei Dritteln von Reibungswinkel und Kohäsion und empfiehlt diese Werte für
den Spitzendruck von Pfählen (Kap. 9.2.7, 12.5). Aus 36° werden 24°, und N_q
sinkt von 37.8 auf 9.6 -- auf ein Viertel.

Das Buch sieht dann keine weitere Sicherheit am Spitzendruck vor. Hier gelten
η_a und γ_M,a der Norm trotzdem -- nach Vorgabe, nicht nachgeschlagen.
