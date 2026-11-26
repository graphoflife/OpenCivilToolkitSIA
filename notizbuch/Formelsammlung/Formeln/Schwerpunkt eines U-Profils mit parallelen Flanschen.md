---
erzeugt: 7e31c2f17ec6
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Abstand des Schwerpunkts vom Rücken, «UPE 200 um z» (UPE 200, um z, die schwache Achse)»*

$$
e_{y} = \frac{h_{\text{Q15}} \cdot \left(t_{w}\right)^{2} / 2 + 2 \cdot \left(b_{\text{Q15}} - t_{w}\right) \cdot t_{f} \cdot \frac{b_{\text{Q15}} + t_{w}}{2} + 2 \cdot 0.2146 \cdot \left(r_{\text{Q15}}\right)^{2} \cdot \left(t_{w} + 0.2234 \cdot r_{\text{Q15}}\right)}{A_{\text{Q15}}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $h_{\text{Q15}}$ | Höhe, UPE 200 um z | mm | Vorgabe |
| $t_{w}$ | Stegdicke, UPE 200 um z | mm | Vorgabe |
| $b_{\text{Q15}}$ | Breite, UPE 200 um z | mm | Vorgabe |
| $t_{f}$ | Flanschdicke, UPE 200 um z | mm | Vorgabe |
| $r_{\text{Q15}}$ | Ausrundung, UPE 200 um z | mm | Vorgabe |
| $A_{\text{Q15}}$ | Querschnittsfläche, UPE 200 um z | cm² | [[Fläche eines U-Profils mit parallelen Flanschen]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  e_{y,\text{Q15}} &= \frac{h_{\text{Q15}} \cdot \left(t_{w,\text{Q15}}\right)^{2} / 2 + 2 \cdot \left(b_{\text{Q15}} - t_{w,\text{Q15}}\right) \cdot t_{f,\text{Q15}} \cdot \frac{b_{\text{Q15}} + t_{w,\text{Q15}}}{2} + 2 \cdot 0.2146 \cdot \left(r_{\text{Q15}}\right)^{2} \cdot \left(t_{w,\text{Q15}} + 0.2234 \cdot r_{\text{Q15}}\right)}{A_{\text{Q15}}} \\
  &= \frac{200\,\mathrm{mm} \cdot \left(6\,\mathrm{mm}\right)^{2} / 2 + 2 \cdot \left(80\,\mathrm{mm} - 6\,\mathrm{mm}\right) \cdot 11\,\mathrm{mm} \cdot \frac{80\,\mathrm{mm} + 6\,\mathrm{mm}}{2} + 2 \cdot 0.2146 \cdot \left(13\,\mathrm{mm}\right)^{2} \cdot \left(6\,\mathrm{mm} + 0.2234 \cdot 13\,\mathrm{mm}\right)}{29.01\,\mathrm{cm}^{2}} \\
  &= 25.6\,\mathrm{mm}
\end{aligned}
$$

## Gebraucht von

- [[Flächenträgheitsmoment eines U-Profils mit parallelen Flanschen um z]]

## Im Code

- [[opencivil.stahlprofile.formen]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie weit der Schwerpunkt vom Rücken liegt: die statischen Momente der Teile
um den Rücken, geteilt durch die Fläche. Der Steg $h\,t_w$ liegt im
Abstand $t_w/2$, die Flansche $(b - t_w)\,t_f$ im Abstand $(b + t_w)/2$,
die Zwickel im Abstand $t_w + 0.2234\,r$. Der Schwerpunkt liegt nahe am
Steg; um ihn biegt sich das Profil um $z$.
