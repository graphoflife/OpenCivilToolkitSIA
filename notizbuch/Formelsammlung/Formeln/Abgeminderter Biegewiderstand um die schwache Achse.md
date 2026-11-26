---
erzeugt: c98acf600494
art: formel
tags: [formel]
normstelle: "SIA 263:2013, 5.1.10.2, (51); 5.1.10.4"
---
> [!info] Normstelle
> SIA 263:2013, 5.1.10.2, (51); 5.1.10.4

*In der Herleitung: «Abgeminderter Widerstand um die schwache Achse z»*

$$
M_{z,red,Rd} = M_{z,Rd}^{+} \cdot \left(1 - \frac{|N_{Ed}|}{N_{K,Rd,min}}\right) \cdot \left(1 - \frac{|N_{Ed}|}{N_{cr,z}}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $M_{z,Rd}^{+}$ | Biegewiderstand des Querschnitts | kNm | [[Plastischer Biegewiderstand eines Stahlquerschnitts]] |
| $\vert N_{Ed}\vert $ | Druckkraft | kN | Zwischenwert |
| $N_{K,Rd,min}$ | Kleinerer Knickwiderstand | kN | Zwischenwert |
| $N_{cr,z}$ | Ideale Knicklast | kN | [[Knicklast nach Euler]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  M_{z,red,Rd} &= M_{z,Rd}^{+} \cdot \left(1 - \frac{|N_{Ed}|}{N_{K,Rd,min}}\right) \cdot \left(1 - \frac{|N_{Ed}|}{N_{cr,z}}\right) \\
  &= 164.2\,\mathrm{kNm} \cdot \left(1 - \frac{1000\,\mathrm{kN}}{3681.2\,\mathrm{kN}}\right) \cdot \left(1 - \frac{1000\,\mathrm{kN}}{7801.1\,\mathrm{kN}}\right) \\
  &= 104.3\,\mathrm{kNm}
\end{aligned}
$$

## Im Code

- [[opencivil.nachweis.qa_stahl_stabilitaet#_Herleitung.gleichung_51|_Herleitung.gleichung_51]]

## Themen

- [[Knicken und Kippen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

In [[Druck und zweiachsige Biegung im doppelsymmetrischen I-Stab|(51)]]
steht um die schwache Achse nicht der volle Biegewiderstand, sondern
einer, in dem die Druckkraft schon steckt. Zwei Faktoren mindern ihn:
$1 - N_{Ed}/N_{K,Rd,min}$ ist der Teil des Knickwiderstands, den die
Druckkraft nicht braucht – mit dem kleineren der beiden
Knickwiderstände –, und $1 - N_{Ed}/N_{cr,z}$ steht für die
Vergrösserung der Momente am ausgebogenen Stab, wie in
[[Druck und zweiachsige Biegung im Stab|(50)]].

Ohne Druckkraft bleibt der Biegewiderstand des Querschnitts; je näher
$N_{Ed}$ an den Knickwiderstand kommt, desto weniger Moment bleibt.
