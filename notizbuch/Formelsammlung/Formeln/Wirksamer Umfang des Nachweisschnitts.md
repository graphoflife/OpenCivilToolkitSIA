---
erzeugt: dd1eb1bd1bfc
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.6.2.3"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.6.2.3

$$
u = k_e \cdot u_{red}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $k_e$ | – | – | Zwischenwert, [[Beiwert der Momentenübertragung]] |
| $u_{red}$ | – | mm | [[Nachweisschnitt ohne das, was nicht zählt]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
u = k_e \cdot u_{red} = 0.9 \cdot 2335\,\mathrm{mm} = 2102\,\mathrm{mm}
$$

## Gebraucht von

- [[Durchstanzwiderstand ohne Durchstanzbewehrung]]
- [[Widerstand der ersten Betondruckdiagonale]]

## Im Code

- [[opencivil.durchstanzen.nachweis#Durchstanzen.pruefe|Durchstanzen.pruefe]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Umfang, mit dem der Widerstand rechnet: der
[[Nachweisschnitt ohne das, was nicht zählt]], um
[[Beiwert der Momentenübertragung|k_e]] gemindert. So geht eine ungleich
verteilte Querkraft als kürzerer Schnitt ein.
