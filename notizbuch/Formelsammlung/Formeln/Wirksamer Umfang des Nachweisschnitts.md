---
erzeugt: 2e5ec437f627
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

- [[opencivil.durchstanzen.herleitung#wirksam|wirksam]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Umfang, mit dem der Widerstand rechnet: der
[[Nachweisschnitt ohne das, was nicht zählt]], um
[[Beiwert der Momentenübertragung|k_e]] gemindert. So geht eine ungleich
verteilte Querkraft als kürzerer Schnitt ein.

Der äussere Schnitt um die Anker und der Schnitt um einen Stahlpilz werden
mit dem $k_e$ des Schnitts um die Stütze gemindert. Aus der Näherung ist es
dasselbe; aus der Exzentrizität wäre es aussen grösser, der Wert von innen
liegt auf der sicheren Seite.
