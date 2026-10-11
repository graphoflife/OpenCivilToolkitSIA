---
erzeugt: 4edc60977a18
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

- `opencivil.nachweis.resistenzlinie:Ebenenlinie.protokoll_ansatz`
- `opencivil.querschnitt.analyse:Querschnittsanalyse.werkstoffe_protokollieren`

## Themen

- [[Schiefe Biegung]]
- [[Biegung und Normalkraft]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->
