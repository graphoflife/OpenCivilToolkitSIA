---
erzeugt: 1a28568be63d
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
d_v = d - e_{Einlage}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $d$ | – | mm | [[Statische Höhe]] |
| $e_{Einlage}$ | Höhe der Einlage | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
d_v = d - e_{Einlage} = 165\,\mathrm{mm} - 40\,\mathrm{mm} = 125\,\mathrm{mm}
$$

## Gebraucht von

- [[Querkraftwiderstand ohne Bügel bei M_Ed = 0]]
- [[Querkraftwiderstand ohne Querkraftbewehrung]]

## Im Code

- [[opencivil.nachweis.kennzahlen#Plattenkennzahlen._hoehen|Plattenkennzahlen._hoehen]]
- [[opencivil.nachweis.querkraft#Querkraft._protokoll_fall|Querkraft._protokoll_fall]]

## Themen

- [[Querkraft]]
- [[Kennzahlen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Liegt in der Platte eine Einlage -- ein Leitungsrohr, ein Kanal --, schwächt
sie den Querschnitt dort, wo die Querkraft durch muss. Liegt ihre Höhe
zwischen $h/6$ und $d$, wird die wirksame Höhe um sie vermindert; sonst gilt
die [[Wirksame Höhe (Einlage nicht massgebend)]].
