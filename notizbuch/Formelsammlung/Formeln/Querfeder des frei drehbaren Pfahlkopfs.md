---
erzeugt: a6c28c20ae9b
art: formel
tags: [formel]
normstelle: "Kap. 12.10, Bild 12.14"
---
> [!info] Normstelle
> Kap. 12.10, Bild 12.14

*In der Herleitung: «Querfeder, Kopf frei drehbar»*

$$
k_h = \frac{1\,\mathrm{MN}}{y_0}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $y_0$ | Verschiebung des frei drehbaren Kopfs unter H = 1 MN | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
k_h = \frac{1\,\mathrm{MN}}{y_0} = \frac{1\,\mathrm{MN}}{15.092\,\mathrm{mm}} = 66.26\,\mathrm{MN}/\mathrm{m}
$$

## Gebraucht von

- [[Drehfeder des Pfahlkopfs]]

## Im Code

- [[opencivil.pfahl.steifigkeit#Pfahlsteifigkeit|Pfahlsteifigkeit._federn]]

## Themen

- [[Pfahlsteifigkeit]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie weit sich der Kopf unter einer Querkraft verschiebt, wenn er sich frei
drehen kann, etwa unter einem Gelenk: H durch y. Für einen langen Pfahl in
gleichmässigem Boden ist sie k_s · D / (2λ) mit λ = (k_s · D / (4 EI))^¼
(Kap. 12.10). ⌀ 900 mm aus C30/37 in E_s,k = 30 MN/m²: λ = 0.29 1/m,
k_h ≈ 52 MN/m.

Weil sich der Kopf dabei auch dreht, ist k_h kleiner als die Querfeder des
eingespannten Kopfs: beim langen Pfahl genau die Hälfte.
