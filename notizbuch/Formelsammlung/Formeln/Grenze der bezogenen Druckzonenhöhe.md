---
erzeugt: 1e4a8d6d55b7
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.1.4.2.5"
---
> [!info] Normstelle
> SIA 262:2025, 4.1.4.2.5

$$
\left(x/d\right)_{max} = k \cdot \frac{435\,\mathrm{N/mm^2}}{f_{yd}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $k$ | – | – | Zwischenwert |
| $f_{yd}$ | Bemessungswert der Fliessgrenze | N/mm² | [[Bemessungswert der Fliessgrenze]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\left(x/d\right)_{max} = k \cdot \frac{435\,\mathrm{N/mm^2}}{f_{yd}} = 0.35 \cdot \frac{435\,\mathrm{N/mm^2}}{435\,\mathrm{N}/\mathrm{mm}^{2}} = 0.35
$$

## Im Code

- [[opencivil.nachweis.duktilitaet#protokoll_grenze|protokoll_grenze]]

## Themen

- [[Duktilität]]
- [[Duktilität je Richtung]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie klein die Druckzone bleiben muss, damit der Stahl fliesst, lange bevor
der Beton bricht. Ein festerer Stahl dehnt sich bis zum Fliessen mehr; damit
er trotzdem vor dem Beton nachgibt, muss die Nulllinie näher am gedrückten
Rand liegen. Darum steht $f_{yd}$ im Nenner: mit der Vorgabe $k = 0.35$ ist
die Grenze bei B500 ($f_{yd} = 435\,\mathrm{N/mm^2}$) 0.35, bei B700B
($f_{yd} = 609\,\mathrm{N/mm^2}$) 0.25. Was die Grenze voraussetzt, steht
bei der [[Bedingung der Duktilität]].
