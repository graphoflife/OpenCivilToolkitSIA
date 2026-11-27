---
erzeugt: b4ce838bab33
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Flächenträgheitsmoment um y, «UPE 200 um y» (UPE 200, um y, die starke Achse)»*

$$
I_{y} = \frac{t_{w} \cdot \left(h_{\text{Q14}}\right)^{3}}{12} + \frac{\left(b_{\text{Q14}} - t_{w}\right) \cdot \left(t_{f}\right)^{3}}{6} + \frac{\left(b_{\text{Q14}} - t_{w}\right) \cdot t_{f} \cdot \left(h_{\text{Q14}} - t_{f}\right)^{2}}{2} + 2 \cdot \left(0.00755 \cdot \left(r_{\text{Q14}}\right)^{4} + 0.2146 \cdot \left(r_{\text{Q14}}\right)^{2} \cdot \left(\frac{h_{\text{Q14}}}{2} - t_{f} - 0.2234 \cdot r_{\text{Q14}}\right)^{2}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $t_{w}$ | Stegdicke, UPE 200 um y | mm | Vorgabe |
| $h_{\text{Q14}}$ | Höhe, UPE 200 um y | mm | Vorgabe |
| $b_{\text{Q14}}$ | Breite, UPE 200 um y | mm | Vorgabe |
| $t_{f}$ | Flanschdicke, UPE 200 um y | mm | Vorgabe |
| $r_{\text{Q14}}$ | Ausrundung, UPE 200 um y | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  I_{y,\text{Q14}} &= \frac{t_{w,\text{Q14}} \cdot \left(h_{\text{Q14}}\right)^{3}}{12} + \frac{\left(b_{\text{Q14}} - t_{w,\text{Q14}}\right) \cdot \left(t_{f,\text{Q14}}\right)^{3}}{6} + \frac{\left(b_{\text{Q14}} - t_{w,\text{Q14}}\right) \cdot t_{f,\text{Q14}} \cdot \left(h_{\text{Q14}} - t_{f,\text{Q14}}\right)^{2}}{2} + 2 \cdot \left(0.00755 \cdot \left(r_{\text{Q14}}\right)^{4} + 0.2146 \cdot \left(r_{\text{Q14}}\right)^{2} \cdot \left(\frac{h_{\text{Q14}}}{2} - t_{f,\text{Q14}} - 0.2234 \cdot r_{\text{Q14}}\right)^{2}\right) \\
  &= \frac{6\,\mathrm{mm} \cdot \left(200\,\mathrm{mm}\right)^{3}}{12} + \frac{\left(80\,\mathrm{mm} - 6\,\mathrm{mm}\right) \cdot \left(11\,\mathrm{mm}\right)^{3}}{6} + \frac{\left(80\,\mathrm{mm} - 6\,\mathrm{mm}\right) \cdot 11\,\mathrm{mm} \cdot \left(200\,\mathrm{mm} - 11\,\mathrm{mm}\right)^{2}}{2} + 2 \cdot \left(0.00755 \cdot \left(13\,\mathrm{mm}\right)^{4} + 0.2146 \cdot \left(13\,\mathrm{mm}\right)^{2} \cdot \left(\frac{200\,\mathrm{mm}}{2} - 11\,\mathrm{mm} - 0.2234 \cdot 13\,\mathrm{mm}\right)^{2}\right) \\
  &= 1909.3\,\mathrm{cm}^{4}
\end{aligned}
$$

## Im Code

- [[opencivil.stahlprofile.formen]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Steg über die ganze Höhe mit $t_w\,h^3/12$; die zwei Flansche neben
ihm mit ihrem Eigenanteil $(b - t_w)\,t_f^3/12$ und dem Steineranteil
$(b - t_w)\,t_f\,((h - t_f)/2)^2$; die zwei Zwickel der Ausrundungen mit
$0.00755\,r^4$ und ihrem Steineranteil. Das U ist zur Achse $y$
symmetrisch, sie liegt auf halber Höhe wie beim I. Die Formel der Tabelle
des Benutzers – nach Vorgabe, nicht nachgeschlagen.
