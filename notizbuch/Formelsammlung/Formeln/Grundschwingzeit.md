---
erzeugt: 0c6d752c1c17
art: formel
tags: [formel]
normstelle: "SIA 261:2020, 16.5.2.3, (40)"
---
> [!info] Normstelle
> SIA 261:2020, 16.5.2.3, (40)

*In der Herleitung: «Grundschwingzeit in x»*

$$
T_{1,x} = 2 \cdot \sqrt{u_x} \quad \left(u_x\ \text{in}\ \mathrm{m}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $u_x$ | Auslenkung des Dachs in x | mm | [[Auslenkung des Dachs]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
T_{1,x} = 2 \cdot \sqrt{u_x} = 2 \cdot \sqrt{0.0317} = 0.356\,\mathrm{s} \quad \left(u_x\ \text{in}\ \mathrm{m}\right)
$$

## Gebraucht von

- [[Bemessungsspektrum (34)]]

## Im Code

- [[opencivil.erdbeben.ersatzkraft#Lauf._schwingzeit|Lauf._schwingzeit]]

## Themen

- [[Erdbeben]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Eine Abschätzung der Norm für Gebäude (16.5.2.3): die fiktive
[[Auslenkung des Dachs]] in Metern eingesetzt, gibt $T_1$ in Sekunden. Die
Formel ist nicht dimensionsrein, darum die Einheit dabei. Statt ihrer
erlaubt die Norm den Rayleigh-Quotienten; wer $T_1$ so oder mit einem
eigenen Modell bestimmt hat, gibt ihn von Hand ein, und er gilt, wie er
steht.

Je weicher das Gebäude, desto länger $T_1$. Hinter $T_C$ fällt das
Spektrum ([[Bemessungsspektrum (33)|(33)]]), und über $4 \cdot T_C$ gilt das
Verfahren nicht mehr ([[Grenze der Grundschwingzeit]]).
