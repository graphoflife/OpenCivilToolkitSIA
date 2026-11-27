---
erzeugt: c0efaf5561be
art: formel
tags: [formel]
normstelle: "SIA 264:2014, 5.4.3.3, (26); Figur 18"
---
> [!info] Normstelle
> SIA 264:2014, 5.4.3.3, (26); Figur 18

*In der Herleitung: «Querkraftwiderstand über die Breite b: (26) mal b»*

$$
V_{Rd} = k_d \cdot \tau_{cd} \cdot d_p \cdot \frac{b_0}{b_s} \cdot b
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $k_d$ | Beiwert für d\_p bis 150 mm | – | Zwischenwert |
| $\tau_{cd}$ | Bemessungswert der Schubspannungsgrenze | N/mm² | [[Bemessungswert der Schubspannungsgrenze]] |
| $d_p$ | Statische Höhe der Decke | mm | [[Statische Höhe einer Blechverbunddecke]] |
| $b_0$ | Rippenbreite | mm | [[Rippenbreite einer Blechverbunddecke]] |
| $b_s$ | Rippenabstand | mm | Zwischenwert |
| $b$ | Breite der Decke, n · b\_s | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  V_{Rd} &= k_d \cdot \tau_{cd} \cdot d_p \cdot \frac{b_0}{b_s} \cdot b \\
  &= 0.8 \cdot 1.1\,\mathrm{N}/\mathrm{mm}^{2} \cdot 108.9\,\mathrm{mm} \cdot \frac{95\,\mathrm{mm}}{200\,\mathrm{mm}} \cdot 1000\,\mathrm{mm} \\
  &= 45.3\,\mathrm{kN}
\end{aligned}
$$

## Im Code

- [[opencivil.nachweis.qa_blechverbund#KennzahlenBlechQA|KennzahlenBlechQA._querkraft]]

## Themen

- [[Blechverbunddecke]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Gleichung (26) der SIA 264 gibt den Querkraftwiderstand je Breite der
Decke. Er wächst mit der
[[Statische Höhe einer Blechverbunddecke|statischen Höhe]] $d_p$ und mit dem
Anteil $b_0/b_s$ der Breite, den die Betonrippen einnehmen
([[Rippenbreite einer Blechverbunddecke|Rippenbreite]]). Mal die ganze
gezeichnete Breite $b = n \cdot b_s$ gibt er den Widerstand der Decke.

$\tau_{cd}$ ist der
[[Bemessungswert der Schubspannungsgrenze]] des Betons nach SIA 262. Er
bleibt ein Bemessungswert, auch wo die Tragsicherheit den Beton
charakteristisch rechnet: Gleichung (26) nennt nur ihn – eine Vorgabe,
nicht nachgeschlagen.

Der Beiwert $k_d = 0.8$ gilt bis $d_p = 150$ mm. Für dickere Decken
verweist die Norm auf SIA 262; das rechnet das Werkzeug nicht, und die
Querkraft steht grau.
