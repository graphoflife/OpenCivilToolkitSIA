---
erzeugt: 028674dd5a6b
art: formel
tags: [formel]
normstelle: "SIA 266:2015, 4.7.1.5, Gl. (27)"
---
> [!info] Normstelle
> SIA 266:2015, 4.7.1.5, Gl. (27)

*In der Herleitung: «Normalkraftniveau des Pfeilers»*

$$
n_d = \frac{N_{xd}}{l_w \cdot t_w \cdot f_{xd}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $N_{xd}$ | Normalkraft am Fuss des Pfeilers | kN | Zwischenwert |
| $l_w$ | Breite des Pfeilers | mm | Zwischenwert |
| $t_w$ | Dicke der Wand | mm | Zwischenwert |
| $f_{xd}$ | Druckfestigkeit der Wand | N/mm² | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
n_d = \frac{N_{xd}}{l_w \cdot t_w \cdot f_{xd}} = \frac{65.6\,\mathrm{kN}}{800\,\mathrm{mm} \cdot 175\,\mathrm{mm} \cdot 2.98\,\mathrm{N}/\mathrm{mm}^{2}} = 0.158
$$

## Im Code

- [[opencivil.mauerwerk.querlast#Normalkraftniveau.stelle|Normalkraftniveau.stelle]]

## Themen

- [[Mauerwerk]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Im Erdbeben rechnet ein Gebäude aus Mauerwerk in der Regel mit dem
Verhaltensbeiwert $q = 1.5$ (SIA 266:2015, 4.7.1.5). Mit $q = 2.0$ wird die
Ersatzkraft um ein Viertel kleiner. Das darf es nur, wenn es im Grundriss
und im Aufriss regelmässig ist nach SIA 261 und jede Wand, die zur
Tragsicherheit zählt, Gl. (27) erfüllt: Die Normalkraft am Fuss ist
höchstens ein Fünftel dessen, was der Querschnitt mit $f_{xd}$ trägt. Eine
wenig gedrückte Wand verformt sich weiter, bevor sie versagt; diese Reserve
steckt im grösseren $q$.

Das Werkzeug prüft Gl. (27) je Pfeiler, mit seiner Breite $l_w$ zwischen
den Öffnungen, in jeder Kombination mit einer Querlast des Erdbebens, bei
der $q = 2.0$ gewählt ist. Die Regelmässigkeit prüft es nicht. Mit
$q = 2.5$ braucht das Mauerwerk ein erhöhtes Verformungsvermögen, das
Versuche an Schubwänden belegen (4.7.2); das sagt ein grauer Hinweis.

Beispiel: Ein Pfeiler aus Kalksandstein im Verband, 800 mm breit und
175 mm dick, mit $f_{xd}$ = 0.85 · 3.5 = 2.975 N/mm², trägt am Fuss
65.6 kN. Mittig trüge er 800 · 175 · 2.975 N = 416.5 kN; $n_d$ =
65.6/416.5 = 0.158, kleiner als 0.20.
