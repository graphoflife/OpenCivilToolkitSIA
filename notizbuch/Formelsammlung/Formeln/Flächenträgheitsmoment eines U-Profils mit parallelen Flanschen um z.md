---
erzeugt: 7df1c7bcad17
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Flächenträgheitsmoment um z, «UPE 200 um z» (UPE 200, um z, die schwache Achse)»*

$$
I_{z} = \frac{h_{\text{Q15}} \cdot \left(t_{w}\right)^{3}}{12} + \frac{t_{f} \cdot \left(b_{\text{Q15}} - t_{w}\right)^{3}}{6} + h_{\text{Q15}} \cdot t_{w} \cdot \left(e_{y} - \frac{t_{w}}{2}\right)^{2} + 2 \cdot \left(b_{\text{Q15}} - t_{w}\right) \cdot t_{f} \cdot \left(\frac{b_{\text{Q15}} + t_{w}}{2} - e_{y}\right)^{2} + 2 \cdot \left(0.00755 \cdot \left(r_{\text{Q15}}\right)^{4} + 0.2146 \cdot \left(r_{\text{Q15}}\right)^{2} \cdot \left(t_{w} + 0.2234 \cdot r_{\text{Q15}} - e_{y}\right)^{2}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $h_{\text{Q15}}$ | Höhe, UPE 200 um z | mm | Vorgabe |
| $t_{w}$ | Stegdicke, UPE 200 um z | mm | Vorgabe |
| $t_{f}$ | Flanschdicke, UPE 200 um z | mm | Vorgabe |
| $b_{\text{Q15}}$ | Breite, UPE 200 um z | mm | Vorgabe |
| $e_{y}$ | Abstand des Schwerpunkts vom Rücken, UPE 200 um z | mm | [[Schwerpunkt eines U-Profils mit parallelen Flanschen]] |
| $r_{\text{Q15}}$ | Ausrundung, UPE 200 um z | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  I_{z,\text{Q15}} &= \frac{h_{\text{Q15}} \cdot \left(t_{w,\text{Q15}}\right)^{3}}{12} + \frac{t_{f,\text{Q15}} \cdot \left(b_{\text{Q15}} - t_{w,\text{Q15}}\right)^{3}}{6} + h_{\text{Q15}} \cdot t_{w,\text{Q15}} \cdot \left(e_{y,\text{Q15}} - \frac{t_{w,\text{Q15}}}{2}\right)^{2} + 2 \cdot \left(b_{\text{Q15}} - t_{w,\text{Q15}}\right) \cdot t_{f,\text{Q15}} \cdot \left(\frac{b_{\text{Q15}} + t_{w,\text{Q15}}}{2} - e_{y,\text{Q15}}\right)^{2} + 2 \cdot \left(0.00755 \cdot \left(r_{\text{Q15}}\right)^{4} + 0.2146 \cdot \left(r_{\text{Q15}}\right)^{2} \cdot \left(t_{w,\text{Q15}} + 0.2234 \cdot r_{\text{Q15}} - e_{y,\text{Q15}}\right)^{2}\right) \\
  &= \frac{200\,\mathrm{mm} \cdot \left(6\,\mathrm{mm}\right)^{3}}{12} + \frac{11\,\mathrm{mm} \cdot \left(80\,\mathrm{mm} - 6\,\mathrm{mm}\right)^{3}}{6} + 200\,\mathrm{mm} \cdot 6\,\mathrm{mm} \cdot \left(25.6\,\mathrm{mm} - \frac{6\,\mathrm{mm}}{2}\right)^{2} + 2 \cdot \left(80\,\mathrm{mm} - 6\,\mathrm{mm}\right) \cdot 11\,\mathrm{mm} \cdot \left(\frac{80\,\mathrm{mm} + 6\,\mathrm{mm}}{2} - 25.6\,\mathrm{mm}\right)^{2} + 2 \cdot \left(0.00755 \cdot \left(13\,\mathrm{mm}\right)^{4} + 0.2146 \cdot \left(13\,\mathrm{mm}\right)^{2} \cdot \left(6\,\mathrm{mm} + 0.2234 \cdot 13\,\mathrm{mm} - 25.6\,\mathrm{mm}\right)^{2}\right) \\
  &= 187.3\,\mathrm{cm}^{4}
\end{aligned}
$$

## Im Code

- [[opencivil.stabwerk.profilformen]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Zur Achse $z$ ist das U nicht symmetrisch: sie geht durch den Schwerpunkt,
$e_y$ vom Rücken entfernt
([[Schwerpunkt eines U-Profils mit parallelen Flanschen]]). Jeder Teil
bringt sein Eigenträgheitsmoment und den Steineranteil mit seinem Abstand
von dieser Achse: der Steg liegt $t_w/2$ vom Rücken, die Flansche
$(b + t_w)/2$, die Zwickel $t_w + 0.2234\,r$.
