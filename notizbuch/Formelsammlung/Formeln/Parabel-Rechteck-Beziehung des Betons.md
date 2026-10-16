---
erzeugt: 82dec5e3e818
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.2.1.6"
---
> [!info] Normstelle
> SIA 262:2025, 4.2.1.6

*In der Herleitung: «C30/37: Parabel-Rechteck-Beziehung, Bemessungswerte»*

$$
\sigma_c(\varepsilon_c) = \begin{cases} -f_{cd} \cdot \dfrac{k_\sigma\,\eta - \eta^2}{1 + (k_\sigma - 2)\,\eta} & 0 \le |\varepsilon_c| \le \varepsilon_{c1d},\ \eta = \dfrac{|\varepsilon_c|}{\varepsilon_{c1d}} \\[2ex] -f_{cd} & \varepsilon_{c1d} < |\varepsilon_c| \le \varepsilon_{c2d} \\[1ex] 0 & |\varepsilon_c| > \varepsilon_{c2d} \quad (\text{jenseits der Bruchstauchung}) \\[1ex] 0 & \varepsilon_c > 0 \quad (\text{Zug, gerissen}) \end{cases}
$$

*In der Herleitung: «Werkstoffgesetze: Beton, Parabel-Rechteck»*

$$
\sigma_c(\varepsilon_c) = \begin{cases} -f_{ck} \cdot \dfrac{k_\sigma\,\eta - \eta^2}{1 + (k_\sigma - 2)\,\eta} & 0 \le |\varepsilon_c| \le \varepsilon_{c1d},\ \eta = \dfrac{|\varepsilon_c|}{\varepsilon_{c1d}} \\[2ex] -f_{ck} & \varepsilon_{c1d} < |\varepsilon_c| \le \varepsilon_{c2d} \\[1ex] 0 & |\varepsilon_c| > \varepsilon_{c2d} \quad (\text{jenseits der Bruchstauchung}) \\[1ex] 0 & \varepsilon_c > 0 \quad (\text{Zug, gerissen}) \end{cases}
$$

## Im Code

- [[opencivil.nachweis.rechenwahl#protokoll_betongesetz|protokoll_betongesetz]]
- [[opencivil.querschnitt.analyse#Querschnittsanalyse.werkstoffe_protokollieren|Querschnittsanalyse.werkstoffe_protokollieren]]
- [[opencivil.spannungsanalyse#herleitung|herleitung]]

## Themen

- [[Schiefe Biegung]]
- [[Knicken]]
- [[Biegung und Normalkraft]]
- [[Stahlspannung gegen Fliessen]]
- [[Stahlspannung aus Rissbreite]]
- [[Spannung-Dehnung-Analyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie der Beton auf Druck antwortet, wirklichkeitsnah: erst eine Parabel bis
zur Festigkeit bei $\varepsilon_{c1d}$, dann ein Plateau bis zur
Bruchstauchung $\varepsilon_{c2d}$. Auf Zug trägt er nichts -- gerechnet wird
der gerissene Querschnitt. Druck ist negativ.

Die Form der Parabel bestimmt der
[[Krümmungsbeiwert der Spannungs-Dehnungs-Beziehung|Krümmungsbeiwert k_σ]];
mit $k_\sigma = 2$ ist es die gewöhnliche Parabel. Mit Bemessungswerten ist
die Höhe $f_{cd}$, charakteristisch $f_{ck}$.

Gebraucht wird die Beziehung von der Linie aus Dehnungsebenen, vom
Querschnittslöser bei den Stahlspannungen und beim Knicken, und von der
Spannung-Dehnung-Analyse. Für den Bruchzustand gibt sie ähnliche
Widerstände wie der [[Spannungsblock des Betons]]; dazwischen, unter
Gebrauchslast, beschreibt nur sie die Druckzone richtig.

Jenseits der Bruchstauchung trägt der Beton nichts mehr: die Faser ist
zerdrückt, und eine Suche bleibt so im gültigen Bereich. Auf der Grenze
selbst gilt noch das Plateau, auch um eine Rundung darüber -- sonst kippte
eine Faser, die genau auf ihr liegt, an der letzten Stelle auf null.
