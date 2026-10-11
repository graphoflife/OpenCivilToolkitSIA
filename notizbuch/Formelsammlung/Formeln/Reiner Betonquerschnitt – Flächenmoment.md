---
erzeugt: b133388cfe86
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Reiner Betonquerschnitt: Flächenmoment»*

$$
I_c = \frac{b \cdot \left(h\right)^{3}}{12}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $b$ | Betrachtete Breite (x) | mm | Vorgabe |
| $h$ | Plattendicke | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
I_c = \frac{b \cdot \left(h\right)^{3}}{12} = \frac{1000\,\mathrm{mm} \cdot \left(300\,\mathrm{mm}\right)^{3}}{12} = 2250\,\cdot 10^{6}\,\mathrm{mm}^{4}
$$

## Im Code

- [[opencivil.spannungsanalyse#_herleitung_modul|_herleitung_modul]]

## Themen

- [[Spannung-Dehnung-Analyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das Flächenmoment des Rechtecks $b \times h$, ohne Bewehrung -- der
Vergleichsquerschnitt für den [[Äquivalenter E-Modul über dem Moment|äquivalenten E-Modul]].
Mit ihm rechnet man, wenn man eine Platte als homogenes, elastisches
Bauteil berechnet.
