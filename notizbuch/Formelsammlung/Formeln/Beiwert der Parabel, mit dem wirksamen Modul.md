---
erzeugt: 0c985aceb480
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
k_{\sigma} = \max\left(1;\ \frac{E_{c,eff}}{400 \cdot f_{cd}}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $E_{c,eff}$ | – | N/mm² | [[Wirksamer Elastizitätsmodul]] |
| $f_{cd}$ | Bemessungswert der Betondruckfestigkeit | N/mm² | [[Bemessungswert der Betondruckfestigkeit]], Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
k_{\sigma} = \max\left(1;\ \frac{E_{c,eff}}{400 \cdot f_{cd}}\right) = \max\left(1;\ \frac{11207\,\mathrm{N}/\mathrm{mm}^{2}}{400 \cdot 20\,\mathrm{N}/\mathrm{mm}^{2}}\right) = 1.4
$$

## Im Code

- `opencivil.nachweis.rechenwahl:protokoll_betongesetz`
- `opencivil.spannungsanalyse:_herleitung`

## Themen

- [[Knicken]]
- [[Biegung und Normalkraft]]
- [[Stahlspannung gegen Fliessen]]
- [[Spannung-Dehnung-Analyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->
