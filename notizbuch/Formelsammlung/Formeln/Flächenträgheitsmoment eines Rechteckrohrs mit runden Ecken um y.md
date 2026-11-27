---
erzeugt: 8224fbaa611d
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Flächenträgheitsmoment um y, «RRK 200 x 100 x 8 um y» (RRK 200 x 100 x 8, um y, die starke Achse)»*

$$
I_{y} = \frac{b_{\text{Q18}} \cdot \left(h_{\text{Q18}}\right)^{3} - \left(b_{\text{Q18}} - 2 \cdot t_{\text{Q18}}\right) \cdot \left(h_{\text{Q18}} - 2 \cdot t_{\text{Q18}}\right)^{3}}{12} - 4 \cdot \left(0.00755 \cdot \left(r_{o}\right)^{4} + 0.2146 \cdot \left(r_{o}\right)^{2} \cdot \left(\frac{h_{\text{Q18}}}{2} - 0.2234 \cdot r_{o}\right)^{2}\right) + 4 \cdot \left(0.00755 \cdot \left(r_{i}\right)^{4} + 0.2146 \cdot \left(r_{i}\right)^{2} \cdot \left(\frac{h_{\text{Q18}}}{2} - t_{\text{Q18}} - 0.2234 \cdot r_{i}\right)^{2}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $b_{\text{Q18}}$ | Breite, RRK 200 x 100 x 8 um y | mm | Vorgabe |
| $h_{\text{Q18}}$ | Höhe, RRK 200 x 100 x 8 um y | mm | Vorgabe |
| $t_{\text{Q18}}$ | Wanddicke, RRK 200 x 100 x 8 um y | mm | Vorgabe |
| $r_{o}$ | Radius aussen, RRK 200 x 100 x 8 um y | mm | Vorgabe |
| $r_{i}$ | Radius innen, RRK 200 x 100 x 8 um y | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  I_{y,\text{Q18}} &= \frac{b_{\text{Q18}} \cdot \left(h_{\text{Q18}}\right)^{3} - \left(b_{\text{Q18}} - 2 \cdot t_{\text{Q18}}\right) \cdot \left(h_{\text{Q18}} - 2 \cdot t_{\text{Q18}}\right)^{3}}{12} - 4 \cdot \left(0.00755 \cdot \left(r_{o,\text{Q18}}\right)^{4} + 0.2146 \cdot \left(r_{o,\text{Q18}}\right)^{2} \cdot \left(\frac{h_{\text{Q18}}}{2} - 0.2234 \cdot r_{o,\text{Q18}}\right)^{2}\right) + 4 \cdot \left(0.00755 \cdot \left(r_{i,\text{Q18}}\right)^{4} + 0.2146 \cdot \left(r_{i,\text{Q18}}\right)^{2} \cdot \left(\frac{h_{\text{Q18}}}{2} - t_{\text{Q18}} - 0.2234 \cdot r_{i,\text{Q18}}\right)^{2}\right) \\
  &= \frac{100\,\mathrm{mm} \cdot \left(200\,\mathrm{mm}\right)^{3} - \left(100\,\mathrm{mm} - 2 \cdot 8\,\mathrm{mm}\right) \cdot \left(200\,\mathrm{mm} - 2 \cdot 8\,\mathrm{mm}\right)^{3}}{12} - 4 \cdot \left(0.00755 \cdot \left(20\,\mathrm{mm}\right)^{4} + 0.2146 \cdot \left(20\,\mathrm{mm}\right)^{2} \cdot \left(\frac{200\,\mathrm{mm}}{2} - 0.2234 \cdot 20\,\mathrm{mm}\right)^{2}\right) + 4 \cdot \left(0.00755 \cdot \left(12\,\mathrm{mm}\right)^{4} + 0.2146 \cdot \left(12\,\mathrm{mm}\right)^{2} \cdot \left(\frac{200\,\mathrm{mm}}{2} - 8\,\mathrm{mm} - 0.2234 \cdot 12\,\mathrm{mm}\right)^{2}\right) \\
  &= 2090.85\,\mathrm{cm}^{4}
\end{aligned}
$$

## Im Code

- [[opencivil.stahlprofile.formen#_rohr_traegheit|_rohr_traegheit]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das volle Rechteck $b \times h$ weniger das Loch $(b - 2t) \times (h - 2t)$,
beide um die Mitte: $(b\,h^3 - (b - 2t)\,(h - 2t)^3)/12$. Die runden Ecken
ändern das wenig. Aussen fehlen vier Zwickel mit $r_o$, ihr Schwerpunkt
liegt $h/2 - 0.2234\,r_o$ von der Achse. Innen kommen vier mit $r_i$ hinzu,
$h/2 - t - 0.2234\,r_i$ von der Achse. Jeder hat Eigen- und Steineranteil
wie beim [[Flächenträgheitsmoment eines I-Profils um y]].

Nach Vorgabe, nicht nachgeschlagen: die Formel der Tabelle des Benutzers.
Dort stehen die Beiwerte der Zwickel genau, hier gerundet wie beim
I-Profil; das ändert höchstens die fünfte Stelle. Kalt- und warmgefertigte
Rohre rechnen gleich, nur mit ihren eigenen Radien – siehe
[[Fläche eines Rechteckrohrs mit runden Ecken]].
