---
erzeugt: 5b846621732c
art: formel
tags: [formel]
normstelle: "Kap. 9.2.12"
---
> [!info] Normstelle
> Kap. 9.2.12

*In der Herleitung: «Formfaktor der seitlichen Auflast»*

$$
s_q = 1 + \frac{b}{L} \cdot \tan \varphi_{eff}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $b$ | Breite des Fundaments | m | Vorgabe |
| $L$ | Länge des Fundaments | m | Vorgabe |
| $\varphi_{eff}$ | Reibungswinkel, Bemessungswert | ° | [[Bemessungswert des Reibungswinkels]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
s_q = 1 + \frac{b}{L} \cdot \tan \varphi_{eff} = 1 + \frac{2\,\mathrm{m}}{2.5\,\mathrm{m}} \cdot \tan 27.51{}^{\circ} = 1.42
$$

## Gebraucht von

- [[Bruchspannung in der Sohle]]

## Im Code

- [[opencivil.geotechnik.grundbruch#Grundbruch|Grundbruch._drainiert]]

## Themen

- [[Grundbruch]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie beim [[Formfaktor s_c]]: beim räumlichen Bruch ist der Gleitkörper
grösser, und mehr Auflast liegt auf ihm. Der Zuwachs hängt an $\tan\varphi$
-- ohne Reibung trägt die Auflast nichts dazu bei.
