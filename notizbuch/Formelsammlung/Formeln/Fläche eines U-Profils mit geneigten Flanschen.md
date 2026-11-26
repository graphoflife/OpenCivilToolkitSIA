---
erzeugt: e3cd7a17e9a2
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Querschnittsfläche, «UNP 200 um y» (UNP 200, um y, die starke Achse)»*

$$
A_{\text{Q16}} = b_{\text{Q16}} \cdot h_{\text{Q16}} - \left(b_{\text{Q16}} - t_{w}\right) \cdot \left(h_{\text{Q16}} - t_{1} - t_{2}\right) + 2 \cdot 0.2146 \cdot \left(\left(r_{1}\right)^{2} - \left(r_{2}\right)^{2}\right)
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
  A_{\text{Q16}} &= b_{\text{Q16}} \cdot h_{\text{Q16}} - \left(b_{\text{Q16}} - t_{w,\text{Q16}}\right) \cdot \left(h_{\text{Q16}} - t_{1,\text{Q16}} - t_{2,\text{Q16}}\right) + 2 \cdot 0.2146 \cdot \left(\left(r_{1,\text{Q16}}\right)^{2} - \left(r_{2,\text{Q16}}\right)^{2}\right) \\
  &= 75\,\mathrm{mm} \cdot 200\,\mathrm{mm} - \left(75\,\mathrm{mm} - 8.5\,\mathrm{mm}\right) \cdot \left(200\,\mathrm{mm} - 13.82\,\mathrm{mm} - 8.5\,\mathrm{mm}\right) + 2 \cdot 0.2146 \cdot \left(\left(11.5\,\mathrm{mm}\right)^{2} - \left(6\,\mathrm{mm}\right)^{2}\right) \\
  &= 32.26\,\mathrm{cm}^{2}
\end{aligned}
$$

## Gebraucht von

- [[Flächenträgheitsmoment eines U-Profils mit geneigten Flanschen um z]]
- [[Schwerpunkt eines U-Profils mit geneigten Flanschen]]

## Im Code

- [[opencivil.stahlprofile.formen]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das ganze Rechteck $b \times h$, weniger die Lücke zwischen den Flanschen:
sie ist $b - t_w$ breit, am Steg $h - 2t_1$ und an der Spitze $h - 2t_2$
hoch, im Mittel also $h - t_1 - t_2$. Dazu kommen die zwei Ausrundungen am
Steg mit $r_1$, weg gehen die zwei Rundungen an den Flanschspitzen mit
$r_2$ -- beide als Zwickel mit $0.2146\,r^2$.

Die Zwickel sind die des rechten Winkels, obwohl die Flansche geneigt
sind. Die Tabelle des Benutzers hat beim UNP nur Werte, keine Formeln; die
Rechnung trifft sie auf 0.6 %. Nach Vorgabe, nicht nachgeschlagen.
