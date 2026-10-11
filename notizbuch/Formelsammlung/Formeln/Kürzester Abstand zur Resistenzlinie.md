---
erzeugt: 08feaf4e1bcb
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
a = \sqrt{\left(\frac{N_{Ed} - N_P}{N_{ref}}\right)^{2} + \left(\frac{M_{Ed} - M_P}{M_{ref}}\right)^{2}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $N_{Ed}$ | – | kN | Zwischenwert |
| $N_P$ | – | kN | Zwischenwert |
| $N_{ref}$ | – | kN | [[Bezugsgrösse der Normalkraft]] |
| $M_{Ed}$ | – | kNm | Zwischenwert |
| $M_P$ | – | kNm | Zwischenwert |
| $M_{ref}$ | – | kNm | [[Bezugsgrösse des Moments]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  a &= \sqrt{\left(\frac{N_{Ed} - N_P}{N_{ref}}\right)^{2} + \left(\frac{M_{Ed} - M_P}{M_{ref}}\right)^{2}} \\
  &= \sqrt{\left(\frac{-500\,\mathrm{kN} - 160.8\,\mathrm{kN}}{5000\,\mathrm{kN}}\right)^{2} + \left(\frac{30\,\mathrm{kNm} - 38.6\,\mathrm{kNm}}{178.6\,\mathrm{kNm}}\right)^{2}} \\
  &= 0.141
\end{aligned}
$$

## Gebraucht von

- [[Widerstand im normierten Diagramm]]

## Im Code

- `opencivil.nachweis.biegung_normalkraft:BiegungNormalkraft._protokoll_naechster`

## Themen

- [[Biegung und Normalkraft]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->
