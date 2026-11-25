---
erzeugt: a42b752b630f
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.2.1.5, Figur 12; 4.2.1.6, (27)"
---
> [!info] Normstelle
> SIA 262:2025, 4.2.1.5, Figur 12; 4.2.1.6, (27)

*In der Herleitung: «Werkstoffgesetz C30/37, Bemessungswerte: Beton, Parabel-Rechteck»*

$$
\sigma_c(\varepsilon_c) = \begin{cases} -f_{cd} \cdot \dfrac{k_\sigma\,\eta - \eta^2}{1 + (k_\sigma - 2)\,\eta} & 0 \le |\varepsilon_c| \le \varepsilon_{c1d},\ \eta = \dfrac{|\varepsilon_c|}{\varepsilon_{c1d}} \\[2ex] -f_{cd} & \varepsilon_{c1d} < |\varepsilon_c| \le \varepsilon_{c2d} \\[1ex] 0 & |\varepsilon_c| > \varepsilon_{c2d} \quad (\text{jenseits der Bruchstauchung}) \\[1ex] 0 & \varepsilon_c > 0 \quad (\text{Zug, gerissen}) \end{cases}
$$

*In der Herleitung: «Werkstoffgesetze im Gebrauchszustand: Beton, Parabel-Rechteck»*

$$
\sigma_c(\varepsilon_c) = \begin{cases} -f_{ck} \cdot \dfrac{k_\sigma\,\eta - \eta^2}{1 + (k_\sigma - 2)\,\eta} & 0 \le |\varepsilon_c| \le \varepsilon_{c1d},\ \eta = \dfrac{|\varepsilon_c|}{\varepsilon_{c1d}} \\[2ex] -f_{ck} & \varepsilon_{c1d} < |\varepsilon_c| \le \varepsilon_{c2d} \\[1ex] 0 & |\varepsilon_c| > \varepsilon_{c2d} \quad (\text{jenseits der Bruchstauchung}) \\[1ex] 0 & \varepsilon_c > 0 \quad (\text{Zug, gerissen}) \end{cases}
$$

## Im Code

- [[opencivil.querschnitt.werkstoffgesetz#Gesetz.protokoll|Gesetz.protokoll]]

## Themen

- [[Schiefe Biegung]]
- [[Innerer Pfahlwiderstand]]
- [[Stahlspannung aus Rissbreite]]
- [[Stahlspannung gegen Fliessen]]
- [[Knicken]]
- [[Biegung und Normalkraft]]
- [[Zwängung auf Biegung]]
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

Unter Gebrauchslast liegt die Betonspannung weit unter der Festigkeit, und
die Parabel ist dort beinahe eine Gerade. Bis 2026-11-25 gab es darum für die
Stahlspannungen die Rechenart «elastisch»: der Beton linear mit dem
[[Wirksamer Elastizitätsmodul|wirksamen Modul]], ohne Zug. Ihre
Stahlspannungen lagen um etwa ein Prozent neben denen der Parabel, und der
Benutzer hat sie gestrichen; die Stahlspannungen rechnen seither präzise.

Jenseits der Bruchstauchung trägt der Beton nichts mehr: die Faser ist
zerdrückt, und eine Suche bleibt so im gültigen Bereich. Auf der Grenze
selbst gilt noch das Plateau, auch um eine Rundung darüber -- sonst kippte
eine Faser, die genau auf ihr liegt, an der letzten Stelle auf null.
