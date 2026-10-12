---
erzeugt: 632e02846d22
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Schnittgrössen aus den Kräften an den Stabenden»*

$$
N(0) = -s_{u,a} \qquad V(0) = s_{v,a} \qquad M(0) = -s_{\theta,a} \qquad \frac{\mathrm{d}N}{\mathrm{d}x} = -p_x \qquad \frac{\mathrm{d}V}{\mathrm{d}x} = p_y \qquad \frac{\mathrm{d}M}{\mathrm{d}x} = V - m
$$

## Im Code

- [[opencivil.stabwerk.herleitung|_ansaetze]]

## Themen

- [[Steifigkeitsmethode]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Aus den Kräften $\mathbf{s}$ an den Enden -- in den Achsen des Stabs, mit dem
Vorzeichen der Matrix -- werden die Schnittgrössen der Baustatik: $N > 0$ ist
Zug, $M > 0$ zieht an der gestrichelten Faser, bei einem Stab von links nach
rechts unten. Dazwischen folgen sie aus dem Gleichgewicht am kurzen
Stabstück: die Querlast $p_y$ ändert die Querkraft, die Querkraft das Moment,
ein verteiltes Moment $m$ ebenso.

Zwischen zwei Laststellen sind die Lasten linear, also $V$ quadratisch und
$M$ kubisch. Gerechnet wird darum genau, mit Polynomen. Ein Extremwert liegt,
wo die Ableitung null wird, oder an einer Grenze -- einem Stabende, einer
Laststelle.
