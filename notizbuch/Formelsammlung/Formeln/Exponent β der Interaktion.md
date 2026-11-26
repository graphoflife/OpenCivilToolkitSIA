---
erzeugt: 707b26e232e7
art: formel
tags: [formel]
normstelle: "SIA 263:2013, 5.1.10.2, (51); 5.1.10.4"
---
> [!info] Normstelle
> SIA 263:2013, 5.1.10.2, (51); 5.1.10.4

*In der Herleitung: «Exponent der Interaktion»*

$$
\beta = \max\left(1;\ 0.4 + \frac{|N_{Ed}|}{N_{Rd}} + \frac{b}{h - t_f}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\vert N_{Ed}\vert $ | Druckkraft | kN | Zwischenwert |
| $N_{Rd}$ | Druckwiderstand des Querschnitts | kN | [[Normalkraftwiderstand eines Stahlquerschnitts]] |
| $b$ | Breite des Profils | mm | Zwischenwert |
| $h$ | Höhe des Profils | mm | Zwischenwert |
| $t_f$ | Dicke des Flanschs | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  \beta &= \max\left(1;\ 0.4 + \frac{|N_{Ed}|}{N_{Rd}} + \frac{b}{h - t_f}\right) \\
  &= \max\left(1;\ 0.4 + \frac{1000\,\mathrm{kN}}{5275.5\,\mathrm{kN}} + \frac{220\,\mathrm{mm}}{600\,\mathrm{mm} - 19\,\mathrm{mm}}\right) \\
  &= 1
\end{aligned}
$$

## Im Code

- [[opencivil.nachweis.qa_stahl_stabilitaet#_Herleitung.gleichung_51|_Herleitung.gleichung_51]]

## Themen

- [[Knicken und Kippen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Mit $\beta = 1$ wäre (51) eine Gerade: die Anteile der beiden Momente
addierten sich wie in (50). Ein grösseres $\beta$ wölbt sie nach aussen –
zweiachsige Biegung wird günstiger, als die Gerade sagt. $\beta$ wächst
mit dem Anteil der Druckkraft am Querschnittswiderstand und mit der
Breite des Profils im Verhältnis zu seiner Höhe; kleiner als eins wird
es nie.
