---
erzeugt: 74ccdc423eca
art: formel
tags: [formel]
normstelle: "SIA 266:2015, 4.2.1.1, Gl. (3)"
---
> [!info] Normstelle
> SIA 266:2015, 4.2.1.1, Gl. (3)

$$
f_{yd,v} = \frac{f_{yk,v}}{\gamma_M}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $f_{yk,v}$ | Druckfestigkeit senkrecht zu den Stossfugen, vollfugig vermauert, kennzeichnend | N/mm² | Vorgabe |
| $\gamma_M$ | Widerstandsbeiwert des Mauerwerks | – | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
f_{yd,v} = \frac{f_{yk,v}}{\gamma_M} = \frac{3.2\,\mathrm{N}/\mathrm{mm}^{2}}{2} = 1.6\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Im Code

- [[opencivil.material.mauerwerk#_durch_gamma|_durch_gamma]]

## Themen

- [[Mauerwerk]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Vollfugig heisst: auch die Stossfugen sind ganz mit Mörtel gefüllt (SIA
266:2015, 1.1). Dann drücken die Steine auch längs der Wand über den Mörtel
aufeinander, und $f_{yd}$ ist grösser – bei Kalksandstein 1.6 statt 1.1
N/mm². Tabelle 7 nennt beide Zeilen. Wie die Stossfugen gefüllt sind, wählt
die Wand; ihre Herleitung sagt, mit welcher Zeile sie rechnet.

Wie bei [[Bemessungswert der Druckfestigkeit senkrecht zu den Stossfugen]]
ist $f_{yk,v} = \gamma_M \cdot f_{yd,v}$ gesetzt, damit die Formel die Zahl
der Tabelle gibt.
