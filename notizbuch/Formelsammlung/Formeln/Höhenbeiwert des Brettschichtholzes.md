---
erzeugt: 4b9fa2f2442c
art: formel
tags: [formel]
normstelle: "SIA 265:2012, 3.4.2.3, (5)"
---
> [!info] Normstelle
> SIA 265:2012, 3.4.2.3, (5)

*In der Herleitung: «Höhenbeiwert unter 600 mm Höhe, für die Biegung um y»*

$$
k_h = \min\left(\left(\frac{600\ \mathrm{mm}}{h}\right)^{0.1};\ 1.1\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $h$ | Höhe des Brettschichtholzes, in z | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
k_h = \min\left(\left(\frac{600\ \mathrm{mm}}{h}\right)^{0.1};\ 1.1\right) = \min\left(\left(\frac{600\ \mathrm{mm}}{400\,\mathrm{mm}}\right)^{0.1};\ 1.1\right) = 1.041
$$

## Gebraucht von

- [[Biegewiderstand des Brettschichtholzes]]

## Im Code

- [[opencivil.nachweis.qa_holz_werte#HolzwerteQA|HolzwerteQA._biegung]]

## Themen

- [[Holzquerschnitt]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ein grosser Holzquerschnitt ist im Mittel schwächer als ein kleiner: in
mehr Holz liegt eher eine schwache Stelle in der Zugzone. Die
Biegefestigkeit von Tabelle 7 gilt für 600 mm Höhe; ein niedrigerer Träger
aus Brettschichtholz darf mehr, höchstens 10 %.

Das Werkzeug nimmt an, dass die Lamellen parallel zu y liegen: $k_h$ gilt
dann für die Biegung um y, mit der Höhe in z – nach Vorgabe, nicht
nachgeschlagen. Den Systembeiwert $k_{sys}$ für die Biegung um z nimmt es
nicht.
