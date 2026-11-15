---
erzeugt: b66059a823cf
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Torsionsträgheitsmoment, «Stütze» (HEB 300)»*

$$
I_{T} = \frac{2}{3} \cdot b_{\text{Q2}} \cdot \left(t_{f}\right)^{3} \cdot \left(1 - 0.63 \cdot \frac{t_{f}}{b_{\text{Q2}}}\right) + \frac{1}{3} \cdot \left(h_{\text{Q2}} - 2 \cdot t_{f}\right) \cdot \left(t_{w}\right)^{3} + 2 \cdot \left(0.145 + 0.1 \cdot \frac{r_{\text{Q2}}}{t_{f}}\right) \cdot \frac{t_{w}}{t_{f}} \cdot \left(d_{K}\right)^{4}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $b_{\text{Q2}}$ | Breite, Stütze | mm | Vorgabe |
| $t_{f}$ | Flanschdicke, Stütze | mm | Vorgabe |
| $h_{\text{Q2}}$ | Höhe, Stütze | mm | Vorgabe |
| $t_{w}$ | Stegdicke, Stütze | mm | Vorgabe |
| $r_{\text{Q2}}$ | Ausrundung, Stütze | mm | Vorgabe |
| $d_{K}$ | Durchmesser des Kreises im Knoten von Steg und Flansch, Stütze | mm | [[Kreis im Knoten eines I-Profils]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  I_{T,\text{Q2}} &= \frac{2}{3} \cdot b_{\text{Q2}} \cdot \left(t_{f,\text{Q2}}\right)^{3} \cdot \left(1 - 0.63 \cdot \frac{t_{f,\text{Q2}}}{b_{\text{Q2}}}\right) + \frac{1}{3} \cdot \left(h_{\text{Q2}} - 2 \cdot t_{f,\text{Q2}}\right) \cdot \left(t_{w,\text{Q2}}\right)^{3} + 2 \cdot \left(0.145 + 0.1 \cdot \frac{r_{\text{Q2}}}{t_{f,\text{Q2}}}\right) \cdot \frac{t_{w,\text{Q2}}}{t_{f,\text{Q2}}} \cdot \left(d_{K,\text{Q2}}\right)^{4} \\
  &= \frac{2}{3} \cdot 300\,\mathrm{mm} \cdot \left(19\,\mathrm{mm}\right)^{3} \cdot \left(1 - 0.63 \cdot \frac{19\,\mathrm{mm}}{300\,\mathrm{mm}}\right) + \frac{1}{3} \cdot \left(300\,\mathrm{mm} - 2 \cdot 19\,\mathrm{mm}\right) \cdot \left(11\,\mathrm{mm}\right)^{3} + 2 \cdot \left(0.145 + 0.1 \cdot \frac{27\,\mathrm{mm}}{19\,\mathrm{mm}}\right) \cdot \frac{11\,\mathrm{mm}}{19\,\mathrm{mm}} \cdot \left(33.47\,\mathrm{mm}\right)^{4} \\
  &= 185.05\,\mathrm{cm}^{4}
\end{aligned}
$$

## Gebraucht von

- [[Torsionssteifigkeit]]

## Im Code

- [[opencivil.stabwerk.profilformen]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ein offenes, dünnwandiges Profil trägt Torsion nach St. Venant schwach: jede
Wand etwa mit $\frac{1}{3}\,s\,t^3$, Länge mal Dicke hoch drei. Die Formel hat
drei Glieder: die beiden Flansche, je mit einer Minderung für ihre freien
Enden ($1 - 0.63\,t_f/b$); der Steg zwischen den Flanschen; und die beiden
Knoten von Steg und Flansch. Dort ist das Profil dicker als jede Wand, und
der [[Kreis im Knoten eines I-Profils]] geht in der vierten Potenz ein, mit
einem Beiwert aus $r/t_f$ und $t_w/t_f$.

Wie wenig das ist: ein IPE 300 hat $I_T = 20.1\,\mathrm{cm}^4$, gut
vierhundertmal weniger als sein $I_y$. Die Formel und ihre Beiwerte sind die
der Tabelle des Benutzers, nach Vorgabe, nicht nachgeschlagen. Die
Wölbkrafttorsion, die ein I-Profil mit gehaltenen Enden deutlich steifer
macht, rechnet das Werkzeug nicht ([[TODO]]).
