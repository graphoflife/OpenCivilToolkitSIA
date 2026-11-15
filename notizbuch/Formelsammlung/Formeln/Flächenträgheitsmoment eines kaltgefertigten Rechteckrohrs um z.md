---
erzeugt: 46bd6fe8bfcc
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Flächenträgheitsmoment um z, «RRK 200 x 100 x 8 um z» (RRK 200 x 100 x 8, um z, die schwache Achse)»*

$$
I_{z} = \frac{h_{\text{Q19}} \cdot \left(b_{\text{Q19}}\right)^{3} - \left(h_{\text{Q19}} - 2 \cdot t_{\text{Q19}}\right) \cdot \left(b_{\text{Q19}} - 2 \cdot t_{\text{Q19}}\right)^{3}}{12} - 4 \cdot \left(0.00755 \cdot \left(r_{o}\right)^{4} + 0.2146 \cdot \left(r_{o}\right)^{2} \cdot \left(\frac{b_{\text{Q19}}}{2} - 0.2234 \cdot r_{o}\right)^{2}\right) + 4 \cdot \left(0.00755 \cdot \left(r_{i}\right)^{4} + 0.2146 \cdot \left(r_{i}\right)^{2} \cdot \left(\frac{b_{\text{Q19}}}{2} - t_{\text{Q19}} - 0.2234 \cdot r_{i}\right)^{2}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $h_{\text{Q19}}$ | Höhe, RRK 200 x 100 x 8 um z | mm | Vorgabe |
| $b_{\text{Q19}}$ | Breite, RRK 200 x 100 x 8 um z | mm | Vorgabe |
| $t_{\text{Q19}}$ | Wanddicke, RRK 200 x 100 x 8 um z | mm | Vorgabe |
| $r_{o}$ | Radius aussen, RRK 200 x 100 x 8 um z | mm | Vorgabe |
| $r_{i}$ | Radius innen, RRK 200 x 100 x 8 um z | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  I_{z,\text{Q19}} &= \frac{h_{\text{Q19}} \cdot \left(b_{\text{Q19}}\right)^{3} - \left(h_{\text{Q19}} - 2 \cdot t_{\text{Q19}}\right) \cdot \left(b_{\text{Q19}} - 2 \cdot t_{\text{Q19}}\right)^{3}}{12} - 4 \cdot \left(0.00755 \cdot \left(r_{o,\text{Q19}}\right)^{4} + 0.2146 \cdot \left(r_{o,\text{Q19}}\right)^{2} \cdot \left(\frac{b_{\text{Q19}}}{2} - 0.2234 \cdot r_{o,\text{Q19}}\right)^{2}\right) + 4 \cdot \left(0.00755 \cdot \left(r_{i,\text{Q19}}\right)^{4} + 0.2146 \cdot \left(r_{i,\text{Q19}}\right)^{2} \cdot \left(\frac{b_{\text{Q19}}}{2} - t_{\text{Q19}} - 0.2234 \cdot r_{i,\text{Q19}}\right)^{2}\right) \\
  &= \frac{200\,\mathrm{mm} \cdot \left(100\,\mathrm{mm}\right)^{3} - \left(200\,\mathrm{mm} - 2 \cdot 8\,\mathrm{mm}\right) \cdot \left(100\,\mathrm{mm} - 2 \cdot 8\,\mathrm{mm}\right)^{3}}{12} - 4 \cdot \left(0.00755 \cdot \left(20\,\mathrm{mm}\right)^{4} + 0.2146 \cdot \left(20\,\mathrm{mm}\right)^{2} \cdot \left(\frac{100\,\mathrm{mm}}{2} - 0.2234 \cdot 20\,\mathrm{mm}\right)^{2}\right) + 4 \cdot \left(0.00755 \cdot \left(12\,\mathrm{mm}\right)^{4} + 0.2146 \cdot \left(12\,\mathrm{mm}\right)^{2} \cdot \left(\frac{100\,\mathrm{mm}}{2} - 8\,\mathrm{mm} - 0.2234 \cdot 12\,\mathrm{mm}\right)^{2}\right) \\
  &= 705.36\,\mathrm{cm}^{4}
\end{aligned}
$$

## Im Code

- [[opencivil.stabwerk.profilformen#_rohr_traegheit|_rohr_traegheit]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Dieselbe Rechnung wie beim
[[Flächenträgheitsmoment eines kaltgefertigten Rechteckrohrs um y]], mit
$b$ und $h$ vertauscht: um $z$ steht die Breite $b$ quer zur Achse. Beim
quadratischen Rohr ist $I_z = I_y$.
