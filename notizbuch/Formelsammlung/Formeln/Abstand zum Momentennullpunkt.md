---
erzeugt: 3916bb185ceb
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.6.4.4"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.6.4.4

*In der Herleitung: «Abstand zum Momentennullpunkt in x»*

$$
r_{sx} = 0.22 \cdot l_x
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $l_x$ | Spannweite in x | m | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
r_{sx} = 0.22 \cdot l_x = 0.22 \cdot 7\,\mathrm{m} = 1540\,\mathrm{mm}
$$

## Gebraucht von

- [[Breite des Stützstreifens]]
- [[Plattenrotation]]

## Im Code

- [[opencivil.durchstanzen.nachweis#Durchstanzen._rotation|Durchstanzen._rotation]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie stark sich die Platte über der Stütze verdreht, hängt davon ab, wie weit
das negative Moment reicht: bis zum Momentennullpunkt im Abstand $r_s$ von der
Stützenachse. In den Näherungsstufen 1 und 2 wird er aus der Spannweite
geschätzt, mit der grösseren der angrenzenden Spannweiten je Richtung
(4.3.6.4.4). In Stufe 3 kommt $r_s$ aus einer Berechnung nach der
Elastizitätstheorie und wird eingegeben.
