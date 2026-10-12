---
erzeugt: acb93a47ae01
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Querschnittsfläche, «Rohr» (Kreisring)»*

$$
A_{\text{Q3}} = \frac{\pi \cdot \left(\left(D_{\text{Q3}}\right)^{2} - \left(D_{\text{Q3}} - 2 \cdot t_{\text{Q3}}\right)^{2}\right)}{4}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $D_{\text{Q3}}$ | Aussendurchmesser, Rohr | mm | Vorgabe |
| $t_{\text{Q3}}$ | Wanddicke, Rohr | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  A_{\text{Q3}} &= \frac{\pi \cdot \left(\left(D_{\text{Q3}}\right)^{2} - \left(D_{\text{Q3}} - 2 \cdot t_{\text{Q3}}\right)^{2}\right)}{4} \\
  &= \frac{\pi \cdot \left(\left(168.3\,\mathrm{mm}\right)^{2} - \left(168.3\,\mathrm{mm} - 2 \cdot 10\,\mathrm{mm}\right)^{2}\right)}{4} \\
  &= 4973\,\mathrm{mm}^{2}
\end{aligned}
$$

## Im Code

- [[opencivil.stabwerk.querschnitte]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Aussenkreis minus Innenkreis; innen bleibt der Durchmesser $D - 2t$. So ein
Rohr mit der Wanddicke $t$.
