---
erzeugt: 327fcabbced9
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

Mit den Zahlen aus dem Beispielprojekt:

$$
A_{s,2,x} = A_{s,2,x,g} + A_{s,2,x,z} = 1696\,\mathrm{mm}^{2} + 754\,\mathrm{mm}^{2} = 2450\,\mathrm{mm}^{2}
$$

## Gebraucht von

- [[Bewehrungsgehalt]]
- [[Schwerpunkt der zusammengefassten Lage]]

## Im Code

- [[opencivil.nachweis.handrechnung#Handrechnung._schwerpunkt|Handrechnung._schwerpunkt]]
- [[opencivil.nachweis.verformung#Vergroesserungsfaktor._bewehrungsgehalte|Vergroesserungsfaktor._bewehrungsgehalte]]

## Themen

- [[Biegung und Normalkraft]]
- [[Verformung]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Liegen Grundbewehrung und Zulage in derselben Lage, wirken sie wie ein
gemeinsamer Querschnitt: ihre Flächen addieren sich. Wo die Rechnung nur
eine Lage je Seite kennt -- in der Handrechnung und beim
[[Vergrösserungsfaktor der Durchbiegung]] --, steht die Summe in ihrem
[[Schwerpunkt der zusammengefassten Lage|Schwerpunkt]].
