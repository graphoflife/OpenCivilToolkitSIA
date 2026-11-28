---
erzeugt: 4e07ee3a5063
art: formel
tags: [formel]
normstelle: "SIA 266:2015, 4.3.2.2, Gl. (13), Figur 7 und 8"
---
> [!info] Normstelle
> SIA 266:2015, 4.3.2.2, Gl. (13), Figur 7 und 8

*In der Herleitung: «Neigung der Druckstrebe gegen die Lotrechte, in Grad»*

$$
\alpha = \arctan\frac{V_d}{N_{xd}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $V_d$ | Querkraft in der Wandebene, Betrag | kN | Zwischenwert |
| $N_{xd}$ | Normalkraft am Fuss des Pfeilers | kN | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\alpha = \arctan\frac{V_d}{N_{xd}} = \arctan\frac{7\,\mathrm{kN}}{51.1\,\mathrm{kN}} = 7.8{}^{\circ}
$$

## Gebraucht von

- [[Widerstand der Druckstrebe in einem Pfeiler]]

## Im Code

- [[opencivil.mauerwerk.schub#Schub.gedrueckt|Schub.gedrueckt]]

## Themen

- [[Mauerwerk]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Querkraft und Normalkraft setzen sich im Pfeiler zu einer geneigten
Druckstrebe zusammen; $\alpha$ ist ihre Neigung gegen die Lotrechte, also
gegen die Normale der Lagerfugen. Wie viel das Mauerwerk in dieser Richtung
trägt, zeigt Figur 7 (4.3.2.1): lotrecht $f_{xd}$, schon wenig geneigt nur
noch $f_{yd}$, und flacher als $\arctan \mu_d$ gleiten die Fugen. Darum
rechnet die Strebe mit $f_{yd}$, und das Gleiten prüft Gl. (14) für sich.
