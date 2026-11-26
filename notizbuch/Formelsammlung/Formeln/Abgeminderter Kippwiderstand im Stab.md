---
erzeugt: 60936f08edac
art: formel
tags: [formel]
normstelle: "SIA 263:2013, 5.1.10.2, (51); 5.1.10.4"
---
> [!info] Normstelle
> SIA 263:2013, 5.1.10.2, (51); 5.1.10.4

*In der Herleitung: «Abgeminderter Widerstand um die starke Achse y»*

$$
M_{y,red,Rd} = \min\left(M_{D,Rd,min} \cdot \left(1 - \frac{|N_{Ed}|}{N_{K,Rd,min}}\right) \cdot \left(1 - \frac{|N_{Ed}|}{N_{cr,y}}\right);\ \omega_{y} \cdot M_{D,Rd}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $M_{D,Rd,min}$ | Kippwiderstand für konstantes Moment | kNm | Zwischenwert |
| $\vert N_{Ed}\vert $ | Druckkraft | kN | Zwischenwert |
| $N_{K,Rd,min}$ | Kleinerer Knickwiderstand | kN | Zwischenwert |
| $N_{cr,y}$ | Ideale Knicklast | kN | [[Knicklast nach Euler]] |
| $\omega_{y}$ | Beiwert der Momentenverteilung | – | [[Beiwert ω der Momentenverteilung]] |
| $M_{D,Rd}$ | Kippwiderstand | kNm | [[Kippwiderstand]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  M_{y,red,Rd} &= \min\left(M_{D,Rd,min} \cdot \left(1 - \frac{|N_{Ed}|}{N_{K,Rd,min}}\right) \cdot \left(1 - \frac{|N_{Ed}|}{N_{cr,y}}\right);\ \omega_{y} \cdot M_{D,Rd}\right) \\
  &= \min\left(1061.8\,\mathrm{kNm} \cdot \left(1 - \frac{1000\,\mathrm{kN}}{3681.2\,\mathrm{kN}}\right) \cdot \left(1 - \frac{1000\,\mathrm{kN}}{53037\,\mathrm{kN}}\right);\ 0.6 \cdot 1142.5\,\mathrm{kNm}\right) \\
  &= 685.5\,\mathrm{kNm}
\end{aligned}
$$

## Im Code

- [[opencivil.nachweis.qa_stahl_stabilitaet#_Herleitung.gleichung_51|_Herleitung.gleichung_51]]

## Themen

- [[Knicken und Kippen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Um die starke Achse geht (51) vom [[Kippwiderstand]] aus und mindert ihn
wie um die schwache Achse: um den Teil des Knickwiderstands, den die
Druckkraft braucht, und um die Vergrösserung am ausgebogenen Stab.

Welcher Kippwiderstand, hängt von der Biegung ab: bei zweiachsiger
Biegung der für ein konstantes Moment über die ganze Länge, $\eta = 1$,
bei einachsiger der mit der wirklichen Verteilung. Nach oben begrenzt
ihn $\omega_y \cdot M_{D,Rd}$: weil (51) das Moment mit $\omega_y$
abmindert, wäre der Nachweis sonst günstiger als das Kippen allein
nach (9).
