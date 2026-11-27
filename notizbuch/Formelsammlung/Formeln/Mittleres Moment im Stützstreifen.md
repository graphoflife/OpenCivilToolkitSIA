---
erzeugt: 8ede032498ee
art: formel
tags: [formel]
normstelle: ["SIA 262:2025, 4.3.6.4.7, (62)", "SIA 262:2025, 4.3.6.4.7, (63)", "SIA 262:2025, 4.3.6.4.7, (64)", "SIA 262:2025, 4.3.6.4.7, (65)"]
---
> [!info] Normstellen
> SIA 262:2025, 4.3.6.4.7, (62) · SIA 262:2025, 4.3.6.4.7, (63) · SIA 262:2025, 4.3.6.4.7, (64) · SIA 262:2025, 4.3.6.4.7, (65)

*In der Herleitung: «Mittleres Moment im Stützstreifen in x»*

$$
m_{sd,x} = V_d \cdot \left(\frac{1}{8} + \frac{e_{u,x}}{2 \cdot b_s}\right)
$$

*In der Herleitung: «Mittleres Moment im Stützstreifen in x»*

$$
m_{sd,x} = \max\left[V_d \cdot \left(\frac{1}{8} + \frac{e_{u,x}}{2 \cdot b_s}\right);\ 0.25 \cdot V_d\right]
$$

*In der Herleitung: «Mittleres Moment im Stützstreifen in y»*

$$
m_{sd,y} = V_d \cdot \left(\frac{1}{8} + \frac{e_{u,y}}{b_{s,y}}\right)
$$

*In der Herleitung: «Mittleres Moment im Stützstreifen in x»*

$$
m_{sd,x} = \max\left[V_d \cdot \left(\frac{1}{8} + \frac{e_{u,x}}{b_{s,x}}\right);\ 0.5 \cdot V_d\right]
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $V_d$ | Bemessungswert der Auflagerkraft | kN | Vorgabe, Zwischenwert |
| $e_{u,x}$ | – | mm | Zwischenwert |
| $b_s$ | Breite des Stützstreifens | mm | [[Breite des Stützstreifens]] |
| $e_{u,y}$ | – | mm | Zwischenwert |
| $b_{s,y}$ | Breite des Stützstreifens in y | mm | [[Breite des Stützstreifens senkrecht zum Rand]] |
| $b_{s,x}$ | Breite des Stützstreifens in x | mm | [[Breite des Randstreifens an der Eckstütze]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
m_{sd,x} = V_d \cdot \left(\frac{1}{8} + \frac{e_{u,x}}{2 \cdot b_s}\right) = 900\,\mathrm{kN} \cdot \left(\frac{1}{8} + \frac{0\,\mathrm{mm}}{2 \cdot 2310\,\mathrm{mm}}\right) = 112.5\,\mathrm{kNm}/\mathrm{m}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  m_{sd,x} &= \max\left[V_d \cdot \left(\frac{1}{8} + \frac{e_{u,x}}{2 \cdot b_s}\right);\ 0.25 \cdot V_d\right] \\
  &= \max\left[500\,\mathrm{kN} \cdot \left(\frac{1}{8} + \frac{0\,\mathrm{mm}}{2 \cdot 2310\,\mathrm{mm}}\right);\ 0.25 \cdot 500\,\mathrm{kN}\right] \\
  &= 125\,\mathrm{kNm}/\mathrm{m}
\end{aligned}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
m_{sd,y} = V_d \cdot \left(\frac{1}{8} + \frac{e_{u,y}}{b_{s,y}}\right) = 500\,\mathrm{kN} \cdot \left(\frac{1}{8} + \frac{1\,\mathrm{mm}}{1550\,\mathrm{mm}}\right) = 62.7\,\mathrm{kNm}/\mathrm{m}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  m_{sd,x} &= \max\left[V_d \cdot \left(\frac{1}{8} + \frac{e_{u,x}}{b_{s,x}}\right);\ 0.5 \cdot V_d\right] \\
  &= \max\left[80\,\mathrm{kN} \cdot \left(\frac{1}{8} + \frac{153\,\mathrm{mm}}{600\,\mathrm{mm}}\right);\ 0.5 \cdot 80\,\mathrm{kN}\right] \\
  &= 40\,\mathrm{kNm}/\mathrm{m}
\end{aligned}
$$

## Gebraucht von

- [[Plattenrotation]]

## Im Code

- [[opencivil.durchstanzen.nachweis#Stuetzenrechnung._m_sd|Stuetzenrechnung._m_sd]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

In Näherungsstufe 2 wird das Moment im Stützstreifen aus der Auflagerkraft
geschätzt (4.3.6.4.7): ein Achtel von $V_d$, dazu ein Anteil aus der
Exzentrizität $e_u$, verteilt über die [[Breite des Stützstreifens]]. Für
Rand- und Eckstützen gelten eigene Gleichungen mit Mindestwerten, und der
Rand begrenzt den Streifen
([[Breite des Stützstreifens senkrecht zum Rand]],
[[Breite des Randstreifens an der Eckstütze]]). Das Moment geht als
$m_{sd}/m_{Rd}$ in die [[Plattenrotation]] ein.
