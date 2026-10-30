---
erzeugt: 9f5aa7ddba23
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.6.2.1"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.6.2.1

$$
d = \frac{d_x + d_y}{2}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $d_x$ | – | mm | [[Statische Höhe der äusseren Lage]] |
| $d_y$ | – | mm | [[Statische Höhe der inneren Lage]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
d = \frac{d_x + d_y}{2} = \frac{242\,\mathrm{mm} + 226\,\mathrm{mm}}{2} = 234\,\mathrm{mm}
$$

## Gebraucht von

- [[Beiwert k_r]]
- [[Plattenrotation]]
- [[Spannung in der Durchstanzbewehrung]]
- [[Wirksame statische Höhe im äusseren Nachweisschnitt]]

## Im Code

- [[opencivil.durchstanzen.nachweis#Durchstanzen._statische_hoehe|Durchstanzen._statische_hoehe]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Über der Stütze kreuzen sich zwei Lagen der Zugbewehrung; die äussere hat die
grössere statische Höhe ([[Statische Höhe der äusseren Lage]],
[[Statische Höhe der inneren Lage]]). Für das Durchstanzen zählt ihr Mittel
(4.3.6.2.1).
