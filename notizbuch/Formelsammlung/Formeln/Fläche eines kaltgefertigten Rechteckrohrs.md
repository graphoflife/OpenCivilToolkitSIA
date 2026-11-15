---
erzeugt: 810e276f474c
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Querschnittsfläche, «RRK 200 x 100 x 8 um y» (RRK 200 x 100 x 8, um y, die starke Achse)»*

$$
A_{\text{Q18}} = 2 \cdot t_{\text{Q18}} \cdot \left(h_{\text{Q18}} + b_{\text{Q18}} - 2 \cdot t_{\text{Q18}}\right) - 4 \cdot 0.2146 \cdot \left(\left(r_{o}\right)^{2} - \left(r_{i}\right)^{2}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $t_{\text{Q18}}$ | Wanddicke, RRK 200 x 100 x 8 um y | mm | Vorgabe |
| $h_{\text{Q18}}$ | Höhe, RRK 200 x 100 x 8 um y | mm | Vorgabe |
| $b_{\text{Q18}}$ | Breite, RRK 200 x 100 x 8 um y | mm | Vorgabe |
| $r_{o}$ | Radius aussen, RRK 200 x 100 x 8 um y | mm | Vorgabe |
| $r_{i}$ | Radius innen, RRK 200 x 100 x 8 um y | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  A_{\text{Q18}} &= 2 \cdot t_{\text{Q18}} \cdot \left(h_{\text{Q18}} + b_{\text{Q18}} - 2 \cdot t_{\text{Q18}}\right) - 4 \cdot 0.2146 \cdot \left(\left(r_{o,\text{Q18}}\right)^{2} - \left(r_{i,\text{Q18}}\right)^{2}\right) \\
  &= 2 \cdot 8\,\mathrm{mm} \cdot \left(200\,\mathrm{mm} + 100\,\mathrm{mm} - 2 \cdot 8\,\mathrm{mm}\right) - 4 \cdot 0.2146 \cdot \left(\left(20\,\mathrm{mm}\right)^{2} - \left(12\,\mathrm{mm}\right)^{2}\right) \\
  &= 43.24\,\mathrm{cm}^{2}
\end{aligned}
$$

## Im Code

- [[opencivil.stabwerk.profilformen]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Vier Wände der Dicke $t$, zusammen $2t\,(h + b - 2t)$ -- so gezählt, dass
keine Ecke doppelt steht. Die Ecken sind rund, aussen mit $r_o$ und innen
mit $r_i$: aussen fehlt je ein Zwickel mit $0.2146\,r_o^2$, innen kommt je
einer mit $0.2146\,r_i^2$ hinzu, denn das Loch ist an seinen Ecken kleiner.

Die Radien kommen aus der Wanddicke, wie in der Tabelle des Benutzers: bis
$t = 6$ mm ist $r_o = 2t$ und $r_i = t$, bis 10 mm $2.5\,t$ und $1.5\,t$,
darüber $3t$ und $2t$. Nach Vorgabe, nicht nachgeschlagen.
