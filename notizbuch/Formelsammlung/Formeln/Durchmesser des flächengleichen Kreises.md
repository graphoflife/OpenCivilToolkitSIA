---
erzeugt: 5252c12d9eb0
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.6.2.4"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.6.2.4

$$
b = \sqrt{\frac{4 \cdot A_u}{\pi}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $A_u$ | Fläche innerhalb des Nachweisschnitts | m² | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
b = \sqrt{\frac{4 \cdot A_u}{\pi}} = \sqrt{\frac{4 \cdot 0.423\,\mathrm{m}^{2}}{\pi}} = 734\,\mathrm{mm}
$$

## Gebraucht von

- [[Beiwert der Momentenübertragung]]

## Im Code

- [[opencivil.durchstanzen.nachweis#Durchstanzen._k_e|Durchstanzen._k_e]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Für $k_e$ aus der Exzentrizität ([[Beiwert der Momentenübertragung]]) wird
die Fläche innerhalb des Nachweisschnitts durch einen Kreis derselben Fläche
ersetzt; $b$ ist sein Durchmesser (4.3.6.2.4). Am Plattenrand zählt nur die
Fläche in der Platte.
