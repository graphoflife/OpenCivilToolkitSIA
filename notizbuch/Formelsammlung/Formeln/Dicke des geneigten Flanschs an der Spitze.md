---
erzeugt: b342d144b7c0
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Flanschdicke an der Spitze, «UNP 200 um y» (UNP 200, um y, die starke Achse)»*

$$
t_{2} = t_{f} - p_{\text{Q16}} \cdot \left(b_{\text{Q16}} - c_{\text{Q16}}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $t_{f}$ | Flanschdicke, UNP 200 um y | mm | Vorgabe |
| $p_{\text{Q16}}$ | Neigung der Flansche, UNP 200 um y | % | Vorgabe |
| $b_{\text{Q16}}$ | Breite, UNP 200 um y | mm | Vorgabe |
| $c_{\text{Q16}}$ | Abstand der Stelle von t\_f vom Rücken, UNP 200 um y | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  t_{2,\text{Q16}} &= t_{f,\text{Q16}} - p_{\text{Q16}} \cdot \left(b_{\text{Q16}} - c_{\text{Q16}}\right) \\
  &= 11.5\,\mathrm{mm} - 8\,\% \cdot \left(75\,\mathrm{mm} - 37.5\,\mathrm{mm}\right) \\
  &= 8.5\,\mathrm{mm}
\end{aligned}
$$

## Gebraucht von

- [[Fläche eines U-Profils mit geneigten Flanschen]]
- [[Flächenträgheitsmoment eines U-Profils mit geneigten Flanschen um y]]
- [[Flächenträgheitsmoment eines U-Profils mit geneigten Flanschen um z]]
- [[Schwerpunkt eines U-Profils mit geneigten Flanschen]]

## Im Code

- [[opencivil.stabwerk.profilformen]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Dieselbe geneigte Innenseite wie bei der
[[Dicke des geneigten Flanschs am Steg]], hier an der Spitze, bei $x = b$.
Mit $t_1$ und $t_2$ ist der Flansch ein Trapez; daraus rechnen Fläche,
Schwerpunkt und Trägheitsmomente des UNP.
