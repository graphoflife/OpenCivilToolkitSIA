---
erzeugt: 8ceed2dd6f34
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.6.4.5"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.6.4.5

*In der Herleitung: «Biegewiderstand im Stützstreifen in x»*

$$
m_{Rd,x} = a_{s,x} \cdot f_{yd} \cdot \left(d_x - \frac{0.85 \cdot x_x}{2}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $a_{s,x}$ | Bewehrung in x je Meter | mm^2/m | [[Biegebewehrung im Stützstreifen je Meter]] |
| $f_{yd}$ | Bemessungswert der Fliessgrenze | N/mm² | [[Bemessungswert der Fliessgrenze]] |
| $d_x$ | – | mm | [[Statische Höhe der äusseren Lage]] |
| $x_x$ | – | mm | [[Druckzonenhöhe im Stützstreifen]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  m_{Rd,x} &= a_{s,x} \cdot f_{yd} \cdot \left(d_x - \frac{0.85 \cdot x_x}{2}\right) \\
  &= 1340\,\mathrm{mm}^{2}/\mathrm{m} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(242\,\mathrm{mm} - \frac{0.85 \cdot 34.3\,\mathrm{mm}}{2}\right) \\
  &= 132.5\,\mathrm{kNm}/\mathrm{m}
\end{aligned}
$$

## Gebraucht von

- [[Plattenrotation]]

## Im Code

- [[opencivil.durchstanzen.nachweis#Durchstanzen._m_Rd|Durchstanzen._m_Rd]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Biegewiderstand je Meter, aus dem Gleichgewicht mit dem Spannungsblock:
die Zugkraft der Bewehrung $a_s \cdot f_{yd}$ mal ihr Hebelarm bis zur Mitte
der Druckzone ([[Druckzonenhöhe im Stützstreifen]]). In den Näherungsstufen 2
und 3 steht er im Nenner der [[Plattenrotation]]: je näher das Moment
$m_{sd}$ an $m_{Rd}$ heranreicht, desto stärker dreht sich die Platte.
