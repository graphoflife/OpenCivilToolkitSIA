---
erzeugt: 90eaf6bd591e
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Flächenträgheitsmoment um y, «UNP 200 um y» (UNP 200, um y, die starke Achse)»*

$$
I_{y} = \frac{b_{\text{Q16}} \cdot \left(h_{\text{Q16}}\right)^{3}}{12} - \frac{\left(b_{\text{Q16}} - t_{w}\right) \cdot \left(h_{\text{Q16}} - t_{1} - t_{2}\right) \cdot \left(\left(h_{\text{Q16}} - 2 \cdot t_{1}\right)^{2} + \left(h_{\text{Q16}} - 2 \cdot t_{2}\right)^{2}\right)}{24} + 2 \cdot \left(0.00755 \cdot \left(r_{1}\right)^{4} + 0.2146 \cdot \left(r_{1}\right)^{2} \cdot \left(\frac{h_{\text{Q16}}}{2} - t_{1} - 0.2234 \cdot r_{1}\right)^{2}\right) - 2 \cdot \left(0.00755 \cdot \left(r_{2}\right)^{4} + 0.2146 \cdot \left(r_{2}\right)^{2} \cdot \left(\frac{h_{\text{Q16}}}{2} - t_{2} + 0.2234 \cdot r_{2}\right)^{2}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $b_{\text{Q16}}$ | Breite, UNP 200 um y | mm | Vorgabe |
| $h_{\text{Q16}}$ | Höhe, UNP 200 um y | mm | Vorgabe |
| $t_{w}$ | Stegdicke, UNP 200 um y | mm | Vorgabe |
| $t_{1}$ | Flanschdicke am Steg, UNP 200 um y | mm | [[Dicke des geneigten Flanschs am Steg]] |
| $t_{2}$ | Flanschdicke an der Spitze, UNP 200 um y | mm | [[Dicke des geneigten Flanschs an der Spitze]] |
| $r_{1}$ | Ausrundung am Steg, UNP 200 um y | mm | Vorgabe |
| $r_{2}$ | Rundung an der Flanschspitze, UNP 200 um y | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  I_{y,\text{Q16}} &= \frac{b_{\text{Q16}} \cdot \left(h_{\text{Q16}}\right)^{3}}{12} - \frac{\left(b_{\text{Q16}} - t_{w,\text{Q16}}\right) \cdot \left(h_{\text{Q16}} - t_{1,\text{Q16}} - t_{2,\text{Q16}}\right) \cdot \left(\left(h_{\text{Q16}} - 2 \cdot t_{1,\text{Q16}}\right)^{2} + \left(h_{\text{Q16}} - 2 \cdot t_{2,\text{Q16}}\right)^{2}\right)}{24} + 2 \cdot \left(0.00755 \cdot \left(r_{1,\text{Q16}}\right)^{4} + 0.2146 \cdot \left(r_{1,\text{Q16}}\right)^{2} \cdot \left(\frac{h_{\text{Q16}}}{2} - t_{1,\text{Q16}} - 0.2234 \cdot r_{1,\text{Q16}}\right)^{2}\right) - 2 \cdot \left(0.00755 \cdot \left(r_{2,\text{Q16}}\right)^{4} + 0.2146 \cdot \left(r_{2,\text{Q16}}\right)^{2} \cdot \left(\frac{h_{\text{Q16}}}{2} - t_{2,\text{Q16}} + 0.2234 \cdot r_{2,\text{Q16}}\right)^{2}\right) \\
  &= \frac{75\,\mathrm{mm} \cdot \left(200\,\mathrm{mm}\right)^{3}}{12} - \frac{\left(75\,\mathrm{mm} - 8.5\,\mathrm{mm}\right) \cdot \left(200\,\mathrm{mm} - 13.82\,\mathrm{mm} - 8.5\,\mathrm{mm}\right) \cdot \left(\left(200\,\mathrm{mm} - 2 \cdot 13.82\,\mathrm{mm}\right)^{2} + \left(200\,\mathrm{mm} - 2 \cdot 8.5\,\mathrm{mm}\right)^{2}\right)}{24} + 2 \cdot \left(0.00755 \cdot \left(11.5\,\mathrm{mm}\right)^{4} + 0.2146 \cdot \left(11.5\,\mathrm{mm}\right)^{2} \cdot \left(\frac{200\,\mathrm{mm}}{2} - 13.82\,\mathrm{mm} - 0.2234 \cdot 11.5\,\mathrm{mm}\right)^{2}\right) - 2 \cdot \left(0.00755 \cdot \left(6\,\mathrm{mm}\right)^{4} + 0.2146 \cdot \left(6\,\mathrm{mm}\right)^{2} \cdot \left(\frac{200\,\mathrm{mm}}{2} - 8.5\,\mathrm{mm} + 0.2234 \cdot 6\,\mathrm{mm}\right)^{2}\right) \\
  &= 1915.06\,\mathrm{cm}^{4}
\end{aligned}
$$

## Im Code

- [[opencivil.stahlprofile.formen]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie beim Rechteck $b \times h$, weniger die Lücke zwischen den Flanschen.
Die Lücke ist an jeder Stelle so hoch wie $h - 2t(x)$, und diese Höhe
ändert sich linear vom Steg zur Spitze. Ihr Trägheitsmoment um die Mitte
ist das Integral von $(h - 2t)^3/12$ über ihre Breite; mit linearer Höhe
wird daraus $(b - t_w)\,(h - t_1 - t_2)\,((h - 2t_1)^2 + (h - 2t_2)^2)/24$.

Dazu kommen die zwei Ausrundungen am Steg, weg gehen die zwei Rundungen an
den Spitzen, beide als Zwickel des rechten Winkels wie bei der
[[Fläche eines U-Profils mit geneigten Flanschen]]. Die Werte der Tabelle
des Benutzers trifft das auf 0.6 %.
