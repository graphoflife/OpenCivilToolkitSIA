---
erzeugt: 78ffb5f7efe1
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.6.2.3, Figur 23b und c"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.6.2.3, Figur 23b und c

*In der Herleitung: «Nachweisschnitt um die Wandecke: je 1.5·d\_v entlang der Wände»*

$$
u_0 = 3 \cdot d_v + \frac{\pi \cdot d_v}{4}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $d_v$ | – | mm | [[Wirksame Höhe ohne Abzug]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
u_0 = 3 \cdot d_v + \frac{\pi \cdot d_v}{4} = 3 \cdot 234\,\mathrm{mm} + \frac{\pi \cdot 234\,\mathrm{mm}}{4} = 886\,\mathrm{mm}
$$

## Gebraucht von

- [[Nachweisschnitt ohne das, was nicht zählt]]

## Im Code

- [[opencivil.durchstanzen.nachweis#Durchstanzen._nachweisschnitt|Durchstanzen._nachweisschnitt]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

An der äusseren Ecke zweier Wände läuft der Schnitt im Abstand $d_v/2$ um die
Ecke und zählt entlang jeder Wand 1.5·d_v (Figur 23c): zusammen $3 \cdot d_v$
längs der Wände und ein Viertelkreis um die Ecke.
