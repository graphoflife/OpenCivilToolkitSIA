---
erzeugt: 9bdc1cd26b46
art: formel
tags: [formel]
normstelle: ["Kap. 9.2.12", "Kap. 9.2.17"]
---
> [!info] Normstellen
> Kap. 9.2.12 · Kap. 9.2.17

*In der Herleitung: «Formfaktor der Kohäsion»*

$$
s_c = 1 + \frac{b}{L} \cdot \frac{N_q}{N_c}
$$

*In der Herleitung: «Formfaktor, undrainiert»*

$$
s_c = 0.2 \cdot \frac{b}{L}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $b$ | Breite des Fundaments | m | Vorgabe |
| $L$ | Länge des Fundaments | m | Vorgabe |
| $N_q$ | Tragfähigkeitsfaktor der seitlichen Auflast | – | [[Tragfähigkeitsfaktor N_q]] |
| $N_c$ | Tragfähigkeitsfaktor der Kohäsion | – | [[Tragfähigkeitsfaktor N_c]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
s_c = 1 + \frac{b}{L} \cdot \frac{N_q}{N_c} = 1 + \frac{2\,\mathrm{m}}{2.5\,\mathrm{m}} \cdot \frac{13.95}{24.86} = 1.45
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
s_c = 0.2 \cdot \frac{b}{L} = 0.2 \cdot \frac{1.5\,\mathrm{m}}{2\,\mathrm{m}} = 0.15
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

Die Faktoren $N$ gelten für einen unendlich langen Streifen. Ein Rechteck-
oder Quadratfundament bricht räumlich, und der Gleitkörper wird an den Enden
grösser -- das trägt mehr. Der Formfaktor der Kohäsion wächst darum mit
$b/L$; für den Streifen ($b/L \to 0$) ist er 1.

In der [[Tragfähigkeitsformel undrainiert|undrainierten Formel]] steht er als
Summand in der Klammer: $0.2\,b/L$, also 0.2 beim Quadrat.
