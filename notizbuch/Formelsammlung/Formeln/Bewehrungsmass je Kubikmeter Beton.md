---
erzeugt: 4d3dc109fc96
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
\mu_s = \frac{A_{s,tot} \cdot 7850\,\mathrm{kg}/\mathrm{m}^{3}}{b \cdot h}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $A_{s,tot}$ | – | mm² | Zwischenwert |
| $b$ | Betrachtete Breite (x) | mm | Vorgabe |
| $h$ | Plattendicke | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\mu_s = \frac{A_{s,tot} \cdot 7850\,\mathrm{kg}/\mathrm{m}^{3}}{b \cdot h} = \frac{4712\,\mathrm{mm}^{2} \cdot 7850\,\mathrm{kg}/\mathrm{m}^{3}}{1000\,\mathrm{mm} \cdot 300\,\mathrm{mm}} = 123\,\mathrm{kg}/\mathrm{m}^{3}
$$

## Im Code

- [[opencivil.querschnitt.platte#Lagenaufbau._kennzahlen|Lagenaufbau._kennzahlen]]

## Themen

- [[Querschnitt]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie viel Stahl im Beton steckt, als Masse je Kubikmeter: die ganze
Bewehrung der Platte, mal der Dichte des Stahls von 7850 kg/m³, geteilt
durch das Volumen des Streifens. Eine Kennzahl für Menge und Kosten, kein
Nachweis -- gewöhnliche Decken liegen etwa zwischen 60 und 150 kg/m³.
