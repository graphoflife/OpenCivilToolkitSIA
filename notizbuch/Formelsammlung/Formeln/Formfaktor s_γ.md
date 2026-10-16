---
erzeugt: afb1a06e6a94
art: formel
tags: [formel]
normstelle: "Kap. 9.2.12"
---
> [!info] Normstelle
> Kap. 9.2.12

*In der Herleitung: «Formfaktor des Gleitkörpergewichts»*

$$
s_{\gamma} = 1 - 0.4 \cdot \frac{b}{L}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $b$ | Breite des Fundaments | m | Vorgabe |
| $L$ | Länge des Fundaments | m | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
s_{\gamma} = 1 - 0.4 \cdot \frac{b}{L} = 1 - 0.4 \cdot \frac{2\,\mathrm{m}}{2.5\,\mathrm{m}} = 0.68
$$

## Gebraucht von

- [[Bruchspannung in der Sohle]]

## Im Code

- [[opencivil.geotechnik.grundbruch#Grundbruch|Grundbruch._drainiert]]

## Themen

- [[Grundbruch]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der einzige Formfaktor unter eins: beim Quadrat nur 0.6. Das Eigengewicht
des Gleitkörpers trägt beim räumlichen Bruch anteilig weniger als beim
Streifen. Für den Streifen ist er 1.
