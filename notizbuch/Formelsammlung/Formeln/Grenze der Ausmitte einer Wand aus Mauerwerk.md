---
erzeugt: f41d757cadc9
art: formel
tags: [formel]
normstelle: "SIA 266:2015, 4.3.1.1, Gl. (6), Figur 4"
---
> [!info] Normstelle
> SIA 266:2015, 4.3.1.1, Gl. (6), Figur 4

*In der Herleitung: «Die Ausmitte der verformten Wand, nirgends grösser»*

$$
\left|e_z\right| \le \min\left[0.375 \cdot t_w;\ \frac{t_w}{2} \cdot \left(1 - \frac{N_{xd}}{l_w \cdot t_w \cdot f_{xd}}\right)\right]
$$

## Im Code

- [[opencivil.mauerwerk.nachweise#Normalkraft.ansatz|Normalkraft.ansatz]]

## Themen

- [[Mauerwerk]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie weit die Normalkraft aus der Mitte rücken darf, begrenzt zweierlei.
Bei kleiner Normalkraft die Verformbarkeit: höchstens $0.375 \cdot t_w$.
Bei grosser Normalkraft die Festigkeit: die Kraft muss auf dem überdrückten
Rest des Querschnitts Platz finden, der vom gedrückten Rand aus
$t_w - 2 e_z$ breit ist. Mit $f_{xd}$ darauf folgt Gl. (6).

Es gilt die kleinere der beiden Grenzen. Figur 4 zeichnet sie über
$n = N_{xd}/(l_w t_w f_{xd})$: bis $n = 0.25$ waagrecht bei 0.375, danach
die Gerade, die bei $n = 1$ null wird. Bis $n = 0.25$ darf sich das
Mauerwerk beliebig verformen, darüber versagt es spröde.

Im Nachweis gilt die Grenze an jeder Stelle der verformten Wand, nicht nur
an den Rändern. Erreicht die Ausmitte sie irgendwo, ist die Normalkraft
die grösste, die der Pfeiler trägt.
