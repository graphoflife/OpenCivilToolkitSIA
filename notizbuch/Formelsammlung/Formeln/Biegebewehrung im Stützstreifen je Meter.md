---
erzeugt: 3f1103c7112c
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Bewehrung in x je Meter»*

$$
a_{s,x} = \frac{\pi \cdot \varnothing_x^{2}}{4 \cdot s_x}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\varnothing_x$ | Stabdurchmesser in x | mm | Vorgabe |
| $s_x$ | Stababstand in x | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
a_{s,x} = \frac{\pi \cdot \varnothing_x^{2}}{4 \cdot s_x} = \frac{\pi \cdot \left(16\,\mathrm{mm}\right)^{2}}{4 \cdot 150\,\mathrm{mm}} = 1340\,\mathrm{mm}^{2}/\mathrm{m}
$$

## Gebraucht von

- [[Biegewiderstand im Stützstreifen]]
- [[Druckzonenhöhe im Stützstreifen]]

## Im Code

- [[opencivil.durchstanzen.nachweis#Durchstanzen._m_Rd|Durchstanzen._m_Rd]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Querschnittsfläche einer Lage der Biegebewehrung je Meter Breite, aus
Durchmesser und Abstand der Stäbe. Sie bestimmt den
[[Biegewiderstand im Stützstreifen]].
