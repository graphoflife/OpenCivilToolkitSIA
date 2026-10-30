---
erzeugt: e9fe19758d17
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.6.5.4, (69)"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.6.5.4, (69)

$$
\sigma_{sd} = \min\left[\frac{E_s \cdot \psi}{6} \cdot \left(1 + \frac{f_{ctm}}{f_{yd}} \cdot \frac{d}{\varnothing_{sw}}\right);\ f_{yd}\right]
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $E_s$ | Elastizitätsmodul des Betonstahls | N/mm² | Vorgabe |
| $\psi$ | – | – | [[Massgebende Plattenrotation – die grössere]] |
| $f_{ctm}$ | Mittelwert der Zugfestigkeit | N/mm² | Vorgabe |
| $f_{yd}$ | Bemessungswert der Fliessgrenze | N/mm² | [[Bemessungswert der Fliessgrenze]] |
| $d$ | – | mm | [[Mittlere statische Höhe der beiden Lagen der Zugbewehrung]] |
| $\varnothing_{sw}$ | – | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  \sigma_{sd} &= \min\left[\frac{E_s \cdot \psi}{6} \cdot \left(1 + \frac{f_{ctm}}{f_{yd}} \cdot \frac{d}{\varnothing_{sw}}\right);\ f_{yd}\right] \\
  &= \min\left[\frac{200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 0.0186}{6} \cdot \left(1 + \frac{2.9\,\mathrm{N}/\mathrm{mm}^{2}}{435\,\mathrm{N}/\mathrm{mm}^{2}} \cdot \frac{234\,\mathrm{mm}}{10\,\mathrm{mm}}\right);\ 435\,\mathrm{N}/\mathrm{mm}^{2}\right] \\
  &= 435\,\mathrm{N}/\mathrm{mm}^{2}
\end{aligned}
$$

## Gebraucht von

- [[Beitrag der Durchstanzbewehrung]]

## Im Code

- [[opencivil.durchstanzen.mit_bewehrung#nachweisen|nachweisen]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Durchstanzbewehrung wird erst gedehnt, wenn sich der kritische Schubriss
öffnet. Wie weit, hängt an der Rotation der Platte ([[Plattenrotation]]):
die Spannung wächst mit $\psi$ und mit der Verbundwirkung, ausgedrückt durch
$f_{ctm}$ und das Verhältnis von statischer Höhe und Ankerdurchmesser. Mehr als
$f_{yd}$ kann sie nicht werden (4.3.6.5.4, Gleichung (69)).
