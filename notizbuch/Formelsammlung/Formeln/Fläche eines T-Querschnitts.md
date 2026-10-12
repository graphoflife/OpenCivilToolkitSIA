---
erzeugt: 45ef739bc6ed
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Querschnittsfläche, «Plattenbalken» (T-Querschnitt)»*

$$
A_{\text{Q5}} = b_{\text{Q5}} \cdot h_{f} + b_{w} \cdot \left(h_{\text{Q5}} - h_{f}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $b_{\text{Q5}}$ | Flanschbreite, Plattenbalken | mm | Vorgabe |
| $h_{f}$ | Flanschdicke, Plattenbalken | mm | Vorgabe |
| $b_{w}$ | Stegbreite, Plattenbalken | mm | Vorgabe |
| $h_{\text{Q5}}$ | Höhe, Plattenbalken | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  A_{\text{Q5}} &= b_{\text{Q5}} \cdot h_{f,\text{Q5}} + b_{w,\text{Q5}} \cdot \left(h_{\text{Q5}} - h_{f,\text{Q5}}\right) \\
  &= 1200\,\mathrm{mm} \cdot 200\,\mathrm{mm} + 300\,\mathrm{mm} \cdot \left(600\,\mathrm{mm} - 200\,\mathrm{mm}\right) \\
  &= 360000\,\mathrm{mm}^{2}
\end{aligned}
$$

## Gebraucht von

- [[Schwerpunkt eines T-Querschnitts]]

## Im Code

- [[opencivil.stabwerk.querschnitte]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Flansch $b \times h_f$ oben und der Steg $b_w \times (h - h_f)$ darunter.
So lässt sich ein Plattenbalken rechnen: die Breite der Platte, die mitträgt,
wird als Flanschbreite $b$ eingesetzt.
