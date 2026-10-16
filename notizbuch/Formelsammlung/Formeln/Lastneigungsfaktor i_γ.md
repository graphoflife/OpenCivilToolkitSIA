---
erzeugt: a011a3e5ba44
art: formel
tags: [formel]
normstelle: "Kap. 9.2.14"
---
> [!info] Normstelle
> Kap. 9.2.14

*In der Herleitung: «Lastneigungsfaktor des Gleitkörpergewichts»*

$$
i_{\gamma} = \left[1 - \frac{\left(0.7 - \frac{\alpha}{450^\circ}\right) \cdot T_{Ed}}{N_{Ed} + b \cdot L \cdot c_{eff} \cdot \cot \varphi_{eff}}\right]^{5}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\alpha$ | Neigung der Sohle | ° | Vorgabe |
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
  i_{\gamma} &= \left[1 - \frac{\left(0.7 - \frac{\alpha}{450^\circ}\right) \cdot T_{Ed}}{N_{Ed} + b \cdot L \cdot c_{eff} \cdot \cot \varphi_{eff}}\right]^{5} \\
  &= \left[1 - \frac{\left(0.7 - \frac{0{}^{\circ}}{450^\circ}\right) \cdot 150\,\mathrm{kN}}{1500\,\mathrm{kN} + 2\,\mathrm{m} \cdot 2.5\,\mathrm{m} \cdot 0\,\mathrm{kPa} \cdot \cot 27.51{}^{\circ}}\right]^{5} \\
  &= 0.7
\end{aligned}
$$

## Gebraucht von

- [[Bruchspannung in der Sohle]]

## Im Code

- [[opencivil.geotechnik.grundbruch#Grundbruch|Grundbruch._drainierter_fall]]

## Themen

- [[Grundbruch]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Für das Gewicht des Gleitkörpers mindert die Lastneigung noch stärker als
für die Auflast: 0.7 statt 0.5 in der Klammer. Eine geneigte Sohle mildert
das etwas, um $\alpha/450°$.

Ohne Kohäsion und mit waagrechter Sohle bleiben bei $\delta_R = 10°$ noch
52 % (Tabelle 9.2.16). Wird die Klammer kleiner als null, gilt null.
