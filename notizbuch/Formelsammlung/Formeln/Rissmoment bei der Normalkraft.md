---
erzeugt: 5556c39c7c69
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
M_{Riss}(N) = \left(f_{ct,eff} - \frac{N}{A}\right) \cdot W
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $f_{ct,eff}$ | – | N/mm² | [[Wirksame Zugfestigkeit]] |
| $N$ | – | kN | Zwischenwert |
| $A$ | Fläche des Bruttoquerschnitts | mm² | [[Fläche eines Rechtecks]], Zwischenwert |
| $W$ | – | ·10⁶ mm³ | [[Widerstandsmoment zum gezogenen Rand]], [[Widerstandsmoment zum gezogensten Betonpunkt]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  M_{Riss}(N) &= \left(f_{ct,eff} - \frac{N}{A}\right) \cdot W \\
  &= \left(2.76\,\mathrm{N}/\mathrm{mm}^{2} - \frac{-300\,\mathrm{kN}}{300000\,\mathrm{mm}^{2}}\right) \cdot 15\,\cdot 10^{6}\,\mathrm{mm}^{3} \\
  &= 56.4\,\mathrm{kNm}
\end{aligned}
$$

## Im Code

- [[opencivil.spannungsanalyse.riss#Bruttoriss._herleitung_rissmoment|Bruttoriss._herleitung_rissmoment]]

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
