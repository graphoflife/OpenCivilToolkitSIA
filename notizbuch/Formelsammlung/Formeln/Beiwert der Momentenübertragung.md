---
erzeugt: 1d5be6d54368
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.6.2.4, (57)"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.6.2.4, (57)

$$
k_e = \frac{1}{1 + \frac{e_u}{b}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $e_u$ | – | mm | Zwischenwert |
| $b$ | – | mm | [[Durchmesser des flächengleichen Kreises]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
k_e = \frac{1}{1 + \frac{e_u}{b}} = \frac{1}{1 + \frac{1\,\mathrm{mm}}{734\,\mathrm{mm}}} = 0.999
$$

## Gebraucht von

- [[Beitrag der Durchstanzbewehrung]]
- [[Durchstanzbewehrung an der Fliessgrenze]]
- [[Wirksamer Umfang des äusseren Nachweisschnitts]]
- [[Wirksamer Umfang des Nachweisschnitts]]

## Im Code

- [[opencivil.durchstanzen.nachweis#Durchstanzen._k_e|Durchstanzen._k_e]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Leitet die Stütze ein Moment in die Platte, ist die Querkraft längs des
Nachweisschnitts ungleich verteilt. $k_e$ mindert dafür den Umfang
([[Wirksamer Umfang des Nachweisschnitts]]). $e_u$ ist der Abstand der
Resultierenden der Auflagerkraft vom Schwerpunkt der zählenden Teile des
Schnitts, $b$ der Durchmesser des Kreises mit der Fläche innerhalb des
Schnitts ([[Durchmesser des flächengleichen Kreises]]).

Für regelmässig gestützte Flachdecken darf $k_e$ genähert werden
(4.3.6.2.5): 0.9 für Innenstützen, 0.7 für Randstützen und Innenstützen mit
grossen Aussparungen, 0.65 für Eckstützen, 0.75 für Wandenden und Wandecken.
