---
erzeugt: 514f5bbf24f0
art: formel
tags: [formel]
normstelle: "SIA 264:2014, Figur 18"
---
> [!info] Normstelle
> SIA 264:2014, Figur 18

*In der Herleitung: «Rippenbreite, offen: auf halber Höhe der Rippe»*

$$
b_0 = \frac{b_o + b_u}{2}
$$

*In der Herleitung: «Rippenbreite, hinterschnitten: oben, wo die Rippe am schmalsten ist»*

$$
b_0 = b_o
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $b_o$ | Breite einer Rippe oben | mm | Zwischenwert |
| $b_u$ | Breite einer Rippe unten | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
b_0 = \frac{b_o + b_u}{2} = \frac{120\,\mathrm{mm} + 70\,\mathrm{mm}}{2} = 95\,\mathrm{mm}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
b_0 = b_o = 70\,\mathrm{mm}
$$

## Gebraucht von

- [[Querkraftwiderstand einer Blechverbunddecke]]

## Im Code

- [[opencivil.nachweis.qa_blechverbund#KennzahlenBlechQA._form|KennzahlenBlechQA._form]]

## Themen

- [[Blechverbunddecke]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Querkraft tragen in der Decke die Betonrippen; ihre Breite $b_0$ geht
in den [[Querkraftwiderstand einer Blechverbunddecke|Querkraftwiderstand]]
ein. Welche Breite zählt, hängt an der Form der Rippe (Figur 18 der
SIA 264):

- **offen** – die Rippe oben breiter als unten: das Mittel aus beiden
  Breiten, also die Breite auf halber Höhe;
- **hinterschnitten** – unten breiter als oben: die obere Breite, wo die
  Rippe am schmalsten ist.

Welche Form das Blech hat, liest das Werkzeug aus den Massen: ist $b_u$
grösser als $b_o$, ist es hinterschnitten.
