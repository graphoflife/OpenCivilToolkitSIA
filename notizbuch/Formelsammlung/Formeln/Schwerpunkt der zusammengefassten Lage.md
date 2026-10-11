---
erzeugt: 1be5ead20d16
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Schwerpunkt der x-Bewehrung unten»*

$$
z_{u} = \frac{A_{s,2,x,g} \cdot z_{2,x,g} + A_{s,2,x,z} \cdot z_{2,x,z}}{A_{s,u}}
$$

*In der Herleitung: «Schwerpunkt der zusammengefassten Lage – 2. Lage Grundbewehrung + 2. Lage Zulage»*

$$
z_{2,x} = \frac{A_{s,2,x,g} \cdot z_{2,x,g} + A_{s,2,x,z} \cdot z_{2,x,z}}{A_{s,2,x,g} + A_{s,2,x,z}}
$$

*In der Herleitung: «Gemeinsamer Schwerpunkt der Lage»*

$$
z_{2,x} = \frac{A_{s,2,x,g} \cdot z_{2,x,g} + A_{s,2,x,z} \cdot z_{2,x,z}}{A_{s,2,x,g} + A_{s,2,x,z}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $A_{s,2,x,g}$ | Bewehrungsquerschnitt 2. Lage Grundbewehrung | mm² | Zwischenwert |
| $z_{2,x,g}$ | Tiefe 2. Lage Grundbewehrung ab Oberkante | mm | Zwischenwert |
| $A_{s,2,x,z}$ | Bewehrungsquerschnitt 2. Lage Zulage | mm² | Zwischenwert |
| $z_{2,x,z}$ | Tiefe 2. Lage Zulage ab Oberkante | mm | Zwischenwert |
| $A_{s,u}$ | – | mm² | [[Bewehrungsquerschnitt der zusammengefassten Lage]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\begin{aligned}
  z_{u} &= \frac{A_{s,2,x,g} \cdot z_{2,x,g} + A_{s,2,x,z} \cdot z_{2,x,z}}{A_{s,u}} \\
  &= \frac{1696\,\mathrm{mm}^{2} \cdot 249\,\mathrm{mm} + 754\,\mathrm{mm}^{2} \cdot 246\,\mathrm{mm}}{2450\,\mathrm{mm}^{2}} \\
  &= 248.1\,\mathrm{mm}
\end{aligned}
$$

Mit den Zahlen aus dem Beispielprojekt:

$$
\begin{aligned}
  z_{2,x} &= \frac{A_{s,2,x,g} \cdot z_{2,x,g} + A_{s,2,x,z} \cdot z_{2,x,z}}{A_{s,2,x,g} + A_{s,2,x,z}} \\
  &= \frac{1696\,\mathrm{mm}^{2} \cdot 249\,\mathrm{mm} + 754\,\mathrm{mm}^{2} \cdot 246\,\mathrm{mm}}{1696\,\mathrm{mm}^{2} + 754\,\mathrm{mm}^{2}} \\
  &= 248.1\,\mathrm{mm}
\end{aligned}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  z_{2,x} &= \frac{A_{s,2,x,g} \cdot z_{2,x,g} + A_{s,2,x,z} \cdot z_{2,x,z}}{A_{s,2,x,g} + A_{s,2,x,z}} \\
  &= \frac{1696\,\mathrm{mm}^{2} \cdot 249\,\mathrm{mm} + 754\,\mathrm{mm}^{2} \cdot 246\,\mathrm{mm}}{1696\,\mathrm{mm}^{2} + 754\,\mathrm{mm}^{2}} \\
  &= 248.1\,\mathrm{mm}
\end{aligned}
$$

## Gebraucht von

- [[Statische Höhe]]

## Im Code

- [[opencivil.nachweis.handrechnung#Handrechnung._schwerpunkt|Handrechnung._schwerpunkt]]
- [[opencivil.querschnitt.platte#Lagenaufbau._vergroesserung|Lagenaufbau._vergroesserung]]
- [[opencivil.querschnitt.platte#protokoll_lage|protokoll_lage]]

## Themen

- [[Querschnitt]]
- [[Biegung und Normalkraft]]
- [[Duktilität]]
- [[Zwängung auf Biegung]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->
