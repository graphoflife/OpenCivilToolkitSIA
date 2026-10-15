---
erzeugt: fb3f4a9f4fbf
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
| $f_{cd}$ | Bemessungswert der Betondruckfestigkeit | N/mm² | [[Bemessungswert der Betondruckfestigkeit]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
k_{\sigma} = \max\left(1;\ \frac{E_{c,eff}}{400 \cdot f_{cd}}\right) = \max\left(1;\ \frac{11207\,\mathrm{N}/\mathrm{mm}^{2}}{400 \cdot 20\,\mathrm{N}/\mathrm{mm}^{2}}\right) = 1.4
$$

## Im Code

- [[opencivil.nachweis.rechenwahl#protokoll_betongesetz|protokoll_betongesetz]]
- [[opencivil.spannungsanalyse#herleitung|herleitung]]

## Themen

- [[Knicken]]
- [[Biegung und Normalkraft]]
- [[Stahlspannung gegen Fliessen]]
- [[Spannung-Dehnung-Analyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Derselbe Krümmungsbeiwert wie beim Beton (siehe
[[Krümmungsbeiwert der Spannungs-Dehnungs-Beziehung]]), aber mit dem
kriechweichen [[Wirksamer Elastizitätsmodul|wirksamen Modul]] statt mit
$E_{cd}$: die Parabel beginnt flacher, der Beton gibt unter Dauerlast nach.

Mit grossem $\varphi$ und charakteristischen Werten würde $k_\sigma$ kleiner
als 1. Dann hätte der Nenner der Parabel, $1 + (k_\sigma - 2)\,\eta$, im
ansteigenden Ast eine Nullstelle, bei $\eta = 1/(2 - k_\sigma)$. Darum wird
$k_\sigma$ nicht kleiner als 1 angesetzt -- dann ist der Beton bis $f_c$ bei
$\varepsilon_{c1d}$ linear. Diese Grenze ist nach Vorgabe eingebaut, nicht
nachgeschlagen.
