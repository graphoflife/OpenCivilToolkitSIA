---
erzeugt: 72e2c8175f20
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 3.3.2.2, Tabelle 7"
---
> [!info] Normstelle
> SIA 262:2025, 3.3.2.2, Tabelle 7

*In der Herleitung: «Spannglied 1: 4 × Litze ⌀15.7 aus Y1860»*

$$
A_{p,1} = n \cdot a_p
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $n$ | Anzahl der Drähte, Litzen oder Stäbe | – | Zwischenwert |
| $a_p$ | Querschnitt eines Drahts, einer Litze oder eines Stabs | mm² | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
A_{p,1} = n \cdot a_p = 4 \cdot 150\,\mathrm{mm}^{2} = 600\,\mathrm{mm}^{2}
$$

## Gebraucht von

- [[Spannkraft eines Spannglieds]]

## Im Code

- [[opencivil.querschnitt.spannglieder#Spannglieder._glied|Spannglieder._glied]]

## Themen

- [[Querschnittsanalyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ein Spannglied besteht aus $n$ gleichen Drähten, Litzen oder Stäben. Die
Fläche eines Stücks ist keine freie Zahl: sie steht je Erzeugnis in
Tabelle 7 (SIA 262:2025, 3.3.2.2). Eine Litze ⌀15.7 hat 150 mm² und nicht
$\pi \cdot 15.7^2/4$ = 194 mm², denn sie ist aus sieben Drähten verseilt.
Darum wählt man im Werkzeug einen Durchmesser unter den Erzeugnissen der
Sorte, und die Fläche kommt aus der Tabelle. Gibt es den Durchmesser in
der Sorte nicht – etwa nach dem Wechsel zu Y1030, das es nur in Stäben
gibt –, fehlt die Wahl noch: das Glied rechnet nicht und sagt es grau.
