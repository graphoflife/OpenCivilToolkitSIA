---
erzeugt: 3414f5208b5b
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Flächenträgheitsmoment, «Walzprofil» (Doppel-T)»*

$$
I_{\text{Q6}} = \frac{b_{\text{Q6}} \cdot \left(h_{\text{Q6}}\right)^{3} - \left(b_{\text{Q6}} - t_{w}\right) \cdot \left(h_{\text{Q6}} - 2 \cdot t_{f}\right)^{3}}{12}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $b_{\text{Q6}}$ | Flanschbreite, Walzprofil | mm | Vorgabe |
| $h_{\text{Q6}}$ | Höhe, Walzprofil | mm | Vorgabe |
| $t_{w}$ | Stegdicke, Walzprofil | mm | Vorgabe |
| $t_{f}$ | Flanschdicke, Walzprofil | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  I_{\text{Q6}} &= \frac{b_{\text{Q6}} \cdot \left(h_{\text{Q6}}\right)^{3} - \left(b_{\text{Q6}} - t_{w,\text{Q6}}\right) \cdot \left(h_{\text{Q6}} - 2 \cdot t_{f,\text{Q6}}\right)^{3}}{12} \\
  &= \frac{300\,\mathrm{mm} \cdot \left(300\,\mathrm{mm}\right)^{3} - \left(300\,\mathrm{mm} - 11\,\mathrm{mm}\right) \cdot \left(300\,\mathrm{mm} - 2 \cdot 19\,\mathrm{mm}\right)^{3}}{12} \\
  &= 241.87\,\cdot 10^{6}\,\mathrm{mm}^{4}
\end{aligned}
$$

## Im Code

- [[opencivil.stabwerk.querschnitte]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das volle Rechteck $b \times h$ minus die beiden Aussparungen neben dem Steg,
die zusammen ein Rechteck $(b - t_w) \times (h - 2 t_f)$ bilden -- beide
symmetrisch zur selben Achse. Fast alles kommt von den Flanschen, weit weg
von der Achse: darum ist das Doppel-T das Profil für Biegung.
