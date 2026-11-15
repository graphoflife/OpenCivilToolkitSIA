---
erzeugt: c9a2ddb161d2
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Kürzere Seite, «Balken 300×500» (Rechteck)»*

$$
t_{\text{Q1}} = \min\left(b_{\text{Q1}}, h_{\text{Q1}}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $b_{\text{Q1}}$ | Breite, Balken 300×500 | mm | Vorgabe |
| $h_{\text{Q1}}$ | Höhe, Balken 300×500 | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
t_{\text{Q1}} = \min\left(b_{\text{Q1}}, h_{\text{Q1}}\right) = \min\left(300\,\mathrm{mm}, 500\,\mathrm{mm}\right) = 300\,\mathrm{mm}
$$

## Gebraucht von

- [[Torsionsträgheitsmoment eines Rechtecks]]

## Im Code

- [[opencivil.stabwerk.querschnitte#_seiten|_seiten]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Näherung für das [[Torsionsträgheitsmoment eines Rechtecks]] fragt nicht
nach Breite und Höhe, sondern nach der dünnen und der langen Seite: ein
liegendes Brett trägt die Torsion wie ein stehendes. $t$ ist die kürzere
Seite; sie geht in der dritten Potenz ein.
