---
erzeugt: 8580d2c2e311
art: formel
tags: [formel]
normstelle: ["SIA 262:2025, 4.3.1.2", "SIA 262:2025, 4.4.2.3.4, Tabelle 17"]
---
> [!info] Normstellen
> SIA 262:2025, 4.3.1.2 · SIA 262:2025, 4.4.2.3.4, Tabelle 17

$$
M_{Riss} = \left(f_{ct,eff} - \sigma_p\right) \cdot W
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $f_{ct,eff}$ | – | N/mm² | [[Wirksame Zugfestigkeit]] |
| $\sigma_p$ | aus der Vorspannung, an der Ecke | N/mm² | [[Spannung aus der Vorspannung an der Ecke]] |
| $W$ | – | ·10⁶ mm³ | [[Widerstandsmoment zum gezogensten Betonpunkt]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  M_{Riss} &= \left(f_{ct,eff} - \sigma_p\right) \cdot W \\
  &= \left(2.56\,\mathrm{N}/\mathrm{mm}^{2} - \left(-7.97\,\mathrm{N}/\mathrm{mm}^{2}\right)\right) \cdot 42.67\,\cdot 10^{6}\,\mathrm{mm}^{3} \\
  &= 449.3\,\mathrm{kNm}
\end{aligned}
$$

## Im Code

- [[opencivil.nachweis.rissgroessen#protokoll_rissmoment|protokoll_rissmoment]]

## Themen

- [[Sprödes Versagen je Richtung]]
- [[Zwängung auf Biegung]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie das [[Rissmoment des ungerissenen Querschnitts]], nur drückt die
Vorspannung den gezogenen Rand schon: das Moment muss erst ihren Druck
$\sigma_p$ aufheben ([[Spannung aus der Vorspannung an der Ecke]]), dann
reisst der Beton. So zählt die Vorspannung beim spröden Versagen und bei
der Zwängung mit (SIA 262:2025, 4.3.1.2; 4.4.3.2.4).

Im Rechteck 300 × 600 mm aus C30/37 mit vier Litzen 200 mm unter dem
Schwerpunkt steigt das Rissmoment von 2.64 · 18 = 47.5 kNm auf
(2.64 + 11.07) · 18 = 246.7 kNm, mit $W$ = 18 · 10⁶ mm³.
