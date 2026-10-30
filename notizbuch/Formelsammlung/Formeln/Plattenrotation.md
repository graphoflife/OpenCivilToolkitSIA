---
erzeugt: 7e6c711c2975
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.6.4.1, (60)"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.6.4.1, (60)

*In der Herleitung: «Plattenrotation in x»*

$$
\psi_x = 1.5 \cdot \frac{r_{sx}}{d} \cdot \frac{f_{yd}}{E_s} \cdot \left(\frac{m_{sd,x}}{m_{Rd,x}}\right)^{3/2}
$$

*In der Herleitung: «Plattenrotation in x»*

$$
\psi_x = 1.5 \cdot \frac{r_{sx}}{d} \cdot \frac{f_{yd}}{E_s}
$$

*In der Herleitung: «Plattenrotation in x»*

$$
\psi_x = 1.2 \cdot \frac{r_{sx}}{d} \cdot \frac{f_{yd}}{E_s} \cdot \left(\frac{m_{sd,x}}{m_{Rd,x}}\right)^{3/2}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $r_{sx}$ | Abstand zum Momentennullpunkt in x | mm | [[Abstand zum Momentennullpunkt]], Vorgabe |
| $d$ | – | mm | [[Mittlere statische Höhe der beiden Lagen der Zugbewehrung]] |
| $f_{yd}$ | Bemessungswert der Fliessgrenze | N/mm² | [[Bemessungswert der Fliessgrenze]] |
| $E_s$ | Elastizitätsmodul des Betonstahls | N/mm² | Vorgabe |
| $m_{sd,x}$ | Mittleres Moment im Stützstreifen, x | kNm/m | [[Mittleres Moment im Stützstreifen]], Vorgabe |
| $m_{Rd,x}$ | – | kNm/m | [[Biegewiderstand im Stützstreifen]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  \psi_x &= 1.5 \cdot \frac{r_{sx}}{d} \cdot \frac{f_{yd}}{E_s} \cdot \left(\frac{m_{sd,x}}{m_{Rd,x}}\right)^{3/2} \\
  &= 1.5 \cdot \frac{1540\,\mathrm{mm}}{234\,\mathrm{mm}} \cdot \frac{435\,\mathrm{N}/\mathrm{mm}^{2}}{200000\,\mathrm{N}/\mathrm{mm}^{2}} \cdot \left(\frac{111.8\,\mathrm{kNm}/\mathrm{m}}{132.5\,\mathrm{kNm}/\mathrm{m}}\right)^{3/2} \\
  &= 0.0166
\end{aligned}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\psi_x = 1.5 \cdot \frac{r_{sx}}{d} \cdot \frac{f_{yd}}{E_s} = 1.5 \cdot \frac{1540\,\mathrm{mm}}{234\,\mathrm{mm}} \cdot \frac{435\,\mathrm{N}/\mathrm{mm}^{2}}{200000\,\mathrm{N}/\mathrm{mm}^{2}} = 0.0215
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  \psi_x &= 1.2 \cdot \frac{r_{sx}}{d} \cdot \frac{f_{yd}}{E_s} \cdot \left(\frac{m_{sd,x}}{m_{Rd,x}}\right)^{3/2} \\
  &= 1.2 \cdot \frac{2\,\mathrm{m}}{340\,\mathrm{mm}} \cdot \frac{435\,\mathrm{N}/\mathrm{mm}^{2}}{200000\,\mathrm{N}/\mathrm{mm}^{2}} \cdot \left(\frac{180\,\mathrm{kNm}/\mathrm{m}}{298\,\mathrm{kNm}/\mathrm{m}}\right)^{3/2} \\
  &= 0.0072
\end{aligned}
$$

## Gebraucht von

- [[Massgebende Plattenrotation – die grössere]]

## Im Code

- [[opencivil.durchstanzen.nachweis#Durchstanzen._rotation|Durchstanzen._rotation]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Rotation der Platte über der Stütze bestimmt, wie breit der kritische
Schubriss wird ([[Beiwert k_r]]). Sie wächst mit dem
[[Abstand zum Momentennullpunkt]], mit der Fliessdehnung $f_{yd}/E_s$ und
mit dem Verhältnis von Moment zu Biegewiderstand im Stützstreifen; mit
grösserem $d$ wird sie kleiner. In Näherungsstufe 1 ist $m_{sd}/m_{Rd} = 1$,
die Bewehrung fliesst also. In Stufe 2 kommt $m_{sd}$ aus der Auflagerkraft
([[Mittleres Moment im Stützstreifen]]). In Stufe 3 kommt es aus einer
Berechnung nach der Elastizitätstheorie; dann steht 1.2 statt 1.5 vor der
Klammer.
