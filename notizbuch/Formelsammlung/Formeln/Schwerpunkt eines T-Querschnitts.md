---
erzeugt: 6b45f34dba90
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Abstand des Schwerpunkts vom oberen Rand, «Plattenbalken» (T-Querschnitt)»*

$$
z_{S} = \frac{b_{\text{Q5}} \cdot \left(h_{f}\right)^{2} / 2 + b_{w} \cdot \left(h_{\text{Q5}} - h_{f}\right) \cdot \left(h_{\text{Q5}} + h_{f}\right) / 2}{A_{\text{Q5}}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $b_{\text{Q5}}$ | Flanschbreite, Plattenbalken | mm | Vorgabe |
| $h_{f}$ | Flanschdicke, Plattenbalken | mm | Vorgabe |
| $b_{w}$ | Stegbreite, Plattenbalken | mm | Vorgabe |
| $h_{\text{Q5}}$ | Höhe, Plattenbalken | mm | Vorgabe |
| $A_{\text{Q5}}$ | Querschnittsfläche, Plattenbalken | mm² | [[Fläche eines T-Querschnitts]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  z_{S,\text{Q5}} &= \frac{b_{\text{Q5}} \cdot \left(h_{f,\text{Q5}}\right)^{2} / 2 + b_{w,\text{Q5}} \cdot \left(h_{\text{Q5}} - h_{f,\text{Q5}}\right) \cdot \left(h_{\text{Q5}} + h_{f,\text{Q5}}\right) / 2}{A_{\text{Q5}}} \\
  &= \frac{1200\,\mathrm{mm} \cdot \left(200\,\mathrm{mm}\right)^{2} / 2 + 300\,\mathrm{mm} \cdot \left(600\,\mathrm{mm} - 200\,\mathrm{mm}\right) \cdot \left(600\,\mathrm{mm} + 200\,\mathrm{mm}\right) / 2}{360000\,\mathrm{mm}^{2}} \\
  &= 200\,\mathrm{mm}
\end{aligned}
$$

## Gebraucht von

- [[Flächenträgheitsmoment eines T-Querschnitts]]

## Im Code

- [[opencivil.stabwerk.querschnitte]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Beim T liegt der Schwerpunkt nicht auf halber Höhe: der breite Flansch zieht
ihn nach oben. Gerechnet wird er als Summe der statischen Momente von Flansch
und Steg um den oberen Rand, geteilt durch die ganze Fläche,
$z_S = \sum A_i z_i / A$. Um diesen Punkt biegt sich der Querschnitt.
