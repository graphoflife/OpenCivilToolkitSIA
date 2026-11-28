---
erzeugt: d93e0dbe4f73
art: formel
tags: [formel]
normstelle: "SIA 261:2020, 16.7.2, Gl. (49)"
---
> [!info] Normstelle
> SIA 261:2020, 16.7.2, Gl. (49)

*In der Herleitung: «Ersatzkraft des Erdbebens je m² Wand, mit T\_a = T\_1»*

$$
p_E = \frac{\gamma_f \cdot a_{gd} \cdot S \cdot g_k}{g \cdot q_a} \cdot \left[3 \cdot \left(1 + \frac{z_a}{h}\right) - 0.5\right]
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\gamma_f$ | Bedeutungsbeiwert der Bauwerksklasse | – | Zwischenwert |
| $a_{gd}$ | Bemessungswert der Bodenbeschleunigung | m/s² | Zwischenwert |
| $S$ | Bodenparameter | – | Zwischenwert |
| $g_k$ | Eigengewicht der Wand je m² Ansicht | kN/m² | [[Eigengewicht der Wand je m² Ansicht, aus der Dichte ihres Mauerwerks]] |
| $g$ | Erdbeschleunigung | m/s² | Vorgabe |
| $q_a$ | Verhaltensbeiwert der Wand | – | Zwischenwert |
| $z_a$ | Höhe der Wand über dem Fundament | m | Zwischenwert |
| $h$ | Höhe des Gebäudes | m | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  p_E &= \frac{\gamma_f \cdot a_{gd} \cdot S \cdot g_k}{g \cdot q_a} \cdot \left[3 \cdot \left(1 + \frac{z_a}{h}\right) - 0.5\right] \\
  &= \frac{1 \cdot 1\,\mathrm{m}/\mathrm{s}^{2} \cdot 1.45 \cdot 3.15\,\mathrm{kN}/\mathrm{m}^{2}}{10\,\mathrm{m}/\mathrm{s}^{2} \cdot 1.5} \cdot \left[3 \cdot \left(1 + \frac{1.35\,\mathrm{m}}{6\,\mathrm{m}}\right) - 0.5\right] \\
  &= 0.97\,\mathrm{kN}/\mathrm{m}^{2}
\end{aligned}
$$

## Im Code

- [[opencivil.mauerwerk.querlast#erdbeben_schreiben|erdbeben_schreiben]]

## Themen

- [[Mauerwerk]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Im Erdbeben schütteln die Decken auch die Wände, die das Gebäude nicht
aussteifen. Eine solche Wand ist ein sekundäres Bauteil: Sie muss die Kraft
aus ihrer eigenen Masse quer zu sich tragen (SIA 261:2020, 16.7.1).
Gl. (49) gibt diese Kraft im Schwerpunkt eines Bauteils mit dem
Eigengewicht $G_a$, in beiden waagrechten Richtungen:

$$
F_a = \frac{\gamma_f\, a_{gd}\, S\, G_a}{g\, q_a} \cdot \left[\frac{3\,(1 + z_a/h)}{1 + (1 - T_a/T_1)^2} - 0.5\right] \ge \frac{\gamma_f\, a_{gd}\, S\, G_a}{g\, q_a}
$$

Der Bruch vor der Klammer ist die Kraft am Boden. Die Klammer sagt, wie das
Gebäude sie verstärkt: Mit der Höhe $z_a$ wächst die Beschleunigung, und
schwingt das Bauteil im Takt des Gebäudes, $T_a = T_1$, schaukelt es sich
am stärksten auf.

Die Schwingzeit einer Wand kennt man selten. Das Werkzeug setzt darum
$T_a = T_1$, das Ungünstigste – nach Vorgabe, nicht nachgeschlagen, auch für
eine tragende Wand. Die Klammer wird $3\,(1 + z_a/h) - 0.5$, zwischen 2.5
am Fundament und 5.5 auf dem Dach, und die untere Grenze gilt nie. Je m²
Wand ist $G_a$ ihr Eigengewicht $g_k$. Für das Bauteil gilt $q_a = 1.5$
(16.7.3); den Wert 1.0 für Abheben und Kippen braucht das Werkzeug nicht,
es prüft beides nicht. $z_a$ misst es bis zur Mitte der Wand, wo ihr
Schwerpunkt liegt.

Beispiel: Zone Z2, Baugrundklasse C, Bauwerksklasse I, also
$\gamma_f$ = 1.0, $a_{gd}$ = 1.0 m/s² und $S$ = 1.45. Eine Wand aus
Kalksandstein, 175 mm dick, wiegt 3.15 kN/m²; ihre Mitte liegt 1.35 m über
dem Fundament eines 6 m hohen Gebäudes. Die Klammer ist
$3 \cdot (1 + 1.35/6) - 0.5 = 3.18$, und
$p_E = 1.0 \cdot 1.0 \cdot 1.45 \cdot 3.15/(10 \cdot 1.5) \cdot 3.18$
= 0.97 kN/m².
