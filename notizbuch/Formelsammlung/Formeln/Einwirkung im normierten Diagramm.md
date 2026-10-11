---
erzeugt: 1ea5629ac95f
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
\bar{E}_{d,x} = \sqrt{\left(\frac{N_{Ed}}{N_{ref}}\right)^{2} + \left(\frac{M_{Ed}}{M_{ref}}\right)^{2}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $N_{Ed}$ | – | kN | Zwischenwert |
| $N_{ref}$ | – | kN | [[Bezugsgrösse der Normalkraft]] |
| $M_{Ed}$ | – | kNm | Zwischenwert |
| $M_{ref}$ | – | kNm | [[Bezugsgrösse des Moments]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\bar{E}_{d,x} = \sqrt{\left(\frac{N_{Ed}}{N_{ref}}\right)^{2} + \left(\frac{M_{Ed}}{M_{ref}}\right)^{2}} = \sqrt{\left(\frac{-500\,\mathrm{kN}}{5000\,\mathrm{kN}}\right)^{2} + \left(\frac{30\,\mathrm{kNm}}{178.6\,\mathrm{kNm}}\right)^{2}} = 0.195
$$

## Gebraucht von

- [[Erfüllungsgrad]]
- [[Widerstand im normierten Diagramm]]

## Im Code

- `opencivil.nachweis.biegung_normalkraft:BiegungNormalkraft._protokoll_naechster`

## Themen

- [[Biegung und Normalkraft]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->
