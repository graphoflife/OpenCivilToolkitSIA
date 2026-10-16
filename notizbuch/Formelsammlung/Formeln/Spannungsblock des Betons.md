---
erzeugt: f4616c49caca
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Werkstoffgesetze: Beton, Spannungsblock 0.85·x»*

$$
\sigma_c(\varepsilon_c) = \begin{cases} 0 & \varepsilon_c > -(1 - 0.85) \cdot \varepsilon_{c2d} \\[1ex] -f_{cd} & -\varepsilon_{c2d} \le \varepsilon_c \le -(1 - 0.85) \cdot \varepsilon_{c2d} \\[1ex] 0 & \varepsilon_c < -\varepsilon_{c2d} \quad (\text{jenseits der Bruchstauchung}) \end{cases}
$$

*In der Herleitung: «Werkstoffgesetze im Gebrauchszustand: Beton, Spannungsblock 0.85·x»*

$$
\sigma_c(\varepsilon_c) = \begin{cases} 0 & \varepsilon_c > -(1 - 0.85) \cdot \varepsilon_{c2d} \\[1ex] -f_{ck} & -\varepsilon_{c2d} \le \varepsilon_c \le -(1 - 0.85) \cdot \varepsilon_{c2d} \\[1ex] 0 & \varepsilon_c < -\varepsilon_{c2d} \quad (\text{jenseits der Bruchstauchung}) \end{cases}
$$

## Im Code

- [[opencivil.nachweis.rechenwahl#protokoll_betongesetz|protokoll_betongesetz]]
- [[opencivil.querschnitt.analyse#Querschnittsanalyse.werkstoffe_protokollieren|Querschnittsanalyse.werkstoffe_protokollieren]]
- [[opencivil.spannungsanalyse#herleitung|herleitung]]

## Themen

- [[Knicken]]
- [[Stahlspannung aus Rissbreite]]
- [[Biegung und Normalkraft]]
- [[Schiefe Biegung]]
- [[Spannung-Dehnung-Analyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die vereinfachte Druckzone der Handrechnung, als Gesetz geschrieben: unter
$(1 - 0.85)\,\varepsilon_{c2d}$ Stauchung keine Spannung, darüber durchgehend
$f_{cd}$. Liegt der gedrückte Rand bei $\varepsilon_{c2d}$ -- im Bruchzustand
--, ist das genau der Block der Höhe $0.85\,x$, mit dem man von Hand rechnet.

Als Gesetz gilt er auch dort, wo der Rand nicht bei $\varepsilon_{c2d}$ liegt;
so rechnen die Linie aus Dehnungsebenen, der Querschnittslöser und die
Analysen mit der Rechenart «0.85·x-Vereinfachung». Unter Gebrauchslast ist das ein grobes
Bild: die Druckresultierende liegt dann am Rand. Die Normstelle des Blocks
als Gesetz ist offen; sie wird nicht erfunden.

Jenseits der Bruchstauchung trägt auch der Block nichts mehr, wie die
[[Parabel-Rechteck-Beziehung des Betons|Parabel]]; auf der Grenze selbst
gilt er noch, auch um eine Rundung darüber.
