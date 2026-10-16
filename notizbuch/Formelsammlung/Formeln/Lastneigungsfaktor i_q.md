---
erzeugt: 8106a210b0f3
art: formel
tags: [formel]
normstelle: "Kap. 9.2.14"
---
> [!info] Normstelle
> Kap. 9.2.14

*In der Herleitung: «Lastneigungsfaktor der seitlichen Auflast»*

$$
i_q = \left[1 - \frac{0.5 \cdot T_{Ed}}{N_{Ed} + b \cdot L \cdot c_{eff} \cdot \cot \varphi_{eff}}\right]^{5}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $T_{Ed}$ | Einwirkung in der Sohle | kN | Zwischenwert |
| $N_{Ed}$ | Einwirkung normal zur Sohle | kN | Zwischenwert |
| $b$ | Breite des Fundaments | m | Vorgabe |
| $L$ | Länge des Fundaments | m | Vorgabe |
| $c_{eff}$ | Kohäsion, Bemessungswert | kPa | [[Bemessungswert der Kohäsion]] |
| $\varphi_{eff}$ | Reibungswinkel, Bemessungswert | ° | [[Bemessungswert des Reibungswinkels]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\begin{aligned}
  i_q &= \left[1 - \frac{0.5 \cdot T_{Ed}}{N_{Ed} + b \cdot L \cdot c_{eff} \cdot \cot \varphi_{eff}}\right]^{5} \\
  &= \left[1 - \frac{0.5 \cdot 150\,\mathrm{kN}}{1500\,\mathrm{kN} + 2\,\mathrm{m} \cdot 2.5\,\mathrm{m} \cdot 0\,\mathrm{kPa} \cdot \cot 27.51{}^{\circ}}\right]^{5} \\
  &= 0.77
\end{aligned}
$$

## Gebraucht von

- [[Bruchspannung in der Sohle]]
- [[Lastneigungsfaktor i_c]]

## Im Code

- [[opencivil.geotechnik.grundbruch#Grundbruch|Grundbruch._drainierter_fall]]

## Themen

- [[Grundbruch]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Lastneigung mindert die Tragfähigkeit stark, mit der fünften Potenz. Im
Nenner steht neben $N$ der Anteil $b\,L\,c\cot\varphi$: die Kohäsion wirkt
wie ein allseitiger Druck und macht die Last verhältnismässig weniger schräg.

Ohne Kohäsion bleiben bei $\delta_R = 10°$ noch 63 %, bei 20° noch 37 %
(Tabelle 9.2.16). Wird die Klammer kleiner als null, gilt null.
