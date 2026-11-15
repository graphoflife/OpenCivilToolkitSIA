---
erzeugt: 504e1bf1a7c2
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Abstand des Schwerpunkts vom Rücken, «UNP 200 um z» (UNP 200, um z, die schwache Achse)»*

$$
e_{y} = \frac{\left(b_{\text{Q17}}\right)^{2} \cdot h_{\text{Q17}} / 2 - \frac{b_{\text{Q17}} - t_{w}}{6} \cdot \left(t_{w} \cdot \left(3 \cdot h_{\text{Q17}} - 4 \cdot t_{1} - 2 \cdot t_{2}\right) + b_{\text{Q17}} \cdot \left(3 \cdot h_{\text{Q17}} - 2 \cdot t_{1} - 4 \cdot t_{2}\right)\right) + 2 \cdot 0.2146 \cdot \left(r_{1}\right)^{2} \cdot \left(t_{w} + 0.2234 \cdot r_{1}\right) - 2 \cdot 0.2146 \cdot \left(r_{2}\right)^{2} \cdot \left(b_{\text{Q17}} - 0.2234 \cdot r_{2}\right)}{A_{\text{Q17}}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $b_{\text{Q17}}$ | Breite, UNP 200 um z | mm | Vorgabe |
| $h_{\text{Q17}}$ | Höhe, UNP 200 um z | mm | Vorgabe |
| $t_{w}$ | Stegdicke, UNP 200 um z | mm | Vorgabe |
| $t_{1}$ | Flanschdicke am Steg, UNP 200 um z | mm | [[Dicke des geneigten Flanschs am Steg]] |
| $t_{2}$ | Flanschdicke an der Spitze, UNP 200 um z | mm | [[Dicke des geneigten Flanschs an der Spitze]] |
| $r_{1}$ | Ausrundung am Steg, UNP 200 um z | mm | Vorgabe |
| $r_{2}$ | Rundung an der Flanschspitze, UNP 200 um z | mm | Vorgabe |
| $A_{\text{Q17}}$ | Querschnittsfläche, UNP 200 um z | cm² | [[Fläche eines U-Profils mit geneigten Flanschen]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  e_{y,\text{Q17}} &= \frac{\left(b_{\text{Q17}}\right)^{2} \cdot h_{\text{Q17}} / 2 - \frac{b_{\text{Q17}} - t_{w,\text{Q17}}}{6} \cdot \left(t_{w,\text{Q17}} \cdot \left(3 \cdot h_{\text{Q17}} - 4 \cdot t_{1,\text{Q17}} - 2 \cdot t_{2,\text{Q17}}\right) + b_{\text{Q17}} \cdot \left(3 \cdot h_{\text{Q17}} - 2 \cdot t_{1,\text{Q17}} - 4 \cdot t_{2,\text{Q17}}\right)\right) + 2 \cdot 0.2146 \cdot \left(r_{1,\text{Q17}}\right)^{2} \cdot \left(t_{w,\text{Q17}} + 0.2234 \cdot r_{1,\text{Q17}}\right) - 2 \cdot 0.2146 \cdot \left(r_{2,\text{Q17}}\right)^{2} \cdot \left(b_{\text{Q17}} - 0.2234 \cdot r_{2,\text{Q17}}\right)}{A_{\text{Q17}}} \\
  &= \frac{\left(75\,\mathrm{mm}\right)^{2} \cdot 200\,\mathrm{mm} / 2 - \frac{75\,\mathrm{mm} - 8.5\,\mathrm{mm}}{6} \cdot \left(8.5\,\mathrm{mm} \cdot \left(3 \cdot 200\,\mathrm{mm} - 4 \cdot 13.82\,\mathrm{mm} - 2 \cdot 8.5\,\mathrm{mm}\right) + 75\,\mathrm{mm} \cdot \left(3 \cdot 200\,\mathrm{mm} - 2 \cdot 13.82\,\mathrm{mm} - 4 \cdot 8.5\,\mathrm{mm}\right)\right) + 2 \cdot 0.2146 \cdot \left(11.5\,\mathrm{mm}\right)^{2} \cdot \left(8.5\,\mathrm{mm} + 0.2234 \cdot 11.5\,\mathrm{mm}\right) - 2 \cdot 0.2146 \cdot \left(6\,\mathrm{mm}\right)^{2} \cdot \left(75\,\mathrm{mm} - 0.2234 \cdot 6\,\mathrm{mm}\right)}{32.26\,\mathrm{cm}^{2}} \\
  &= 20.1\,\mathrm{mm}
\end{aligned}
$$

## Gebraucht von

- [[Flächenträgheitsmoment eines U-Profils mit geneigten Flanschen um z]]

## Im Code

- [[opencivil.stabwerk.profilformen]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Abstand des Schwerpunkts vom Rücken: die statischen Momente aller
Teile um den Rücken, geteilt durch die Fläche. Das Rechteck $b \times h$
bringt $b^2 h/2$. Die Lücke zwischen den Flanschen fehlt; bei linear
veränderlicher Höhe ist ihr Moment
$(b - t_w)/6 \cdot (t_w\,(3h - 4t_1 - 2t_2) + b\,(3h - 2t_1 - 4t_2))$.
Dazu kommen die Ausrundungen, $t_w + 0.2234\,r_1$ vom Rücken, und weg gehen
die Rundungen an den Spitzen, $b - 0.2234\,r_2$ vom Rücken.

Um diesen Punkt biegt sich das Profil um $z$. Die Werte der Tabelle des
Benutzers trifft er auf 1 %.
