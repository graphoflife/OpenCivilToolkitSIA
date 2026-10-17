---
erzeugt: 0ff5e3632e1d
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.2.2.4"
---
> [!info] Normstelle
> SIA 262:2025, 4.2.2.4

*In der Herleitung: «Werkstoffgesetz B500B, Bemessungswerte: Stahl, bilinear»*

$$
\sigma_s(\varepsilon_s) = \begin{cases} \min(E_s\,\varepsilon_s;\ f_{yd}) & 0 \le \varepsilon_s \le \varepsilon_{ud} \\[1ex] \max(E_s\,\varepsilon_s;\ -f_{yd}^{-}) & -\varepsilon_{ud} \le \varepsilon_s < 0 \\[1ex] 0 & |\varepsilon_s| > \varepsilon_{ud} \quad (\text{jenseits der Bruchdehnung}) \end{cases}
$$

*In der Herleitung: «Werkstoffgesetze im Gebrauchszustand: Stahl, bilinear»*

$$
\sigma_s(\varepsilon_s) = \begin{cases} \min(E_s\,\varepsilon_s;\ f_{yk}) & 0 \le \varepsilon_s \le \varepsilon_{ud} \\[1ex] \max(E_s\,\varepsilon_s;\ -f_{yk}^{-}) & -\varepsilon_{ud} \le \varepsilon_s < 0 \\[1ex] 0 & |\varepsilon_s| > \varepsilon_{ud} \quad (\text{jenseits der Bruchdehnung}) \end{cases}
$$

## Im Code

- [[opencivil.querschnitt.werkstoffgesetz#Gesetz.protokoll|Gesetz.protokoll]]

## Themen

- [[Schiefe Biegung]]
- [[Stahlspannung aus Rissbreite]]
- [[Stahlspannung gegen Fliessen]]
- [[Knicken]]
- [[Biegung und Normalkraft]]
- [[Zwängung auf Biegung]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Elastisch mit $E_s$ bis zur Fliessgrenze, dann ein waagrechtes Plateau --
auf Zug bei $f_{yd}$, auf Druck bei $f_{yd}^-$. Die Verfestigung nach dem
Fliessen wird nicht angesetzt; das liegt auf der sicheren Seite. Begrenzt
ist die Dehnung durch $\varepsilon_{ud}$: dort endet die Linie aus
Dehnungsebenen auf der Zugseite.

Mit charakteristischen Werten stehen $f_{yk}$ und $f_{yk}^-$ an ihrer Stelle.

Jenseits von $\varepsilon_{ud}$ trägt der Stahl nichts mehr. Auf der Grenze
selbst gilt das Plateau, auch um eine Rundung darüber: die Linie aus
Dehnungsebenen legt die gezogene Lage genau auf $\varepsilon_{ud}$, und dort
darf sie nicht an der letzten Stelle auf null kippen.
