---
erzeugt: 269107909c3f
art: formel
tags: [formel]
normstelle: "Kap. 9.2.16"
---
> [!info] Normstelle
> Kap. 9.2.16

*In der Herleitung: «Sohlneigungsfaktor der seitlichen Auflast»*

$$
b_q = e^{-0.035 \cdot \alpha \cdot \tan \varphi_{eff}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\alpha$ | Neigung der Sohle | ° | Vorgabe |
| $\varphi_{eff}$ | Reibungswinkel, Bemessungswert | ° | [[Bemessungswert des Reibungswinkels]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
b_q = e^{-0.035 \cdot \alpha \cdot \tan \varphi_{eff}} = e^{-0.035 \cdot 0{}^{\circ} \cdot \tan 27.51{}^{\circ}} = 1
$$

## Gebraucht von

- [[Bruchspannung in der Sohle]]

## Im Code

- [[opencivil.geotechnik.grundbruch#Grundbruch|Grundbruch._drainiert]]

## Themen

- [[Grundbruch]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Für die Auflast mindert die Sohlneigung exponentiell mit
$\alpha\,\tan\varphi$, $\alpha$ in Grad. Ohne Reibung hat sie auf diesen
Anteil keinen Einfluss.
