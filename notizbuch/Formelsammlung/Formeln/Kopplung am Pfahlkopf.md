---
erzeugt: c095dd0394ff
art: formel
tags: [formel]
normstelle: "Kap. 12.10, Bild 12.14"
---
> [!info] Normstelle
> Kap. 12.10, Bild 12.14

*In der Herleitung: «Kopplung: das Moment am eingespannten Kopf je Verschiebung»*

$$
K_{HM} = \frac{M_{0,E}}{y_{0,E}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $M_{0,E}$ | Moment am eingespannten Kopf unter H = 1 MN | MNm | Zwischenwert |
| $y_{0,E}$ | Verschiebung des eingespannten Kopfs unter H = 1 MN | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
K_{HM} = \frac{M_{0,E}}{y_{0,E}} = \frac{-1.663\,\mathrm{MNm}}{6.67\,\mathrm{mm}} = -249.35\,\mathrm{MN}
$$

## Gebraucht von

- [[Drehfeder des Pfahlkopfs]]

## Im Code

- [[opencivil.pfahl.steifigkeit#Pfahlsteifigkeit|Pfahlsteifigkeit._federn]]

## Themen

- [[Pfahlsteifigkeit]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das Moment, mit dem der eingespannte Kopf sich gegen das Drehen wehrt, je
Verschiebung. Eine Querkraft allein würde den Kopf drehen; die Einspannung
hält mit einem Moment dagegen, darum ist K_HM negativ. Das Vorzeichen folgt
der Abmachung der Rechnung: ein Moment am Kopf ist positiv, wenn es dreht
wie eine Querkraft H, die über dem Kopf angreift.

Für einen langen Pfahl in gleichmässigem Boden −k_s · D / (2λ²)
(Kap. 12.10). ⌀ 900 mm aus C30/37 in E_s,k = 30 MN/m²: K_HM ≈ −180 MN.
