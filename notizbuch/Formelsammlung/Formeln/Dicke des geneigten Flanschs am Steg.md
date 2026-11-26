---
erzeugt: f209c3522c2a
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Flanschdicke am Steg, «UNP 200 um y» (UNP 200, um y, die starke Achse)»*

$$
t_{1} = t_{f} + p_{\text{Q16}} \cdot \left(c_{\text{Q16}} - t_{w}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $t_{f}$ | Flanschdicke, UNP 200 um y | mm | Vorgabe |
| $p_{\text{Q16}}$ | Neigung der Flansche, UNP 200 um y | % | Vorgabe |
| $c_{\text{Q16}}$ | Abstand der Stelle von t\_f vom Rücken, UNP 200 um y | mm | Vorgabe |
| $t_{w}$ | Stegdicke, UNP 200 um y | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  t_{1,\text{Q16}} &= t_{f,\text{Q16}} + p_{\text{Q16}} \cdot \left(c_{\text{Q16}} - t_{w,\text{Q16}}\right) \\
  &= 11.5\,\mathrm{mm} + 8\,\% \cdot \left(37.5\,\mathrm{mm} - 8.5\,\mathrm{mm}\right) \\
  &= 13.82\,\mathrm{mm}
\end{aligned}
$$

## Gebraucht von

- [[Fläche eines U-Profils mit geneigten Flanschen]]
- [[Flächenträgheitsmoment eines U-Profils mit geneigten Flanschen um y]]
- [[Flächenträgheitsmoment eines U-Profils mit geneigten Flanschen um z]]
- [[Schwerpunkt eines U-Profils mit geneigten Flanschen]]

## Im Code

- [[opencivil.stahlprofile.formen]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Beim UNP ist die Innenseite der Flansche geneigt: ein Flansch ist am Steg
dicker als an der Spitze. Die Tabelle nennt eine Dicke $t_f$, die im
Abstand $c$ vom Rücken gilt. Mit der Neigung $p$ ist die Dicke an jeder
Stelle $x$ gleich $t(x) = t_f + p\,(c - x)$; am Steg, bei $x = t_w$, ist sie
$t_1$.

Nach Vorgabe, nicht nachgeschlagen: bis $h = 300$ mm ist $p = 8\,\%$ und
$c = b/2$, darüber $p = 5\,\%$ und $c = (b + t_w)/2$, die Mitte des
Flanschs. Damit treffen Fläche und Trägheitsmomente die Werte der Tabelle
des Benutzers, die beim UNP keine Formeln hat.
