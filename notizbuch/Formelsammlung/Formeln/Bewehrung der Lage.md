---
erzeugt: c09ce5757d12
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
A_{s,2,x} = A_{s,2,x,g} + A_{s,2,x,z}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $A_{s,2,x,g}$ | Bewehrungsquerschnitt 2. Lage Grundbewehrung | mm² | Zwischenwert |
| $A_{s,2,x,z}$ | Bewehrungsquerschnitt 2. Lage Zulage | mm² | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
A_{s,2,x} = A_{s,2,x,g} + A_{s,2,x,z} = 1696\,\mathrm{mm}^{2} + 754\,\mathrm{mm}^{2} = 2450\,\mathrm{mm}^{2}
$$

## Gebraucht von

- [[Aufnehmbare Risskraft]]
- [[Aufnehmbares Moment der Bewehrung]]
- [[Druckzonenhöhe bei reiner Biegung]]
- [[Hilfsgrösse der Nulllinie]]

## Im Code

- [[opencivil.querschnitt.platte#protokoll_lage|protokoll_lage]]

## Themen

- [[Duktilität]]
- [[Zwängung auf Normalkraft]]
- [[Zwängung auf Biegung]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Grundbewehrung und Zulage einer Lage, zusammengezählt: sie fliessen gemeinsam
und wirken als ein Querschnitt. In ihrem
[[Schwerpunkt der zusammengefassten Lage|Schwerpunkt]] zählen sie als eine
Lage.
