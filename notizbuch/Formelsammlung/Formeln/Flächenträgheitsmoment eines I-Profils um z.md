---
erzeugt: 06ec9a192e77
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Flächenträgheitsmoment um z, «HEA 200 um z» (HEA 200, um z, die schwache Achse)»*

$$
I_{z} = \frac{t_{f} \cdot \left(b_{\text{Q13}}\right)^{3}}{6} + \frac{\left(h_{\text{Q13}} - 2 \cdot t_{f}\right) \cdot \left(t_{w}\right)^{3}}{12} + 4 \cdot \left(0.00755 \cdot \left(r_{\text{Q13}}\right)^{4} + 0.2146 \cdot \left(r_{\text{Q13}}\right)^{2} \cdot \left(\frac{t_{w}}{2} + 0.2234 \cdot r_{\text{Q13}}\right)^{2}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $t_{f}$ | Flanschdicke, HEA 200 um z | mm | Vorgabe |
| $b_{\text{Q13}}$ | Breite, HEA 200 um z | mm | Vorgabe |
| $h_{\text{Q13}}$ | Höhe, HEA 200 um z | mm | Vorgabe |
| $t_{w}$ | Stegdicke, HEA 200 um z | mm | Vorgabe |
| $r_{\text{Q13}}$ | Ausrundung, HEA 200 um z | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  I_{z,\text{Q13}} &= \frac{t_{f,\text{Q13}} \cdot \left(b_{\text{Q13}}\right)^{3}}{6} + \frac{\left(h_{\text{Q13}} - 2 \cdot t_{f,\text{Q13}}\right) \cdot \left(t_{w,\text{Q13}}\right)^{3}}{12} + 4 \cdot \left(0.00755 \cdot \left(r_{\text{Q13}}\right)^{4} + 0.2146 \cdot \left(r_{\text{Q13}}\right)^{2} \cdot \left(\frac{t_{w,\text{Q13}}}{2} + 0.2234 \cdot r_{\text{Q13}}\right)^{2}\right) \\
  &= \frac{10\,\mathrm{mm} \cdot \left(200\,\mathrm{mm}\right)^{3}}{6} + \frac{\left(190\,\mathrm{mm} - 2 \cdot 10\,\mathrm{mm}\right) \cdot \left(6.5\,\mathrm{mm}\right)^{3}}{12} + 4 \cdot \left(0.00755 \cdot \left(18\,\mathrm{mm}\right)^{4} + 0.2146 \cdot \left(18\,\mathrm{mm}\right)^{2} \cdot \left(\frac{6.5\,\mathrm{mm}}{2} + 0.2234 \cdot 18\,\mathrm{mm}\right)^{2}\right) \\
  &= 1335.51\,\mathrm{cm}^{4}
\end{aligned}
$$

## Im Code

- [[opencivil.stabwerk.profilformen]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Um die schwache Achse, senkrecht durch den Steg. Die Flansche tragen fast
alles, je $t_f\,b^3/12$; der Steg liegt mit $(h - 2t_f)\,t_w^3/12$ auf der
Achse. Die vier Zwickel liegen $t_w/2 + 0.2234\,r$ neben ihr, mit Eigen-
und Steineranteil wie beim [[Flächenträgheitsmoment eines I-Profils um y]].

Im Balkensystem gilt es, wenn das Profil «um z» gebogen wird: der Steg
steht dann quer zur Ebene des Rahmens.
