---
erzeugt: 862f75ffc976
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.1.2; 4.4.3.2.4"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.1.2; 4.4.3.2.4

$$
\sigma_p = \frac{N_p}{A} - \frac{M_{p,y}\,(I_z \cdot z' - I_{yz} \cdot y') + M_{p,z}\,(I_y \cdot y' - I_{yz} \cdot z')}{I_y \cdot I_z - I_{yz}^{2}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $N_p$ | Normalkraft aus der Vorspannung, Druck negativ | kN | [[Normalkraft aus der Vorspannung]] |
| $A$ | Fläche des Bruttoquerschnitts | mm² | Zwischenwert |
| $M_{p,y}$ | Moment aus der Vorspannung um y | kNm | [[Moment aus der Vorspannung]] |
| $I_z$ | Trägheitsmoment um z des Bruttoquerschnitts | ·10⁶ mm⁴ | Zwischenwert |
| $z'$ | Lage der Ecke, vom Schwerpunkt aus | mm | Zwischenwert |
| $I_{yz}$ | Deviationsmoment des Bruttoquerschnitts | ·10⁶ mm⁴ | Zwischenwert |
| $y'$ | Lage der Ecke, vom Schwerpunkt aus | mm | Zwischenwert |
| $M_{p,z}$ | Moment aus der Vorspannung um z | kNm | [[Moment aus der Vorspannung]] |
| $I_y$ | Trägheitsmoment um y des Bruttoquerschnitts | ·10⁶ mm⁴ | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  \sigma_p &= \frac{N_p}{A} - \frac{M_{p,y}\,(I_z \cdot z' - I_{yz} \cdot y') + M_{p,z}\,(I_y \cdot y' - I_{yz} \cdot z')}{I_y \cdot I_z - I_{yz}^{2}} \\
  &= \frac{-972\,\mathrm{kN}}{320000\,\mathrm{mm}^{2}} - \frac{-259.8\,\mathrm{kNm}\,(4266.7\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot \left(-400\,\mathrm{mm}\right) - 0\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot 200\,\mathrm{mm}) + \left(-24.6\,\mathrm{kNm}\right)\,(17066.7\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot 200\,\mathrm{mm} - 0\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot \left(-400\,\mathrm{mm}\right))}{17066.7\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot 4266.7\,\cdot 10^{6}\,\mathrm{mm}^{4} - \left(0\,\cdot 10^{6}\,\mathrm{mm}^{4}\right)^{2}} \\
  &= -7.97\,\mathrm{N}/\mathrm{mm}^{2}
\end{aligned}
$$

## Gebraucht von

- [[Rissmoment bei der Normalkraft]]
- [[Rissmoment des ungerissenen, vorgespannten Querschnitts]]

## Im Code

- [[opencivil.nachweis.rissgroessen#protokoll_vorspannung|protokoll_vorspannung]]

## Themen

- [[Sprödes Versagen je Richtung]]
- [[Zwängung auf Biegung]]
- [[Spannung-Dehnung-Analyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Spannung, die [[Normalkraft aus der Vorspannung|N_p]] und
[[Moment aus der Vorspannung|M_p]] am ungerissenen Bruttoquerschnitt an der
Ecke wecken, die reisst – Zug positiv, mit derselben Formel wie die Spannung
aus der Einwirkung ([[Spannung im ungerissenen Querschnitt]]). Einachsig
bleibt die Nulllinie waagrecht. Wo die Vorspannung drückt, ist
$\sigma_p$ negativ.

Welche Ecke reisst, entscheidet die Vorspannung mit: es reisst die, die dafür
das kleinste Moment braucht. Ohne Vorspannung ist das die am stärksten
gezogene, mit ihr die, an der am wenigsten Druck aufzuheben ist. Im
Rechteck 300 × 600 mm mit vier Litzen 200 mm unter dem Schwerpunkt sind es
am unteren Rand −664 kN / 180 000 mm² − 132.8 kNm / (18 · 10⁶ mm³) =
−3.69 − 7.38 = −11.07 N/mm².
