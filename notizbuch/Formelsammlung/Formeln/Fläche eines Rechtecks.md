---
erzeugt: 812827823edd
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Querschnittsfläche, «Stütze 300×300» (Rechteck)»*

$$
A_{\text{Q1}} = b_{\text{Q1}} \cdot h_{\text{Q1}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $b_{\text{Q1}}$ | Breite, Stütze 300×300 | mm | Vorgabe |
| $h_{\text{Q1}}$ | Höhe, Stütze 300×300 | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
A_{\text{Q1}} = b_{\text{Q1}} \cdot h_{\text{Q1}} = 300\,\mathrm{mm} \cdot 300\,\mathrm{mm} = 90000\,\mathrm{mm}^{2}
$$

## Gebraucht von

- [[Dehnsteifigkeit]]

## Im Code

- [[opencivil.spannungsanalyse#Loeserpaar.herleitung_bezug|Loeserpaar.herleitung_bezug]]
- [[opencivil.stabwerk.querschnitte]]

## Themen

- [[Stabquerschnitte]]
- [[Spannung-Dehnung-Analyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Fläche des Rechtecks $b \times h$. Im Balkensystem ist es die Fläche
eines Stabs mit Rechteckquerschnitt -- auch eines Plattenstreifens der Breite
$b$ und der Dicke $h$ -- und sie geht über die [[Dehnsteifigkeit]] in die
Rechnung ein.

In der Spannung-Dehnung-Analyse ist es der reine Betonquerschnitt ohne
Bewehrung: der Vergleichsquerschnitt für den
[[Äquivalenter E-Modul über der Normalkraft|äquivalenten E-Modul unter Normalkraft]].
