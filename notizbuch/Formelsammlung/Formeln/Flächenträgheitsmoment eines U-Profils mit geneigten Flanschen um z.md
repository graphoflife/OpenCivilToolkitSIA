---
erzeugt: d853d6a969f8
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Flächenträgheitsmoment um z, «UNP 200 um z» (UNP 200, um z, die schwache Achse)»*

$$
I_{z} = \frac{\left(b_{\text{Q17}}\right)^{3} \cdot h_{\text{Q17}}}{3} - \frac{b_{\text{Q17}} - t_{w}}{12} \cdot \left(\left(h_{\text{Q17}} - 2 \cdot t_{1}\right) \cdot \left(3 \cdot \left(t_{w}\right)^{2} + 2 \cdot t_{w} \cdot b_{\text{Q17}} + \left(b_{\text{Q17}}\right)^{2}\right) + \left(h_{\text{Q17}} - 2 \cdot t_{2}\right) \cdot \left(\left(t_{w}\right)^{2} + 2 \cdot t_{w} \cdot b_{\text{Q17}} + 3 \cdot \left(b_{\text{Q17}}\right)^{2}\right)\right) + 2 \cdot \left(0.00755 \cdot \left(r_{1}\right)^{4} + 0.2146 \cdot \left(r_{1}\right)^{2} \cdot \left(t_{w} + 0.2234 \cdot r_{1}\right)^{2}\right) - 2 \cdot \left(0.00755 \cdot \left(r_{2}\right)^{4} + 0.2146 \cdot \left(r_{2}\right)^{2} \cdot \left(b_{\text{Q17}} - 0.2234 \cdot r_{2}\right)^{2}\right) - A_{\text{Q17}} \cdot \left(e_{y}\right)^{2}
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
| $e_{y}$ | Abstand des Schwerpunkts vom Rücken, UNP 200 um z | mm | [[Schwerpunkt eines U-Profils mit geneigten Flanschen]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  I_{z,\text{Q17}} &= \frac{\left(b_{\text{Q17}}\right)^{3} \cdot h_{\text{Q17}}}{3} - \frac{b_{\text{Q17}} - t_{w,\text{Q17}}}{12} \cdot \left(\left(h_{\text{Q17}} - 2 \cdot t_{1,\text{Q17}}\right) \cdot \left(3 \cdot \left(t_{w,\text{Q17}}\right)^{2} + 2 \cdot t_{w,\text{Q17}} \cdot b_{\text{Q17}} + \left(b_{\text{Q17}}\right)^{2}\right) + \left(h_{\text{Q17}} - 2 \cdot t_{2,\text{Q17}}\right) \cdot \left(\left(t_{w,\text{Q17}}\right)^{2} + 2 \cdot t_{w,\text{Q17}} \cdot b_{\text{Q17}} + 3 \cdot \left(b_{\text{Q17}}\right)^{2}\right)\right) + 2 \cdot \left(0.00755 \cdot \left(r_{1,\text{Q17}}\right)^{4} + 0.2146 \cdot \left(r_{1,\text{Q17}}\right)^{2} \cdot \left(t_{w,\text{Q17}} + 0.2234 \cdot r_{1,\text{Q17}}\right)^{2}\right) - 2 \cdot \left(0.00755 \cdot \left(r_{2,\text{Q17}}\right)^{4} + 0.2146 \cdot \left(r_{2,\text{Q17}}\right)^{2} \cdot \left(b_{\text{Q17}} - 0.2234 \cdot r_{2,\text{Q17}}\right)^{2}\right) - A_{\text{Q17}} \cdot \left(e_{y,\text{Q17}}\right)^{2} \\
  &= \frac{\left(75\,\mathrm{mm}\right)^{3} \cdot 200\,\mathrm{mm}}{3} - \frac{75\,\mathrm{mm} - 8.5\,\mathrm{mm}}{12} \cdot \left(\left(200\,\mathrm{mm} - 2 \cdot 13.82\,\mathrm{mm}\right) \cdot \left(3 \cdot \left(8.5\,\mathrm{mm}\right)^{2} + 2 \cdot 8.5\,\mathrm{mm} \cdot 75\,\mathrm{mm} + \left(75\,\mathrm{mm}\right)^{2}\right) + \left(200\,\mathrm{mm} - 2 \cdot 8.5\,\mathrm{mm}\right) \cdot \left(\left(8.5\,\mathrm{mm}\right)^{2} + 2 \cdot 8.5\,\mathrm{mm} \cdot 75\,\mathrm{mm} + 3 \cdot \left(75\,\mathrm{mm}\right)^{2}\right)\right) + 2 \cdot \left(0.00755 \cdot \left(11.5\,\mathrm{mm}\right)^{4} + 0.2146 \cdot \left(11.5\,\mathrm{mm}\right)^{2} \cdot \left(8.5\,\mathrm{mm} + 0.2234 \cdot 11.5\,\mathrm{mm}\right)^{2}\right) - 2 \cdot \left(0.00755 \cdot \left(6\,\mathrm{mm}\right)^{4} + 0.2146 \cdot \left(6\,\mathrm{mm}\right)^{2} \cdot \left(75\,\mathrm{mm} - 0.2234 \cdot 6\,\mathrm{mm}\right)^{2}\right) - 32.26\,\mathrm{cm}^{2} \cdot \left(20.1\,\mathrm{mm}\right)^{2} \\
  &= 147.08\,\mathrm{cm}^{4}
\end{aligned}
$$

## Im Code

- [[opencivil.stabwerk.profilformen]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Um die senkrechte Achse durch den Schwerpunkt. Gerechnet wird zuerst um den
Rücken: das Rechteck mit $b^3 h/3$, weniger die Lücke zwischen den
Flanschen -- mit ihrer linear veränderlichen Höhe das Integral von
$x^2\,(h - 2t(x))$ von $t_w$ bis $b$ --, dazu die Zwickel. Dann hin zum
Schwerpunkt: weniger $A\,e_y^2$, der Satz von Steiner rückwärts.

Diesen Wert trifft die Rechnung am wenigsten genau, auf 1.4 % der Tabelle
des Benutzers; die Tabelle selbst hat drei Stellen.
