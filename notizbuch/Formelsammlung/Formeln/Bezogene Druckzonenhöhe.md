---
erzeugt: 4f6971dced7c
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.1.4.2.5"
---
> [!info] Normstelle
> SIA 262:2025, 4.1.4.2.5

$$
\left(x/d\right)_{2} = \frac{x}{d_{2,x}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $x$ | – | mm | [[Druckzonenhöhe bei reiner Biegung]] |
| $d_{2,x}$ | – | mm | [[Statische Höhe]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\left(x/d\right)_{2} = \frac{x}{d_{2,x}} = \frac{62.7\,\mathrm{mm}}{248.1\,\mathrm{mm}} = 0.253 \quad \le \quad \left(x/d\right)_{max} = 0.35 \quad \Rightarrow \quad \text{erfüllt}
$$

## Im Code

- [[opencivil.nachweis.duktilitaet#Duktilitaet._protokoll_lage|Duktilitaet._protokoll_lage]]

## Themen

- [[Duktilität]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Druckzonenhöhe im Verhältnis zur statischen Höhe der Lage. Über die
Ebenheit des Querschnitts ist sie mit den Dehnungen verknüpft: bei
Randstauchung $\varepsilon_{cu}$ ist die Stahldehnung
$\varepsilon_{cu}\,(1 - x/d)/(x/d)$. Ein kleines $x/d$ heisst grosse
Stahldehnung, also viel Fliessen vor dem Bruch -- deshalb die Grenze in der
[[Bedingung der Duktilität]].
