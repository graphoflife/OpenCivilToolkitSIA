---
erzeugt: 3e774cd66545
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Flächenträgheitsmoment um z, «Balken 300×500» (Rechteck)»*

$$
I_{z} = \frac{h_{\text{Q1}} \cdot \left(b_{\text{Q1}}\right)^{3}}{12}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $h_{\text{Q1}}$ | Höhe, Balken 300×500 | mm | Vorgabe |
| $b_{\text{Q1}}$ | Breite, Balken 300×500 | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
I_{z,\text{Q1}} = \frac{h_{\text{Q1}} \cdot \left(b_{\text{Q1}}\right)^{3}}{12} = \frac{500\,\mathrm{mm} \cdot \left(300\,\mathrm{mm}\right)^{3}}{12} = 1125\,\cdot 10^{6}\,\mathrm{mm}^{4}
$$

## Gebraucht von

- [[Biegesteifigkeit um z]]

## Im Code

- [[opencivil.stabwerk.querschnitte]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Dasselbe Rechteck wie beim [[Flächenträgheitsmoment eines Rechtecks]], um
die andere Schwerachse, die parallel zu $h$: $\int y^2 \, \mathrm{d}A$ über
die Breite. Breite und Höhe tauschen die Rollen, jetzt geht die Breite in
der dritten Potenz ein. Ein Balken 300×500 hat um $z$ darum nur gut ein
Drittel des Werts um $y$: $(300/500)^2 = 0.36$.
