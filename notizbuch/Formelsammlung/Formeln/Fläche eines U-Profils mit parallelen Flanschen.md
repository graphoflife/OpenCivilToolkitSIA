---
erzeugt: 924c9679f3d5
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Querschnittsfläche, «UPE 200 um y» (UPE 200, um y, die starke Achse)»*

$$
A_{\text{Q14}} = h_{\text{Q14}} \cdot t_{w} + 2 \cdot \left(b_{\text{Q14}} - t_{w}\right) \cdot t_{f} + 2 \cdot 0.2146 \cdot \left(r_{\text{Q14}}\right)^{2}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $h_{\text{Q14}}$ | Höhe, UPE 200 um y | mm | Vorgabe |
| $t_{w}$ | Stegdicke, UPE 200 um y | mm | Vorgabe |
| $b_{\text{Q14}}$ | Breite, UPE 200 um y | mm | Vorgabe |
| $t_{f}$ | Flanschdicke, UPE 200 um y | mm | Vorgabe |
| $r_{\text{Q14}}$ | Ausrundung, UPE 200 um y | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  A_{\text{Q14}} &= h_{\text{Q14}} \cdot t_{w,\text{Q14}} + 2 \cdot \left(b_{\text{Q14}} - t_{w,\text{Q14}}\right) \cdot t_{f,\text{Q14}} + 2 \cdot 0.2146 \cdot \left(r_{\text{Q14}}\right)^{2} \\
  &= 200\,\mathrm{mm} \cdot 6\,\mathrm{mm} + 2 \cdot \left(80\,\mathrm{mm} - 6\,\mathrm{mm}\right) \cdot 11\,\mathrm{mm} + 2 \cdot 0.2146 \cdot \left(13\,\mathrm{mm}\right)^{2} \\
  &= 29.01\,\mathrm{cm}^{2}
\end{aligned}
$$

## Gebraucht von

- [[Schwerpunkt eines U-Profils mit parallelen Flanschen]]

## Im Code

- [[opencivil.stahlprofile.formen]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Steg über die ganze Höhe, $h \times t_w$, daneben zwei Flansche
$(b - t_w) \times t_f$ und in den beiden inneren Ecken je eine Ausrundung
mit Radius $r$, ein Zwickel mit $0.2146\,r^2$. Die Formel des UPE aus der
Tabelle des Benutzers – nach Vorgabe, nicht nachgeschlagen.
