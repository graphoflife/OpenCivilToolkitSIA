---
erzeugt: 44d9a6233a5a
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Querschnittsfläche, «Fundamentbalken» (Trapez)»*

$$
A_{\text{Q7}} = \frac{\left(b_{o} + b_{u}\right) \cdot h_{\text{Q7}}}{2}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $b_{o}$ | Breite oben, Fundamentbalken | mm | Vorgabe |
| $b_{u}$ | Breite unten, Fundamentbalken | mm | Vorgabe |
| $h_{\text{Q7}}$ | Höhe, Fundamentbalken | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
A_{\text{Q7}} = \frac{\left(b_{o,\text{Q7}} + b_{u,\text{Q7}}\right) \cdot h_{\text{Q7}}}{2} = \frac{\left(600\,\mathrm{mm} + 400\,\mathrm{mm}\right) \cdot 500\,\mathrm{mm}}{2} = 250000\,\mathrm{mm}^{2}
$$

## Im Code

- [[opencivil.stabwerk.querschnitte]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die mittlere Breite mal die Höhe -- etwa ein Fundamentbalken mit schrägen
Seiten.
