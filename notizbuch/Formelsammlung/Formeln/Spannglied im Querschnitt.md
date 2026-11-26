---
erzeugt: 9e5915ad8937
art: formel
tags: [formel]
normstelle: ["SIA 262:2025, 4.1.5.1.5; SIA 262:2025, 4.1.5.5.1; 4.2.3.3, Figur 17", "SIA 262:2025, 4.1.5.1.6", "SIA 262:2025, 4.1.5.5.2; SIA 262:2025, 4.1.5.1.5; 4.2.3.3, Figur 17"]
---
> [!info] Normstellen
> SIA 262:2025, 4.1.5.1.5; SIA 262:2025, 4.1.5.5.1; 4.2.3.3, Figur 17 · SIA 262:2025, 4.1.5.1.6 · SIA 262:2025, 4.1.5.5.2; SIA 262:2025, 4.1.5.1.5; 4.2.3.3, Figur 17

*In der Herleitung: «Werkstoffgesetz Spannglied 1, Bemessungswerte: mit Vordehnung»*

$$
\sigma_p(\varepsilon) = \begin{cases} \min\left(E_p\,(\varepsilon + \varepsilon_p);\ f_{pd}\right) & -\varepsilon_p < \varepsilon \le \varepsilon_{ud} - \varepsilon_p \\[1ex] 0 & \varepsilon \le -\varepsilon_p \quad (\text{entspannt}) \\[1ex] 0 & \varepsilon > \varepsilon_{ud} - \varepsilon_p \quad (\text{jenseits der Bruchdehnung}) \end{cases}
$$

*In der Herleitung: «Werkstoffgesetz Spannglied 2, Bemessungswerte: ohne Verbund»*

$$
\sigma_p(\varepsilon) = \sigma_{p\infty}
$$

*In der Herleitung: «Werkstoffgesetz Spannglied 3, Bemessungswerte: schlaff mit Restfestigkeit»*

$$
\sigma_p(\varepsilon) = \begin{cases} \min\left(E_p\,(\varepsilon + \varepsilon_p);\ f_{pd}\right) - \sigma_{p\infty} & -\varepsilon_p < \varepsilon \le \varepsilon_{ud} - \varepsilon_p \\[1ex] -\sigma_{p\infty} & \varepsilon \le -\varepsilon_p \quad (\text{entspannt}) \\[1ex] -\sigma_{p\infty} & \varepsilon > \varepsilon_{ud} - \varepsilon_p \quad (\text{jenseits der Bruchdehnung}) \end{cases}
$$

*In der Herleitung: «Werkstoffgesetze im gerissenen Zustand, Spannglied 1: mit Vordehnung»*

$$
\sigma_p(\varepsilon) = \begin{cases} \min\left(E_p\,(\varepsilon + \varepsilon_p);\ f_{p0.1k}\right) & -\varepsilon_p < \varepsilon \le \varepsilon_{ud} - \varepsilon_p \\[1ex] 0 & \varepsilon \le -\varepsilon_p \quad (\text{entspannt}) \\[1ex] 0 & \varepsilon > \varepsilon_{ud} - \varepsilon_p \quad (\text{jenseits der Bruchdehnung}) \end{cases}
$$

*In der Herleitung: «Werkstoffgesetze im gerissenen Zustand, Spannglied 3: schlaff mit Restfestigkeit»*

$$
\sigma_p(\varepsilon) = \begin{cases} \min\left(E_p\,(\varepsilon + \varepsilon_p);\ f_{p0.1k}\right) - \sigma_{p\infty} & -\varepsilon_p < \varepsilon \le \varepsilon_{ud} - \varepsilon_p \\[1ex] -\sigma_{p\infty} & \varepsilon \le -\varepsilon_p \quad (\text{entspannt}) \\[1ex] -\sigma_{p\infty} & \varepsilon > \varepsilon_{ud} - \varepsilon_p \quad (\text{jenseits der Bruchdehnung}) \end{cases}
$$

## Im Code

- [[opencivil.querschnitt.werkstoffgesetz#Gesetz.protokoll|Gesetz.protokoll]]

## Themen

- [[Schiefe Biegung]]
- [[Zwängung auf Biegung]]
- [[Stahlspannung aus Rissbreite]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie ein Stab hat ein Spannglied ein Gesetz über der Dehnung $\varepsilon$
des Betons an seiner Stelle. Es gibt drei Arten:

- **Mit Vordehnung und Verbund** (SIA 262:2025, 4.1.5.1.5): das Gesetz des
  [[Spannstahl|Spannstahls]] nach Figur 17, um die
  [[Vordehnung eines Spannglieds|Vordehnung]] $\varepsilon_p$ verschoben. Bei
  $\varepsilon = 0$ trägt es $\sigma_{p\infty}$, gezogen bis $f_{pd}$.
  Gestaucht um $\varepsilon_p$ ist es entspannt, und es reisst bei
  $\varepsilon_{ud} - \varepsilon_p$: so weit reicht seine Dehnungsgrenze.
- **Schlaff mit Restfestigkeit** (4.1.5.5.2): für den Fall, dass die
  Vorspannung schon als Einwirkung in den Lastfällen steht. Dann zählt nur,
  was das Glied über $\sigma_{p\infty}$ hinaus trägt – dasselbe Gesetz, um
  $\sigma_{p\infty}$ gesenkt, bis $f_{pd} - \sigma_{p\infty}$. Gestaucht oder
  gerissen fehlt bis $\sigma_{p\infty}$: die Kraft, die als Einwirkung
  angesetzt ist, ginge verloren.
- **Ohne Verbund** (4.1.5.1.6): die Kraft nach allen Verlusten, ohne
  Zuwachs, gleich welche Dehnung; einen Zuwachs liesse die Norm nur mit
  genaueren Untersuchungen zu. Schlaff angesetzt trägt ein Glied ohne
  Verbund darum nichts bei.

Vier Litzen ⌀15.7 aus Y1860 im Bruch: mit Verbund 600 · 1391 = 835 kN,
ohne Verbund 664 kN, schlaff mit Verbund 600 · (1391 − 1107) = 171 kN.
