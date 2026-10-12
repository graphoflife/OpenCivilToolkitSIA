---
erzeugt: 1a9d5894fd53
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Flächenträgheitsmoment, «Plattenbalken» (T-Querschnitt)»*

$$
I_{\text{Q5}} = \frac{b_{\text{Q5}} \cdot \left(h_{f}\right)^{3}}{12} + b_{\text{Q5}} \cdot h_{f} \cdot \left(z_{S} - \frac{h_{f}}{2}\right)^{2} + \frac{b_{w} \cdot \left(h_{\text{Q5}} - h_{f}\right)^{3}}{12} + b_{w} \cdot \left(h_{\text{Q5}} - h_{f}\right) \cdot \left(\frac{h_{\text{Q5}} + h_{f}}{2} - z_{S}\right)^{2}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $b_{\text{Q5}}$ | Flanschbreite, Plattenbalken | mm | Vorgabe |
| $h_{f}$ | Flanschdicke, Plattenbalken | mm | Vorgabe |
| $z_{S}$ | Abstand des Schwerpunkts vom oberen Rand, Plattenbalken | mm | [[Schwerpunkt eines T-Querschnitts]] |
| $b_{w}$ | Stegbreite, Plattenbalken | mm | Vorgabe |
| $h_{\text{Q5}}$ | Höhe, Plattenbalken | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  I_{\text{Q5}} &= \frac{b_{\text{Q5}} \cdot \left(h_{f,\text{Q5}}\right)^{3}}{12} + b_{\text{Q5}} \cdot h_{f,\text{Q5}} \cdot \left(z_{S,\text{Q5}} - \frac{h_{f,\text{Q5}}}{2}\right)^{2} + \frac{b_{w,\text{Q5}} \cdot \left(h_{\text{Q5}} - h_{f,\text{Q5}}\right)^{3}}{12} + b_{w,\text{Q5}} \cdot \left(h_{\text{Q5}} - h_{f,\text{Q5}}\right) \cdot \left(\frac{h_{\text{Q5}} + h_{f,\text{Q5}}}{2} - z_{S,\text{Q5}}\right)^{2} \\
  &= \frac{1200\,\mathrm{mm} \cdot \left(200\,\mathrm{mm}\right)^{3}}{12} + 1200\,\mathrm{mm} \cdot 200\,\mathrm{mm} \cdot \left(200\,\mathrm{mm} - \frac{200\,\mathrm{mm}}{2}\right)^{2} + \frac{300\,\mathrm{mm} \cdot \left(600\,\mathrm{mm} - 200\,\mathrm{mm}\right)^{3}}{12} + 300\,\mathrm{mm} \cdot \left(600\,\mathrm{mm} - 200\,\mathrm{mm}\right) \cdot \left(\frac{600\,\mathrm{mm} + 200\,\mathrm{mm}}{2} - 200\,\mathrm{mm}\right)^{2} \\
  &= 9600\,\cdot 10^{6}\,\mathrm{mm}^{4}
\end{aligned}
$$

## Im Code

- [[opencivil.stabwerk.querschnitte]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Je Teil -- Flansch und Steg -- das eigene Trägheitsmoment $b h^3 / 12$ und
dazu $A_i \cdot a_i^2$, mit $a_i$ dem Abstand seines Schwerpunkts vom
[[Schwerpunkt eines T-Querschnitts|Schwerpunkt des ganzen Querschnitts]]: der
Satz von Steiner. Der zweite Anteil ist beim Flansch meist der grössere.
