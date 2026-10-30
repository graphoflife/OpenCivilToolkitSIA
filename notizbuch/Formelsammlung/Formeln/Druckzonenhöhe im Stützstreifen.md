---
erzeugt: b3d2fbd48b20
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Druckzonenhöhe in x, je Meter»*

$$
x_x = \frac{a_{s,x} \cdot f_{yd}}{0.85 \cdot f_{cd}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $a_{s,x}$ | Bewehrung in x je Meter | mm^2/m | [[Biegebewehrung im Stützstreifen je Meter]] |
| $f_{yd}$ | Bemessungswert der Fliessgrenze | N/mm² | [[Bemessungswert der Fliessgrenze]] |
| $f_{cd}$ | Bemessungswert der Betondruckfestigkeit | N/mm² | [[Bemessungswert der Betondruckfestigkeit]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
x_x = \frac{a_{s,x} \cdot f_{yd}}{0.85 \cdot f_{cd}} = \frac{1340\,\mathrm{mm}^{2}/\mathrm{m} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2}}{0.85 \cdot 20\,\mathrm{N}/\mathrm{mm}^{2}} = 34.3\,\mathrm{mm}
$$

## Gebraucht von

- [[Biegewiderstand im Stützstreifen]]

## Im Code

- [[opencivil.durchstanzen.nachweis#Durchstanzen._m_Rd|Durchstanzen._m_Rd]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Höhe der Druckzone je Meter, aus dem Gleichgewicht zwischen der Zugkraft
der Bewehrung und dem Spannungsblock, der $0.85 \cdot x$ hoch ist und mit
$f_{cd}$ drückt. Daraus folgt der Hebelarm im
[[Biegewiderstand im Stützstreifen]].
