---
erzeugt: 1d6483d81573
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
N_{Riss}(M) = f_{ct,eff} \cdot b \cdot h - \frac{6 \cdot \left|M\right|}{h}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $f_{ct,eff}$ | – | N/mm² | [[Wirksame Zugfestigkeit]] |
| $b$ | Betrachtete Breite (x) | mm | Vorgabe |
| $h$ | Plattendicke | mm | Vorgabe |
| $M$ | – | kNm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  N_{Riss}(M) &= f_{ct,eff} \cdot b \cdot h - \frac{6 \cdot \left|M\right|}{h} \\
  &= 2.52\,\mathrm{N}/\mathrm{mm}^{2} \cdot 1000\,\mathrm{mm} \cdot 300\,\mathrm{mm} - \frac{6 \cdot \left|30\,\mathrm{kNm}\right|}{300\,\mathrm{mm}} \\
  &= 156.5\,\mathrm{kN}
\end{aligned}
$$

## Im Code

- [[opencivil.spannungsanalyse#_herleitung|_herleitung]]

## Themen

- [[Spannung-Dehnung-Analyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Dieselbe Rissbedingung wie beim Rissmoment, nach der Normalkraft aufgelöst:
beim Moment $M$ reisst der Querschnitt, wenn die Zugkraft $N_{Riss}$
erreicht. Unter Zug reisst die ganze Dicke, darum gilt der
[[Beiwert für die Dicke]] mit der ganzen Höhe und nicht mit einem Drittel wie
beim Rissmoment -- nach Vorgabe, nicht nachgeschlagen. Das Vorzeichen des
Moments zählt nicht: der Querschnitt ist oben wie unten derselbe.
