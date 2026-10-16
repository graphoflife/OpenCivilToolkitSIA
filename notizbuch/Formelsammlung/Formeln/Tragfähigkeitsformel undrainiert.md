---
erzeugt: ed6adb7b3c4b
art: formel
tags: [formel]
normstelle: "Kap. 9.2.17"
---
> [!info] Normstelle
> Kap. 9.2.17

$$
\sigma_f = 5.1 \, s_u \left(1 + s_c + d_c - i_c - b_c - g_c\right) + \left(\gamma t + q\right) \qquad N_{Rd} = \sigma_f \cdot b \cdot L
$$

## Im Code

- [[opencivil.geotechnik.grundbruch#Grundbruch|Grundbruch._undrainiert]]

## Themen

- [[Grundbruch]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wird ein wassergesättigter Ton schnell belastet, kann das Porenwasser nicht
abfliessen. Die Scherfestigkeit ist dann die undrainierte $s_u$, unabhängig
von der Normalspannung, und es gilt $\varphi = 0$.

Die Tragfähigkeitsfaktoren gehen dabei über in $N_c = \pi + 2 \approx 5.1$,
$N_q = 1$ und $N_{\gamma} = 0$: die Überlagerung zählt voll, das Gewicht des
Gleitkörpers gar nicht. Die Korrekturen stehen als Summanden in der Klammer,
nicht als Faktoren. Gerechnet wird mit totalen Spannungen.
