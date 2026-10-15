---
erzeugt: df391d3efa4b
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Flächenträgheitsmoment, «Stütze 300×300» (Rechteck)»*

$$
I_{\text{Q1}} = \frac{b_{\text{Q1}} \cdot \left(h_{\text{Q1}}\right)^{3}}{12}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $b_{\text{Q1}}$ | Breite, Stütze 300×300 | mm | Vorgabe |
| $h_{\text{Q1}}$ | Höhe, Stütze 300×300 | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
I_{\text{Q1}} = \frac{b_{\text{Q1}} \cdot \left(h_{\text{Q1}}\right)^{3}}{12} = \frac{300\,\mathrm{mm} \cdot \left(300\,\mathrm{mm}\right)^{3}}{12} = 675\,\cdot 10^{6}\,\mathrm{mm}^{4}
$$

## Gebraucht von

- [[Biegesteifigkeit]]

## Im Code

- [[opencivil.spannungsanalyse#Loeserpaar.herleitung_bezug|Loeserpaar.herleitung_bezug]]
- [[opencivil.stabwerk.querschnitte]]

## Themen

- [[Stabquerschnitte]]
- [[Spannung-Dehnung-Analyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das Flächenträgheitsmoment des Rechtecks $b \times h$ um seine Schwerachse
parallel zu $b$, also $\int z^2 \, \mathrm{d}A$ über die Höhe. Es wächst mit
der dritten Potenz der Höhe: ein doppelt so hoher Balken ist achtmal so steif,
ein doppelt so breiter nur doppelt.

Im Balkensystem geht es über die [[Biegesteifigkeit]] in die Rechnung ein. In
der Spannung-Dehnung-Analyse ist es der reine Betonquerschnitt ohne
Bewehrung, der Vergleichsquerschnitt für den
[[Äquivalenter E-Modul über dem Moment|äquivalenten E-Modul]] -- mit ihm
rechnet man, wenn man eine Platte als homogenes, elastisches Bauteil
berechnet.
