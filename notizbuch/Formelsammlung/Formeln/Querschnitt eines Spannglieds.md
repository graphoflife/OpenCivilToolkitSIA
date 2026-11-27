---
erzeugt: d7da5468b6c8
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

- [[Grösste Kraft eines geneigten Spannglieds]]
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

Seit 2026-11-27 lässt sich die Fläche auch eingeben, mit dem Schalter
«Menge»: etwa für ein Glied aus zwölf Litzen, 1800 mm², oder ein
Erzeugnis, das die Tabelle nicht führt. Dann zählt nur noch die Art, denn
an ihr hängt der Modul: 195 000 N/mm² für Litzen, 200 000 für Drähte und
Stäbe (SIA 262:2025, 3.3.2.4.1 und 3.3.2.4.2). Auch die Art muss es in der
Sorte geben; sonst fehlt die Wahl wie beim Durchmesser.
