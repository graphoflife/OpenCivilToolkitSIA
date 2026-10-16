---
erzeugt: 055afa371f1c
art: formel
tags: [formel]
normstelle: "Kap. 9.2.16"
---
> [!info] Normstelle
> Kap. 9.2.16

*In der Herleitung: «Sohlneigungsfaktor des Gleitkörpergewichts»*

$$
b_{\gamma} = e^{-0.047 \cdot \alpha \cdot \tan \varphi_{eff}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\alpha$ | Neigung der Sohle | ° | Vorgabe |
| $\varphi_{eff}$ | Reibungswinkel, Bemessungswert | ° | [[Bemessungswert des Reibungswinkels]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
b_{\gamma} = e^{-0.047 \cdot \alpha \cdot \tan \varphi_{eff}} = e^{-0.047 \cdot 0{}^{\circ} \cdot \tan 27.51{}^{\circ}} = 1
$$

## Gebraucht von

- [[Bruchspannung in der Sohle]]

## Im Code

- [[opencivil.geotechnik.grundbruch#Grundbruch|Grundbruch._drainiert]]

## Themen

- [[Grundbruch]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Für das Gewicht des Gleitkörpers mindert die Sohlneigung etwas stärker als
für die Auflast.

Im Text des Kapitels steht hier $\tan\alpha$; seine Tabelle 9.2.18 und die
Formel für [[Sohlneigungsfaktor b_q|b_q]] rechnen mit $\tan\varphi$. Das
Werkzeug folgt der Tabelle -- eine Annahme, im TODO vermerkt.
