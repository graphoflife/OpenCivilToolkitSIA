---
erzeugt: b67e8cdf19c8
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.2.2.4"
---
> [!info] Normstelle
> SIA 262:2025, 4.2.2.4

*In der Herleitung: «B500B: bilineare Beziehung, Bemessungswerte»*

$$
\sigma_s(\varepsilon_s) = \begin{cases} \min(E_s\,\varepsilon_s;\ f_{yd}) & \varepsilon_s \ge 0 \\[1ex] \max(E_s\,\varepsilon_s;\ -f_{yd}^{-}) & \varepsilon_s < 0 \end{cases} \qquad |\varepsilon_s| \le \varepsilon_{ud}
$$

*In der Herleitung: «Werkstoffgesetze: Stahl, bilinear»*

$$
\sigma_s(\varepsilon_s) = \begin{cases} \min(E_s\,\varepsilon_s;\ f_{yk}) & \varepsilon_s \ge 0 \\[1ex] \max(E_s\,\varepsilon_s;\ -f_{yk}^{-}) & \varepsilon_s < 0 \end{cases} \qquad |\varepsilon_s| \le \varepsilon_{ud}
$$

## Im Code

- [[opencivil.nachweis.resistenzlinie#Ebenenlinie.protokoll_ansatz|Ebenenlinie.protokoll_ansatz]]
- [[opencivil.querschnitt.analyse#Querschnittsanalyse.werkstoffe_protokollieren|Querschnittsanalyse.werkstoffe_protokollieren]]

## Themen

- [[Schiefe Biegung]]
- [[Knicken]]
- [[Biegung und Normalkraft]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Elastisch mit $E_s$ bis zur Fliessgrenze, dann ein waagrechtes Plateau --
auf Zug bei $f_{yd}$, auf Druck bei $f_{yd}^-$. Die Verfestigung nach dem
Fliessen wird nicht angesetzt; das liegt auf der sicheren Seite. Begrenzt
ist die Dehnung durch $\varepsilon_{ud}$: dort endet die Linie aus
Dehnungsebenen auf der Zugseite.

Mit charakteristischen Werten stehen $f_{yk}$ und $f_{yk}^-$ an ihrer Stelle.
