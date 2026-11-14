---
erzeugt: 84134c1673fe
art: formel
tags: [formel]
normstelle: "Kap. 9.3.5"
---
> [!info] Normstelle
> Kap. 9.3.5

*In der Herleitung: «Erddruck drainiert, vorne passiv und hinten aktiv: wirksame Spannungen, ohne Reibung am Pfahl»*

$$
e_p = K_p \cdot \sigma'_v + 2 \cdot c' \cdot \sqrt{K_p} \qquad e_a = \frac{\sigma'_v}{K_p} - \frac{2 \cdot c'}{\sqrt{K_p}} \qquad K_p = \frac{1 + \sin\varphi'}{1 - \sin\varphi'}
$$

## Im Code

- [[opencivil.pfahl.quer#AeussererQuerwiderstand._erdwiderstand|AeussererQuerwiderstand._erdwiderstand]]

## Themen

- [[Äusserer Pfahlwiderstand quer]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Schiebt sich der Pfahl quer, drückt er vorne gegen den Boden, bis dieser
passiv bricht; hinten entlastet er ihn, bis nur noch der aktive Druck
nachschiebt. Beide Grenzen nach Rankine, ohne Reibung zwischen Pfahl und
Boden (Kap. 9.3.5): K_p = (1 + sin φ') / (1 − sin φ') und K_a = 1 / K_p,
die Kohäsion vorne mit + 2 · c' · √K_p, hinten mit − 2 · c' / √K_p.
Gerechnet mit der wirksamen Spannung, unter dem Grundwasser also mit
γ − γ_w.

Kies mit φ'_k = 35° in 5 m Tiefe, trocken, γ = 20 kN/m³: σ'_v = 100 kPa,
K_p = 3.69 und K_a = 0.27 -- vorne e_p = 369 kPa, hinten e_a = 27 kPa.

Ohne Wandreibung bleibt K_p auf der sicheren Seite: mit ihr wäre er
grösser. Wie die beiden Drücke zum Widerstand je Meter Pfahl werden, steht
unter [[Erdwiderstand je Meter Pfahl]].
