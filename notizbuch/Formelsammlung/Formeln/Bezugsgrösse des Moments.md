---
erzeugt: d39d864c7c5b
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
M_{ref} = \max\left(\left|M_{Rd,x}^{+}\right|;\ \left|M_{Rd,x}^{-}\right|\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $M_{Rd,x}^{+}$ | Grösster positiver Momentenwiderstand (x-Richtung) | kNm | Zwischenwert |
| $M_{Rd,x}^{-}$ | Grösster negativer Momentenwiderstand (x-Richtung) | kNm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  M_{ref} &= \max\left(\left|M_{Rd,x}^{+}\right|;\ \left|M_{Rd,x}^{-}\right|\right) \\
  &= \max\left(\left|162.9\,\mathrm{kNm}\right|;\ \left|-178.6\,\mathrm{kNm}\right|\right) \\
  &= 178.6\,\mathrm{kNm}
\end{aligned}
$$

## Gebraucht von

- [[Einwirkung im normierten Diagramm]]
- [[Kürzester Abstand zur Resistenzlinie]]

## Im Code

- [[opencivil.nachweis.biegung_normalkraft#BiegungNormalkraft._protokoll_naechster|BiegungNormalkraft._protokoll_naechster]]

## Themen

- [[Biegung und Normalkraft]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das Gegenstück auf der Momentenachse: das grössere der beiden grössten
Momente, positiv oder negativ. Mit beiden Bezugsgrössen passt die
Resistenzlinie ungefähr in ein Quadrat der Seitenlänge 2, und Abstände in
beide Richtungen sind vergleichbar.
