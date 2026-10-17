---
erzeugt: 2f93282fe676
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

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
-- eine Regel für jede Rechnung. Im Bruchzustand ist das $E_{cm}$, unter
Dauerlast der kriechweiche [[Wirksamer Elastizitätsmodul|wirksame Modul]]
$E_{cm}/(1+\varphi)$: die Parabel beginnt dann flacher, der Beton gibt nach.
Der Beton selbst nennt denselben Beiwert mit $E_{cd}$ (siehe
[[Krümmungsbeiwert der Spannungs-Dehnungs-Beziehung]]); mit
$\gamma_{cE} = 1$ ist das dieselbe Zahl.

Mit grossem $\varphi$ und charakteristischen Werten würde $k_\sigma$ kleiner
als 1. Dann hätte der Nenner der Parabel, $1 + (k_\sigma - 2)\,\eta$, im
ansteigenden Ast eine Nullstelle, bei $\eta = 1/(2 - k_\sigma)$. Darum wird
$k_\sigma$ nicht kleiner als 1 angesetzt -- dann ist der Beton bis $f_c$ bei
$\varepsilon_{c1d}$ linear. Diese Grenze ist nach Vorgabe eingebaut, nicht
nachgeschlagen.
