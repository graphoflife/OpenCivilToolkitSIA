---
erzeugt: 9075cff50061
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.6.4.6, (61)"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.6.4.6, (61)

$$
b_s = \min\left[1.5 \cdot \sqrt{r_{sx} \cdot r_{sy}};\ l_{min}\right]
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $r_{sx}$ | – | mm | [[Abstand zum Momentennullpunkt]] |
| $r_{sy}$ | – | mm | [[Abstand zum Momentennullpunkt]] |
| $l_{min}$ | – | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  b_s &= \min\left[1.5 \cdot \sqrt{r_{sx} \cdot r_{sy}};\ l_{min}\right] \\
  &= \min\left[1.5 \cdot \sqrt{1540\,\mathrm{mm} \cdot 1540\,\mathrm{mm}};\ 7000\,\mathrm{mm}\right] \\
  &= 2310\,\mathrm{mm}
\end{aligned}
$$

## Gebraucht von

- [[Breite des Stützstreifens am Plattenrand]]
- [[Mittleres Moment im Stützstreifen]]

## Im Code

- [[opencivil.durchstanzen.nachweis#Durchstanzen._m_sd|Durchstanzen._m_sd]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

In Näherungsstufe 2 wird das Moment über die Breite des Stützstreifens
gemittelt ([[Mittleres Moment im Stützstreifen]]). Sie wächst mit dem
[[Abstand zum Momentennullpunkt]] in beiden Richtungen und ist höchstens so
breit wie die kleinere Spannweite.
