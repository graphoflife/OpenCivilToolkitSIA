---
erzeugt: 58c30a9092cd
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Flächenträgheitsmoment, «Hohlprofil» (Rechteckrohr)»*

$$
I_{\text{Q4}} = \frac{b_{\text{Q4}} \cdot \left(h_{\text{Q4}}\right)^{3} - \left(b_{\text{Q4}} - 2 \cdot t_{\text{Q4}}\right) \cdot \left(h_{\text{Q4}} - 2 \cdot t_{\text{Q4}}\right)^{3}}{12}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $b_{\text{Q4}}$ | Breite, Hohlprofil | mm | Vorgabe |
| $h_{\text{Q4}}$ | Höhe, Hohlprofil | mm | Vorgabe |
| $t_{\text{Q4}}$ | Wanddicke, Hohlprofil | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  I_{\text{Q4}} &= \frac{b_{\text{Q4}} \cdot \left(h_{\text{Q4}}\right)^{3} - \left(b_{\text{Q4}} - 2 \cdot t_{\text{Q4}}\right) \cdot \left(h_{\text{Q4}} - 2 \cdot t_{\text{Q4}}\right)^{3}}{12} \\
  &= \frac{200\,\mathrm{mm} \cdot \left(300\,\mathrm{mm}\right)^{3} - \left(200\,\mathrm{mm} - 2 \cdot 12.5\,\mathrm{mm}\right) \cdot \left(300\,\mathrm{mm} - 2 \cdot 12.5\,\mathrm{mm}\right)^{3}}{12} \\
  &= 146.71\,\cdot 10^{6}\,\mathrm{mm}^{4}
\end{aligned}
$$

## Im Code

- [[opencivil.stabwerk.querschnitte]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Aussen minus innen, je mit der Formel des Rechtecks: beide Rechtecke haben
dieselbe Schwerachse, also lassen sich ihre Trägheitsmomente einfach
abziehen. Ohne die Ausrundungen der Ecken, wie bei der
[[Fläche eines Rechteckrohrs|Fläche]].
