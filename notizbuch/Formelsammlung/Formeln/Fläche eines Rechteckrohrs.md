---
erzeugt: 20b649fb85b4
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Querschnittsfläche, «Hohlprofil» (Rechteckrohr)»*

$$
A_{\text{Q4}} = b_{\text{Q4}} \cdot h_{\text{Q4}} - \left(b_{\text{Q4}} - 2 \cdot t_{\text{Q4}}\right) \cdot \left(h_{\text{Q4}} - 2 \cdot t_{\text{Q4}}\right)
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
  A_{\text{Q4}} &= b_{\text{Q4}} \cdot h_{\text{Q4}} - \left(b_{\text{Q4}} - 2 \cdot t_{\text{Q4}}\right) \cdot \left(h_{\text{Q4}} - 2 \cdot t_{\text{Q4}}\right) \\
  &= 200\,\mathrm{mm} \cdot 300\,\mathrm{mm} - \left(200\,\mathrm{mm} - 2 \cdot 12.5\,\mathrm{mm}\right) \cdot \left(300\,\mathrm{mm} - 2 \cdot 12.5\,\mathrm{mm}\right) \\
  &= 11875\,\mathrm{mm}^{2}
\end{aligned}
$$

## Im Code

- [[opencivil.stabwerk.querschnitte]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das äussere Rechteck $b \times h$ minus das innere $(b - 2t) \times (h - 2t)$:
ein Hohlprofil mit derselben Wanddicke ringsum. Die Ausrundungen an den Ecken
eines gewalzten Profils fehlen -- sein Tabellenwert liegt darum etwas
daneben.
