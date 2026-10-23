---
erzeugt: 9de853a589e7
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Bewehrungsmass je Kubikmeter Beton, ohne Bügel»*

$$
\mu_s = \frac{A_{s,tot} \cdot 7850\,\mathrm{kg}/\mathrm{m}^{3}}{A}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $A_{s,tot}$ | Stahlfläche der Bewehrung | mm² | Zwischenwert |
| $A$ | Fläche des Bruttoquerschnitts | mm² | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\mu_s = \frac{A_{s,tot} \cdot 7850\,\mathrm{kg}/\mathrm{m}^{3}}{A} = \frac{1169\,\mathrm{mm}^{2} \cdot 7850\,\mathrm{kg}/\mathrm{m}^{3}}{180000\,\mathrm{mm}^{2}} = 51\,\mathrm{kg}/\mathrm{m}^{3}
$$

## Im Code

- [[opencivil.nachweis.qa_kennzahlen#KennzahlenQA|KennzahlenQA._bewehrungsmass]]

## Themen

- [[Kennzahlen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie viel Stahl im Beton steckt, als Masse je Kubikmeter: die Stahlfläche
aller Bewehrung des gezeichneten Querschnitts, mal der Dichte des Stahls von
7850 kg/m³, geteilt durch die Fläche des Querschnitts -- die Länge des
Bauteils kürzt sich heraus. Wie bei der Platte ohne Bügel. Eine Kennzahl für
Menge und Kosten, kein Nachweis.
