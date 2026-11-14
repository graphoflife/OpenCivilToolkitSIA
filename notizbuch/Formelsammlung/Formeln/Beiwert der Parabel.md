---
erzeugt: a3c9a3f04df0
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.2.1.6, (27); Untergrenze 1 nach Vorgabe"
---
> [!info] Normstelle
> SIA 262:2025, 4.2.1.6, (27); Untergrenze 1 nach Vorgabe

*In der Herleitung: «Werkstoffgesetz C30/37, Bemessungswerte: Beiwert der Parabel»*

$$
k_{\sigma} = \max\left(1;\ \frac{E_{cm}}{400 \cdot f_{cd}}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $E_{cm}$ | Mittelwert des Elastizitätsmoduls | N/mm² | [[Mittelwert des Elastizitätsmoduls]] |
| $f_{cd}$ | Bemessungswert der Betondruckfestigkeit | N/mm² | [[Bemessungswert der Betondruckfestigkeit]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
k_{\sigma} = \max\left(1;\ \frac{E_{cm}}{400 \cdot f_{cd}}\right) = \max\left(1;\ \frac{33620\,\mathrm{N}/\mathrm{mm}^{2}}{400 \cdot 20\,\mathrm{N}/\mathrm{mm}^{2}}\right) = 4.2
$$

## Im Code

- [[opencivil.querschnitt.werkstoffgesetz#Betongesetz.protokoll|Betongesetz.protokoll]]

## Themen

- [[Schiefe Biegung]]
- [[Knicken]]
- [[Biegung und Normalkraft]]
- [[Stahlspannung gegen Fliessen]]
- [[Stahlspannung aus Rissbreite]]
- [[Spannung-Dehnung-Analyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Krümmungsbeiwert der Parabel aus dem Modul, mit dem das Gesetz rechnet
-- eine Regel für jede Rechnung. Im Bruchzustand des Querschnitts ist das
$E_{cm}$, also $\gamma_{cE} = 1.0$; für die Verformung beim Knicken
$E_{cd} = E_{cm}/1.2$ (SIA 262:2025, 4.2.1.15 bis 4.2.1.17). Unter Dauerlast
kommt der kriechweiche [[Wirksamer Elastizitätsmodul|wirksame Modul]]
$E_c/(1+\varphi)$ dazu: die Parabel beginnt dann flacher, der Beton gibt nach.
Der Beton selbst nennt den Beiwert mit $E_{cd}$ für das Knicken (siehe
[[Krümmungsbeiwert der Spannungs-Dehnungs-Beziehung]]); bis 2026-11-14
stand hier, mit $\gamma_{cE} = 1$ sei das dieselbe Zahl.

Mit grossem $\varphi$ und charakteristischen Werten würde $k_\sigma$ kleiner
als 1. Dann hätte der Nenner der Parabel, $1 + (k_\sigma - 2)\,\eta$, im
ansteigenden Ast eine Nullstelle, bei $\eta = 1/(2 - k_\sigma)$. Darum wird
$k_\sigma$ nicht kleiner als 1 angesetzt -- dann ist der Beton bis $f_c$ bei
$\varepsilon_{c1d}$ linear. Diese Grenze ist nach Vorgabe eingebaut, nicht
nachgeschlagen.
