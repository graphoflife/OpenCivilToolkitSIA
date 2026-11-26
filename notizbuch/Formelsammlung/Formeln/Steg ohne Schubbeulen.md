---
erzeugt: 1fa45616fbe4
art: formel
tags: [formel]
normstelle: "SIA 263:2013, 5.1.4.2, (42)"
---
> [!info] Normstelle
> SIA 263:2013, 5.1.4.2, (42)

*In der Herleitung: «Beim I und beim U beult der Steg nicht, solange»*

$$
\frac{h - t_f}{t_w} \le \sqrt{\frac{4 E}{f_y}}
$$

## Im Code

- [[opencivil.nachweis.qa_stahl_kennzahlen#KennzahlenStahlQA|KennzahlenStahlQA._schub]]

## Themen

- [[Kennzahlen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ein gedrungener Steg fliesst unter Schub, bevor er beult. Die Grenze
vergleicht seine Schlankheit $(h - t_f)/t_w$ mit $\sqrt{4E/f_y}$: bei S235
sind das 59.8, bei S355 48.6. Ein IPE 600 aus S355 liegt mit
$(600 - 19)/12 = 48.4$ knapp darunter.

Hält der Steg die Grenze ein, gilt der volle
[[Querkraftwiderstand eines Stahlprofils]]; sonst trägt er nach
[[Schubbeulen des Blechs, ohne Quersteifen]].
