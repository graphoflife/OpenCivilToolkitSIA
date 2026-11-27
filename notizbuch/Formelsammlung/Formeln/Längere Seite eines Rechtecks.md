---
erzeugt: b16fbcc4dd08
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Längere Seite, «Balken 300×500» (Rechteck)»*

$$
s_{\text{Q1}} = \max\left(b_{\text{Q1}}, h_{\text{Q1}}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $b_{\text{Q1}}$ | Breite, Balken 300×500 | mm | Vorgabe |
| $h_{\text{Q1}}$ | Höhe, Balken 300×500 | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
s_{\text{Q1}} = \max\left(b_{\text{Q1}}, h_{\text{Q1}}\right) = \max\left(300\,\mathrm{mm}, 500\,\mathrm{mm}\right) = 500\,\mathrm{mm}
$$

## Gebraucht von

- [[Torsionsträgheitsmoment eines Rechtecks]]

## Im Code

- [[opencivil.stabwerk.querschnitte#_seiten|_seiten]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das Gegenstück zur [[Kürzere Seite eines Rechtecks|kürzeren Seite]]: $s$ ist
die längere Seite eines Rechtecks, für die Näherung des
[[Torsionsträgheitsmoment eines Rechtecks|Torsionsträgheitsmoments]]. Sie geht
nur einfach ein – ein doppelt so langes Brett ist doppelt so steif gegen
Verdrillen, ein doppelt so dickes achtmal.
