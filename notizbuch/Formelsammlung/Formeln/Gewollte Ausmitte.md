---
erzeugt: f30337338021
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
e_{1d} = \left|\frac{M_{Ed,1}}{N_{Ed}}\right|
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $M_{Ed,1}$ | – | kNm | Zwischenwert |
| $N_{Ed}$ | – | kN | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
e_{1d} = \left|\frac{M_{Ed,1}}{N_{Ed}}\right| = \left|\frac{20\,\mathrm{kNm}}{-800\,\mathrm{kN}}\right| = 25\,\mathrm{mm}
$$

## Im Code

- [[opencivil.nachweis.knicken#Knicken|Knicken._protokoll_fall]]

## Themen

- [[Knicken]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ein Moment erster Ordnung, als Ausmitte der Normalkraft geschrieben: wie
weit neben der Achse sie angreifen müsste, um dieses Moment zu erzeugen.
Sie gehört zum System, nicht zur Last -- wächst die Normalkraft, wächst das
Moment mit. So rechnet das Werkzeug auch, wenn es die grösste tragbare
Druckkraft sucht.
