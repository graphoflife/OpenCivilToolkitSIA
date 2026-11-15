---
erzeugt: 4fee7881dc15
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Querschnittsfläche, «Träger» (HEB 300, um y, die starke Achse)»*

$$
A_{\text{Q11}} = 2 \cdot b_{\text{Q11}} \cdot t_{f} + \left(h_{\text{Q11}} - 2 \cdot t_{f}\right) \cdot t_{w} + 4 \cdot 0.2146 \cdot \left(r_{\text{Q11}}\right)^{2}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $b_{\text{Q11}}$ | Breite, Träger | mm | Vorgabe |
| $t_{f}$ | Flanschdicke, Träger | mm | Vorgabe |
| $h_{\text{Q11}}$ | Höhe, Träger | mm | Vorgabe |
| $t_{w}$ | Stegdicke, Träger | mm | Vorgabe |
| $r_{\text{Q11}}$ | Ausrundung, Träger | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  A_{\text{Q11}} &= 2 \cdot b_{\text{Q11}} \cdot t_{f,\text{Q11}} + \left(h_{\text{Q11}} - 2 \cdot t_{f,\text{Q11}}\right) \cdot t_{w,\text{Q11}} + 4 \cdot 0.2146 \cdot \left(r_{\text{Q11}}\right)^{2} \\
  &= 2 \cdot 300\,\mathrm{mm} \cdot 19\,\mathrm{mm} + \left(300\,\mathrm{mm} - 2 \cdot 19\,\mathrm{mm}\right) \cdot 11\,\mathrm{mm} + 4 \cdot 0.2146 \cdot \left(27\,\mathrm{mm}\right)^{2} \\
  &= 149.08\,\mathrm{cm}^{2}
\end{aligned}
$$

## Im Code

- [[opencivil.stabwerk.profilformen]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Zwei Flansche $b \times t_f$, dazwischen der Steg $(h - 2t_f) \times t_w$,
und in den vier Ecken zwischen Steg und Flansch je eine Ausrundung mit
Radius $r$. Was eine Ausrundung an Fläche bringt, ist ein Zwickel: das
Quadrat $r \times r$ ohne den Viertelkreis, $(1 - \pi/4)\,r^2 \approx
0.2146\,r^2$.

Die Formel ist die der Tabelle des Benutzers, mit demselben gerundeten
Beiwert -- nach Vorgabe, nicht nachgeschlagen. Sie gilt für IPE, HEA, HEB
und HEM. Mit der Dichte des Materials gibt die Fläche das Eigengewicht des
Stabs.
