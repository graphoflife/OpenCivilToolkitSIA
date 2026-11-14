---
erzeugt: 439b55347bc3
art: formel
tags: [formel]
normstelle: "Kap. 9.3.6"
---
> [!info] Normstelle
> Kap. 9.3.6

*In der Herleitung: «Erddruck undrainiert, vorne passiv und hinten aktiv: totale Spannungen»*

$$
e_p = \sigma_v + 2 \cdot s_u \qquad e_a = \sigma_v - 2 \cdot s_u
$$

## Im Code

- [[opencivil.pfahl.quer#AeussererQuerwiderstand._erdwiderstand|AeussererQuerwiderstand._erdwiderstand]]

## Themen

- [[Äusserer Pfahlwiderstand quer]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Gesättigter Ton, rasch belastet, trägt mit der totalen Spannung und der
undrainierten Scherfestigkeit (Kap. 9.3.6): K = 1, vorne
e_p = σ_v + 2 · s_u, hinten e_a = σ_v − 2 · s_u. Wird e_a negativ, löst
sich der Boden hinten vom Pfahl -- ein Spalt, der nichts trägt.

Seeton mit s_u,k = 25 kPa und γ = 18 kN/m³: in 2 m ist σ_v = 36 kPa,
e_p = 86 kPa und e_a = −14 kPa, also null. Von 2.78 m an, wo σ_v = 2 · s_u
wird, drückt der Boden auch hinten, und die Differenz bleibt 4 · s_u =
100 kPa, wie tief es auch geht.
