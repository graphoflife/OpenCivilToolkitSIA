---
erzeugt: cbe555000685
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
| $A_{s,2,x,g}$ | – | mm² | Zwischenwert |
| $A_{s,2,x,z}$ | – | mm² | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
A_{s,2,x} = A_{s,2,x,g} + A_{s,2,x,z} = 1696\,\mathrm{mm}^{2} + 754\,\mathrm{mm}^{2} = 2450\,\mathrm{mm}^{2}
$$

## Im Code

- [[opencivil.nachweis.handrechnung#Handrechnung._schwerpunkt|Handrechnung._schwerpunkt]]

## Themen

- [[Biegung und Normalkraft]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Liegen Grundbewehrung und Zulage in derselben Lage, wirken sie wie ein
gemeinsamer Querschnitt: ihre Flächen addieren sich. Wo die Rechnung nur
eine Lage je Seite kennt -- in der Handrechnung --, steht die Summe in ihrem
[[Schwerpunkt der zusammengefassten Lage|Schwerpunkt]]. Dieselbe Summe
schreiben die Nachweise der Lagen und der
[[Vergrösserungsfaktor der Durchbiegung]] als [[Bewehrung der Lage]].
