---
erzeugt: 7d4dcabb2dde
art: formel
tags: [formel]
normstelle: "SIA 263:2013, 4.5.1.3, (7); 4.5.1.4, (8); Tabelle 8"
---
> [!info] Normstelle
> SIA 263:2013, 4.5.1.3, (7); 4.5.1.4, (8); Tabelle 8

*In der Herleitung: «Knickwiderstand um y»*

$$
N_{K,y,Rd} = \chi_{K,y} \cdot N_{Rd}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\chi_{K,y}$ | Abminderung beim Knicken | – | [[Abminderungsfaktor beim Knicken und Kippen]] |
| $N_{Rd}$ | Druckwiderstand des Querschnitts | kN | [[Normalkraftwiderstand eines Stahlquerschnitts]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
N_{K,y,Rd} = \chi_{K,y} \cdot N_{Rd} = 0.972 \cdot 5275.5\,\mathrm{kN} = 5127.9\,\mathrm{kN}
$$

## Im Code

- [[opencivil.nachweis.qa_stahl_stabilitaet#_Herleitung.knicken|_Herleitung.knicken]]

## Themen

- [[Knicken und Kippen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Druckkraft, die der Stab um eine Achse trägt: der Druckwiderstand
des Querschnitts, gemindert mit $\chi_K$ (7) – siehe
[[Abminderungsfaktor beim Knicken und Kippen]]. In Klasse 4 ist es der
Widerstand der wirksamen Fläche (5.3.8). Massgebend ist die schwächere
der beiden Achsen; ihr Wert steht in
[[Druck und zweiachsige Biegung im Stab|(50)]].
