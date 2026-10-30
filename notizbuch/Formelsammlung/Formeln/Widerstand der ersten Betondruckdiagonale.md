---
erzeugt: 7c62b8c2a0f8
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.6.5.8, (70)"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.6.5.8, (70)

*In der Herleitung: «Widerstand der ersten Betondruckdiagonale an der gestützten Fläche»*

$$
V_{Rd,max} = \min\left[k_{sys} \cdot k_r;\ 3.5\right] \cdot \tau_{cd} \cdot d_v \cdot u
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $k_{sys}$ | – | – | Zwischenwert |
| $k_r$ | – | – | [[Beiwert k_r]] |
| $\tau_{cd}$ | – | N/mm² | Zwischenwert |
| $d_v$ | – | mm | [[Wirksame Höhe ohne Abzug]] |
| $u$ | – | mm | [[Wirksamer Umfang des Nachweisschnitts]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  V_{Rd,max} &= \min\left[k_{sys} \cdot k_r;\ 3.5\right] \cdot \tau_{cd} \cdot d_v \cdot u \\
  &= \min\left[2.58 \cdot 0.721;\ 3.5\right] \cdot 1.0954\,\mathrm{N}/\mathrm{mm}^{2} \cdot 234\,\mathrm{mm} \cdot 2102\,\mathrm{mm} \\
  &= 1000.4\,\mathrm{kN}
\end{aligned}
$$

## Im Code

- [[opencivil.durchstanzen.mit_bewehrung#nachweisen|nachweisen]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Auch mit beliebig viel Durchstanzbewehrung bricht die Platte irgendwann an
der ersten Druckdiagonale, die an die gestützte Fläche grenzt. Die Norm
begrenzt den Widerstand darum auf $2 \cdot k_r$, höchstens 3.5, mal
$\tau_{cd} \cdot d_v \cdot u$ (4.3.6.5.8). Beide Faktoren dürfen höher sein,
wenn Versuche es belegen (4.3.6.5.9): für ancoPLUS lässt das Gutachten des
Herstellers bis $3 \cdot k_r$ zu, je nachdem, wie tief die Köpfe auf der
Druckseite liegen. Geht dieser Nachweis nicht auf, hilft nur eine grössere
Stütze, eine dickere Platte, ein besserer Beton oder ein Stahlpilz.
