---
erzeugt: bc86a30a793c
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
f_{ct,eff} = k_t \cdot f_{ctm}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $k_t$ | – | – | [[Beiwert für die Dicke]] |
| $f_{ctm}$ | Mittelwert der Zugfestigkeit | N/mm² | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
f_{ct,eff} = k_t \cdot f_{ctm} = 0.87 \cdot 2.9\,\mathrm{N}/\mathrm{mm}^{2} = 2.52\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Gebraucht von

- [[Risskraft der gezogenen Querschnittshälfte]]
- [[Rissmoment des ungerissenen Querschnitts]]
- [[Rissnormalkraft beim Moment]]

## Im Code

- `opencivil.nachweis.sproedes_versagen:protokoll_zugfestigkeit`

## Themen

- [[Zwängung auf Normalkraft]]
- [[Sprödes Versagen]]
- [[Zwängung auf Biegung]]
- [[Sprödes Versagen je Richtung]]
- [[Spannung-Dehnung-Analyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->
