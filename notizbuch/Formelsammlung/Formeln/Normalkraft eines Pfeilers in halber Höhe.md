---
erzeugt: 3f82b3135c60
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Normalkraft in halber Höhe: die Lasten am Kopf und die Hälfte des Eigengewichts, das bis zum Fuss dazukommt»*

$$
N_m = N_{Ld} + \frac{N_{xd} - N_{Ld}}{2}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $N_{Ld}$ | Normalkraft aus den Lasten am Kopf, ohne Eigengewicht | kN | Zwischenwert |
| $N_{xd}$ | Normalkraft am Fuss des Pfeilers | kN | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
N_m = N_{Ld} + \frac{N_{xd} - N_{Ld}}{2} = 43.4\,\mathrm{kN} + \frac{51.1\,\mathrm{kN} - 43.4\,\mathrm{kN}}{2} = 47.2\,\mathrm{kN}
$$

## Im Code

- [[opencivil.mauerwerk.querlast#Querlastnachweis._normalkraft|Querlastnachweis._normalkraft]]

## Themen

- [[Mauerwerk]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das lotrechte Gewölbe trägt Querlast mit der Normalkraft der Wand: Je
stärker sie gedrückt ist, desto weiter darf die Querlast die Druckkraft zur
Seite schieben. Die Rechnung nach Figur 3 hält die Normalkraft über die
ganze Höhe gleich; in Wirklichkeit wächst sie von oben nach unten um das
Eigengewicht der Wand.

Beim Nachweis der Normalkraft nimmt das Werkzeug darum die Kraft am Fuss:
Dort ist mehr Druck ungünstig. Unter Querlast ist es umgekehrt, Druck hält
das Gewölbe zusammen, und die Kraft am Fuss überschätzte, was es trägt.
Hier nimmt das Werkzeug die Kraft in halber Höhe, wo die Querlast eine
gelenkig gehaltene Wand am stärksten biegt: die Lasten am Kopf und die
Hälfte des Eigengewichts darunter – nach Vorgabe, nicht nachgeschlagen.

Beispiel: Am Kopf eines Pfeilers drücken die Lasten mit 43.35 kN, am Fuss
sind es mit dem Eigengewicht 51.10 kN. In halber Höhe rechnet das Gewölbe
also mit 43.35 + 7.75/2 = 47.23 kN.
