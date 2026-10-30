---
erzeugt: 2deeb86a055f
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.6.2.3, Figur 23b und c"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.6.2.3, Figur 23b und c

*In der Herleitung: «Nachweisschnitt um das Wandende: 1.5·d\_v entlang der Wand»*

$$
u_0 = t + 3 \cdot d_v + \frac{\pi \cdot d_v}{2}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $t$ | Dicke der Wand | mm | Vorgabe |
| $d_v$ | – | mm | [[Wirksame Höhe ohne Abzug]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
u_0 = t + 3 \cdot d_v + \frac{\pi \cdot d_v}{2} = 250\,\mathrm{mm} + 3 \cdot 234\,\mathrm{mm} + \frac{\pi \cdot 234\,\mathrm{mm}}{2} = 1320\,\mathrm{mm}
$$

## Gebraucht von

- [[Nachweisschnitt ohne das, was nicht zählt]]

## Im Code

- [[opencivil.durchstanzen.nachweis#Durchstanzen._nachweisschnitt|Durchstanzen._nachweisschnitt]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Am Ende einer tragenden Wand sammelt sich die Querkraft um das Ende. Der
Schnitt läuft im Abstand $d_v/2$ um die Stirn und zählt entlang der Wand je
1.5·d_v (Figur 23b). Zusammen sind das die Wanddicke $t$, zweimal
$1.5 \cdot d_v$ längs der Wand und zwei Viertelkreise.
