---
erzeugt: 5d71958cf41d
art: formel
tags: [formel]
normstelle: "SIA 263:2013, 4.2.3.2, Figur 3"
---
> [!info] Normstelle
> SIA 263:2013, 4.2.3.2, Figur 3

*In der Herleitung: «Ersatzimperfektion um y, Kurve a, Spalte EE»*

$$
w_{0,y} = \frac{L_{K,y}}{k_{y}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $L_{K,y}$ | Knicklänge | mm | Zwischenwert |
| $k_{y}$ | Nenner der Ersatzimperfektion | – | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
w_{0,y} = \frac{L_{K,y}}{k_{y}} = \frac{3000\,\mathrm{mm}}{300} = 10\,\mathrm{mm}
$$

## Im Code

- [[opencivil.nachweis.qa_stahl_stabilitaet#_Herleitung.gleichungen_62|_Herleitung.gleichungen_62]]

## Themen

- [[Knicken und Kippen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Statt Krümmung, Schiefe und Eigenspannungen einzeln zu erfassen, denkt
man sich den Stab in der Mitte um $w_0$ vorgekrümmt. Die Druckkraft
wirkt an diesem Hebelarm und erzeugt ein Moment, das sie am geraden Stab
nicht hätte. Wie gross $w_0$ ist, hängt an der Knickspannungskurve: ein
Bruchteil der Länge, von 1/300 bei Kurve a bis 1/150 bei Kurve d
(Figur 3, Spalte EE).

Das Werkzeug nimmt dafür die Knicklänge als Länge des Stabs.
