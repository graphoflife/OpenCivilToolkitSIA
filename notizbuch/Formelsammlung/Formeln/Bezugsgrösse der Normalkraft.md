---
erzeugt: 4b1ef576d38a
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
N_{ref} = \max\left(\left|N_{Rd,x}^{+}\right|;\ \left|N_{Rd,x}^{-}\right|\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $N_{Rd,x}^{+}$ | Grösste aufnehmbare Zugkraft (x-Richtung) | kN | Zwischenwert |
| $N_{Rd,x}^{-}$ | Grösste aufnehmbare Druckkraft (x-Richtung) | kN | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  N_{ref} &= \max\left(\left|N_{Rd,x}^{+}\right|;\ \left|N_{Rd,x}^{-}\right|\right) \\
  &= \max\left(\left|655.6\,\mathrm{kN}\right|;\ \left|-5000\,\mathrm{kN}\right|\right) \\
  &= 5000\,\mathrm{kN}
\end{aligned}
$$

## Gebraucht von

- [[Einwirkung im normierten Diagramm]]
- [[Kürzester Abstand zur Resistenzlinie]]

## Im Code

- `opencivil.nachweis.biegung_normalkraft:BiegungNormalkraft._protokoll_naechster`

## Themen

- [[Biegung und Normalkraft]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->
