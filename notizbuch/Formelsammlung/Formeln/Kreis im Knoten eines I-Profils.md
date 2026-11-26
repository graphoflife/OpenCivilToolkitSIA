---
erzeugt: 0c048fbd4df4
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Durchmesser des Kreises im Knoten von Steg und Flansch, «Stütze» (HEB 300)»*

$$
d_{K} = \frac{\left(r_{\text{Q2}} + \frac{t_{w}}{2}\right)^{2} + \left(r_{\text{Q2}} + t_{f}\right)^{2} - \left(r_{\text{Q2}}\right)^{2}}{t_{f} + 2 \cdot r_{\text{Q2}}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $r_{\text{Q2}}$ | Ausrundung, Stütze | mm | Vorgabe |
| $t_{w}$ | Stegdicke, Stütze | mm | Vorgabe |
| $t_{f}$ | Flanschdicke, Stütze | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  d_{K,\text{Q2}} &= \frac{\left(r_{\text{Q2}} + \frac{t_{w,\text{Q2}}}{2}\right)^{2} + \left(r_{\text{Q2}} + t_{f,\text{Q2}}\right)^{2} - \left(r_{\text{Q2}}\right)^{2}}{t_{f,\text{Q2}} + 2 \cdot r_{\text{Q2}}} \\
  &= \frac{\left(27\,\mathrm{mm} + \frac{11\,\mathrm{mm}}{2}\right)^{2} + \left(27\,\mathrm{mm} + 19\,\mathrm{mm}\right)^{2} - \left(27\,\mathrm{mm}\right)^{2}}{19\,\mathrm{mm} + 2 \cdot 27\,\mathrm{mm}} \\
  &= 33.47\,\mathrm{mm}
\end{aligned}
$$

## Gebraucht von

- [[Torsionsträgheitsmoment eines I-Profils]]

## Im Code

- [[opencivil.stahlprofile.formen]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wo Steg und Flansch zusammenstossen, ist das Profil dicker als jede Wand für
sich. Der grösste Kreis, der dort hineinpasst, liegt auf der Mitte des
Stegs; er berührt die Aussenseite des Flanschs und beide Ausrundungen. Sein
Mittelpunkt liegt $d_K/2$ unter der Aussenseite, die Mittelpunkte der
Ausrundungen liegen $t_w/2 + r$ daneben und $t_f + r$ darunter. Berühren
heisst: ihr Abstand ist $d_K/2 + r$,

$$
\left(\frac{t_w}{2} + r\right)^2 + \left(t_f + r - \frac{d_K}{2}\right)^2
= \left(\frac{d_K}{2} + r\right)^2 ,
$$

und nach $d_K$ aufgelöst steht oben die Formel. Er geht in der vierten
Potenz ins [[Torsionsträgheitsmoment eines I-Profils]] ein. Die Formel ist
die der Tabelle des Benutzers, nach Vorgabe, nicht nachgeschlagen.
