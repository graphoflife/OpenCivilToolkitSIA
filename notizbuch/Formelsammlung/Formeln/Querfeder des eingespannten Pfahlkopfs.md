---
erzeugt: de18a871c7a2
art: formel
tags: [formel]
normstelle: "Kap. 12.10, Bild 12.14"
---
> [!info] Normstelle
> Kap. 12.10, Bild 12.14

*In der Herleitung: «Querfeder, Kopf eingespannt»*

$$
K_{HH} = \frac{1\,\mathrm{MN}}{y_{0,E}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $y_{0,E}$ | Verschiebung des eingespannten Kopfs unter H = 1 MN | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
K_{HH} = \frac{1\,\mathrm{MN}}{y_{0,E}} = \frac{1\,\mathrm{MN}}{6.67\,\mathrm{mm}} = 149.93\,\mathrm{MN}/\mathrm{m}
$$

## Gebraucht von

- [[Drehfeder des Pfahlkopfs]]

## Im Code

- [[opencivil.pfahl.steifigkeit#Pfahlsteifigkeit|Pfahlsteifigkeit._federn]]

## Themen

- [[Pfahlsteifigkeit]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Querfeder, wenn sich der Kopf nicht drehen kann, etwa in einer steifen
Pfahlkopfplatte: H durch y bei θ = 0. Für einen langen Pfahl in
gleichmässigem Boden k_s · D / λ, doppelt so viel wie frei drehbar
(Kap. 12.10). ⌀ 900 mm aus C30/37 in E_s,k = 30 MN/m²: K_HH ≈ 104 MN/m.

Mit der Kopplung K_HM und der Drehfeder K_MM bildet sie die
Steifigkeitsmatrix des Kopfs: mit ihr setzt ein Modell des Tragwerks den
Pfahl als Feder ein, ohne ihn selbst abzubilden.
