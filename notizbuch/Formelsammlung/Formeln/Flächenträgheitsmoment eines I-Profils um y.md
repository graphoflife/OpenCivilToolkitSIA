---
erzeugt: 6bce853e5922
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Flächenträgheitsmoment um y, «Träger» (HEB 300, um y, die starke Achse)»*

$$
I_{y} = \frac{t_{w} \cdot \left(h_{\text{Q11}} - 2 \cdot t_{f}\right)^{3}}{12} + \frac{b_{\text{Q11}} \cdot \left(t_{f}\right)^{3}}{6} + \frac{b_{\text{Q11}} \cdot t_{f} \cdot \left(h_{\text{Q11}} - t_{f}\right)^{2}}{2} + 4 \cdot \left(0.00755 \cdot \left(r_{\text{Q11}}\right)^{4} + 0.2146 \cdot \left(r_{\text{Q11}}\right)^{2} \cdot \left(\frac{h_{\text{Q11}}}{2} - t_{f} - 0.2234 \cdot r_{\text{Q11}}\right)^{2}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $t_{w}$ | Stegdicke, Träger | mm | Vorgabe |
| $h_{\text{Q11}}$ | Höhe, Träger | mm | Vorgabe |
| $t_{f}$ | Flanschdicke, Träger | mm | Vorgabe |
| $b_{\text{Q11}}$ | Breite, Träger | mm | Vorgabe |
| $r_{\text{Q11}}$ | Ausrundung, Träger | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  I_{y,\text{Q11}} &= \frac{t_{w,\text{Q11}} \cdot \left(h_{\text{Q11}} - 2 \cdot t_{f,\text{Q11}}\right)^{3}}{12} + \frac{b_{\text{Q11}} \cdot \left(t_{f,\text{Q11}}\right)^{3}}{6} + \frac{b_{\text{Q11}} \cdot t_{f,\text{Q11}} \cdot \left(h_{\text{Q11}} - t_{f,\text{Q11}}\right)^{2}}{2} + 4 \cdot \left(0.00755 \cdot \left(r_{\text{Q11}}\right)^{4} + 0.2146 \cdot \left(r_{\text{Q11}}\right)^{2} \cdot \left(\frac{h_{\text{Q11}}}{2} - t_{f,\text{Q11}} - 0.2234 \cdot r_{\text{Q11}}\right)^{2}\right) \\
  &= \frac{11\,\mathrm{mm} \cdot \left(300\,\mathrm{mm} - 2 \cdot 19\,\mathrm{mm}\right)^{3}}{12} + \frac{300\,\mathrm{mm} \cdot \left(19\,\mathrm{mm}\right)^{3}}{6} + \frac{300\,\mathrm{mm} \cdot 19\,\mathrm{mm} \cdot \left(300\,\mathrm{mm} - 19\,\mathrm{mm}\right)^{2}}{2} + 4 \cdot \left(0.00755 \cdot \left(27\,\mathrm{mm}\right)^{4} + 0.2146 \cdot \left(27\,\mathrm{mm}\right)^{2} \cdot \left(\frac{300\,\mathrm{mm}}{2} - 19\,\mathrm{mm} - 0.2234 \cdot 27\,\mathrm{mm}\right)^{2}\right) \\
  &= 25165.66\,\mathrm{cm}^{4}
\end{aligned}
$$

## Gebraucht von

- [[Biegesteifigkeit]]

## Im Code

- [[opencivil.stabwerk.profilformen]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Um die starke Achse, waagrecht durch die halbe Höhe. Drei Teile: der Steg
mit $t_w\,(h - 2t_f)^3/12$; die beiden Flansche mit ihrem Eigenanteil
$b\,t_f^3/12$ und dem Steineranteil $b\,t_f\,((h - t_f)/2)^2$; die vier
Ausrundungen. Ein Zwickel trägt sein Eigenträgheitsmoment $0.00755\,r^4$
bei und mit seiner Fläche $0.2146\,r^2$ den Steineranteil: sein
Schwerpunkt liegt $0.2234\,r$ von beiden Kanten entfernt, also
$h/2 - t_f - 0.2234\,r$ von der Achse.

Die drei Beiwerte sind gerundet wie in der Tabelle des Benutzers. Genau
wären es $1 - \pi/4$, $(10 - 3\pi)/(12 - 3\pi)$ und
$1/3 - \pi/16 - 1/(3\,(12 - 3\pi))$. Nach Vorgabe, nicht nachgeschlagen.

Im Balkensystem gilt es, wenn das Profil «um y» gebogen wird: der Steg
liegt dann in der Ebene des Rahmens.
