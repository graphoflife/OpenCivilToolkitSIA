---
erzeugt: dc535bf862dd
art: formel
tags: [formel]
normstelle: "SIA 264:2014, 5.4.3.5, (28)"
---
> [!info] Normstelle
> SIA 264:2014, 5.4.3.5, (28)

*In der Herleitung: «Längsschubwiderstand zwischen Blech und Beton»*

$$
V_{L,Rd} = b \cdot d_p \cdot \frac{m \cdot \frac{A_p}{b \cdot L_s} + k}{\gamma_v}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $b$ | Breite der Decke, n · b\_s | mm | Zwischenwert |
| $d_p$ | Statische Höhe der Decke | mm | [[Statische Höhe einer Blechverbunddecke]] |
| $m$ | Beiwert m aus Versuchen | N/mm² | Zwischenwert |
| $A_p$ | Fläche des Blechs über die Breite b | mm² | Zwischenwert |
| $L_s$ | Schublänge | mm | [[Schublänge einer Blechverbunddecke]], Zwischenwert |
| $k$ | Beiwert k aus Versuchen | N/mm² | Zwischenwert |
| $\gamma_v$ | Widerstandsbeiwert für Verbund | – | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  V_{L,Rd} &= b \cdot d_p \cdot \frac{m \cdot \frac{A_p}{b \cdot L_s} + k}{\gamma_v} \\
  &= 1000\,\mathrm{mm} \cdot 108.9\,\mathrm{mm} \cdot \frac{150\,\mathrm{N}/\mathrm{mm}^{2} \cdot \frac{1100\,\mathrm{mm}^{2}}{1000\,\mathrm{mm} \cdot 675\,\mathrm{mm}} + 0.1\,\mathrm{N}/\mathrm{mm}^{2}}{1.25} \\
  &= 30\,\mathrm{kN}
\end{aligned}
$$

## Im Code

- [[opencivil.nachweis.qa_blechverbund#KennzahlenBlechQA|KennzahlenBlechQA._laengsschub]]

## Themen

- [[Blechverbunddecke]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Blech und Beton tragen nur zusammen, solange ihre Verbindung hält – über
Noppen und Sicken im Blech, hinterschnittene Rippen oder eine
Endverankerung. Wie gut ein bestimmtes Blech das kann, fasst die
m-k-Methode in zwei Zahlen $m$ und $k$: der Hersteller bestimmt sie in
Versuchen an Decken und nennt sie im Datenblatt. $k$ darf negativ sein.

Mit ihnen, der Fläche $A_p$ des Blechs über die Breite $b$, der
[[Statische Höhe einer Blechverbunddecke|statischen Höhe]] $d_p$ und der
[[Schublänge einer Blechverbunddecke|Schublänge]] $L_s$ gibt Gleichung (28)
die grösste Querkraft, die die Decke trägt, bevor das Blech im Beton
gleitet; $\gamma_v = 1.25$. Je kürzer die Schublänge, desto grösser der
Widerstand: kurze, hoch belastete Felder versagen eher am Längsschub als
lange.

Die Norm lässt statt der m-k-Methode auch die teilweise Verdübelung nach
SN EN 1994-1-1 zu. Das Werkzeug rechnet nur die m-k-Methode.
