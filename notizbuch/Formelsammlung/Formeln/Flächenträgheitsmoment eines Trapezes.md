---
erzeugt: 3d703022f995
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Flächenträgheitsmoment, «Fundamentbalken» (Trapez)»*

$$
I_{\text{Q7}} = \frac{\left(h_{\text{Q7}}\right)^{3} \cdot \left(\left(b_{o}\right)^{2} + 4 \cdot b_{o} \cdot b_{u} + \left(b_{u}\right)^{2}\right)}{36 \cdot \left(b_{o} + b_{u}\right)}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $h_{\text{Q7}}$ | Höhe, Fundamentbalken | mm | Vorgabe |
| $b_{o}$ | Breite oben, Fundamentbalken | mm | Vorgabe |
| $b_{u}$ | Breite unten, Fundamentbalken | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  I_{\text{Q7}} &= \frac{\left(h_{\text{Q7}}\right)^{3} \cdot \left(\left(b_{o,\text{Q7}}\right)^{2} + 4 \cdot b_{o,\text{Q7}} \cdot b_{u,\text{Q7}} + \left(b_{u,\text{Q7}}\right)^{2}\right)}{36 \cdot \left(b_{o,\text{Q7}} + b_{u,\text{Q7}}\right)} \\
  &= \frac{\left(500\,\mathrm{mm}\right)^{3} \cdot \left(\left(600\,\mathrm{mm}\right)^{2} + 4 \cdot 600\,\mathrm{mm} \cdot 400\,\mathrm{mm} + \left(400\,\mathrm{mm}\right)^{2}\right)}{36 \cdot \left(600\,\mathrm{mm} + 400\,\mathrm{mm}\right)} \\
  &= 5138.89\,\cdot 10^{6}\,\mathrm{mm}^{4}
\end{aligned}
$$

## Im Code

- [[opencivil.stabwerk.querschnitte]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Um die Schwerachse des Trapezes, nicht um die halbe Höhe: bei ungleichen
Breiten liegt der Schwerpunkt näher an der breiteren Seite. Mit
$b_o = b_u = b$ wird daraus $b h^3 / 12$, das
[[Flächenträgheitsmoment eines Rechtecks|Rechteck]].
