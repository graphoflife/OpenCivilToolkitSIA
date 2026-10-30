---
erzeugt: 37bc6f30be4a
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.6.2.3"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.6.2.3

*In der Herleitung: «Wirksamer Umfang des Schnitts um den Stahlpilz, mit k\_e von innen»*

$$
u_{P} = k_e \cdot u_{P,red}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $k_e$ | – | – | Zwischenwert |
| $u_{P,red}$ | – | mm | [[Schnitt um den Stahlpilz ohne das, was nicht zählt]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
u_{P} = k_e \cdot u_{P,red} = 0.9 \cdot 2913\,\mathrm{mm} = 2622\,\mathrm{mm}
$$

## Im Code

- [[opencivil.durchstanzen.mit_bewehrung#_umfang|_umfang]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der [[Schnitt um den Stahlpilz ohne das, was nicht zählt]], mit $k_e$
gemindert wie der Schnitt um die Stütze. Mit ihm rechnet der Widerstand um
den Pilz ([[Durchstanzwiderstand ohne Durchstanzbewehrung]]), und wo der
nicht reicht, die Durchstanzbewehrung um den Pilz.
