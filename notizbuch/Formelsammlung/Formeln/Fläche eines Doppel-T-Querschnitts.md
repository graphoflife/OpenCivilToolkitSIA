---
erzeugt: 9a0437282bae
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Querschnittsfläche, «Walzprofil» (Doppel-T)»*

$$
A_{\text{Q6}} = 2 \cdot b_{\text{Q6}} \cdot t_{f} + t_{w} \cdot \left(h_{\text{Q6}} - 2 \cdot t_{f}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $b_{\text{Q6}}$ | Flanschbreite, Walzprofil | mm | Vorgabe |
| $t_{f}$ | Flanschdicke, Walzprofil | mm | Vorgabe |
| $t_{w}$ | Stegdicke, Walzprofil | mm | Vorgabe |
| $h_{\text{Q6}}$ | Höhe, Walzprofil | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  A_{\text{Q6}} &= 2 \cdot b_{\text{Q6}} \cdot t_{f,\text{Q6}} + t_{w,\text{Q6}} \cdot \left(h_{\text{Q6}} - 2 \cdot t_{f,\text{Q6}}\right) \\
  &= 2 \cdot 300\,\mathrm{mm} \cdot 19\,\mathrm{mm} + 11\,\mathrm{mm} \cdot \left(300\,\mathrm{mm} - 2 \cdot 19\,\mathrm{mm}\right) \\
  &= 14282\,\mathrm{mm}^{2}
\end{aligned}
$$

## Im Code

- [[opencivil.stabwerk.querschnitte]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Zwei Flansche $b \times t_f$ und der Steg zwischen ihnen,
$t_w \times (h - 2 t_f)$. Ohne die Ausrundungen zwischen Steg und Flansch,
die ein Walzprofil hat -- dessen Tabellenwert ist darum etwas grösser.
