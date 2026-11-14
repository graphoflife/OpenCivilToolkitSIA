---
erzeugt: fba49d28473e
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.3.2.9"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.3.2.9

$$
d_v = d - e_{Einlage}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $d$ | – | mm | [[Statische Höhe]] |
| $e_{Einlage}$ | Grösstes Mass der Einlage (Breite oder Höhe) | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
d_v = d - e_{Einlage} = 165\,\mathrm{mm} - 40\,\mathrm{mm} = 125\,\mathrm{mm}
$$

## Gebraucht von

- [[Querkraftwiderstand ohne Bügel bei M_Ed = 0]]
- [[Querkraftwiderstand ohne Querkraftbewehrung]]

## Im Code

- [[opencivil.nachweis.querkraft#protokoll_hoehen|protokoll_hoehen]]

## Themen

- [[Querkraft]]
- [[Kennzahlen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Liegt in der Platte eine Einlage -- ein Leitungsrohr, ein Kanal --, schwächt
sie den Querschnitt dort, wo die Querkraft durch muss. Es zählt ihr grösstes
Mass, Breite oder Höhe. Ist es grösser als ein Sechstel der statischen Höhe,
wird $d$ um dieses Mass vermindert; sonst gilt die
[[Wirksame Höhe ohne Abzug]].

Beispiel mit $d = 248\,\mathrm{mm}$, also $d/6 = 41.3\,\mathrm{mm}$: ein Rohr
⌀40 stört nicht, eines mit ⌀45 vermindert $d_v$ auf 203 mm.

Eine obere Grenze gibt es nicht. Reicht die Einlage über die ganze
statische Höhe, bleibt ohne Bügel kein Widerstand.
