---
erzeugt: e88924496f81
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Rissmoment bei der Normalkraft»*

$$
M_{Riss}(N) = M_{Riss} - N \cdot \frac{h}{6}
$$

*In der Herleitung: «Rissmoment bei der Normalkraft»*

$$
M_{Riss}(N) = \left(f_{ct,eff} - \frac{N}{A}\right) \cdot W
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $M_{Riss}$ | – | kNm | Zwischenwert |
| $N$ | – | kN | Zwischenwert |
| $h$ | Plattendicke | mm | Vorgabe |
| $f_{ct,eff}$ | – | N/mm² | [[Wirksame Zugfestigkeit]] |
| $A$ | Fläche des Bruttoquerschnitts | mm² | Zwischenwert |
| $W$ | – | ·10⁶ mm³ | [[Widerstandsmoment zum gezogensten Betonpunkt]], [[Widerstandsmoment zum gezogenen Rand]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
M_{Riss}(N) = M_{Riss} - N \cdot \frac{h}{6} = 41.4\,\mathrm{kNm} - \left(-300\,\mathrm{kN}\right) \cdot \frac{300\,\mathrm{mm}}{6} = 56.4\,\mathrm{kNm}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  M_{Riss}(N) &= \left(f_{ct,eff} - \frac{N}{A}\right) \cdot W \\
  &= \left(2.56\,\mathrm{N}/\mathrm{mm}^{2} - \frac{-500\,\mathrm{kN}}{330000\,\mathrm{mm}^{2}}\right) \cdot 56.19\,\cdot 10^{6}\,\mathrm{mm}^{3} \\
  &= 228.9\,\mathrm{kNm}
\end{aligned}
$$

## Im Code

- [[opencivil.spannungsanalyse.platte#Loeserpaar.herleitung_riss|Loeserpaar.herleitung_riss]]
- [[opencivil.spannungsanalyse.schnitt#Schnittpaar.herleitung_riss|Schnittpaar.herleitung_riss]]

## Themen

- [[Spannung-Dehnung-Analyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Am Bruttoquerschnitt reisst der gezogene Rand, wenn $N/A + M/W$ die wirksame
Zugfestigkeit erreicht. Mit $A = b h$ und $W = b h^2/6$ verschiebt eine
Normalkraft das Rissmoment um $N \cdot h/6$: Druck hebt es, Zug senkt es.
Beim Rissmoment springt die Krümmung bei demselben Moment vom ungerissenen auf
den gerissenen Wert.

Gerechnet wird wie beim [[Rissmoment des ungerissenen Querschnitts]] am
Bruttoquerschnitt ohne Stahl -- nach Vorgabe, nicht nachgeschlagen.

Beim gezeichneten Querschnitt gehört $W$ zur Ecke, die unter reiner Biegung
zuerst reisst: kippt die Nulllinie, mit dem Deviationsmoment
([[Widerstandsmoment zum gezogensten Betonpunkt]]), «einachsig» zum gezogenen
Rand ([[Widerstandsmoment zum gezogenen Rand]]). Die Normalkraft verschiebt
das Rissmoment um $N \cdot W/A$.
