---
erzeugt: 0cfe2fd77467
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
I_T = 2 \int_A \phi\, dA + 2 \sum_k \phi_k\, A_k
$$

## Im Code

- [[opencivil.querschnitt.analyse#Querschnittsanalyse.torsion_protokollieren|Querschnittsanalyse.torsion_protokollieren]]

## Themen

- [[Querschnittsanalyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das Torsionsmoment ist $T = G\,\theta\,I_T$, und $I_T$ ist das Doppelte des
Volumens unter der Haut φ ([[Spannungsfunktion von Prandtl]]). Über jedem
Hohlraum zählt die steife Platte mit, seine Fläche mal $\phi_k$.

Bei einem dünnen Rohr bleibt fast nur dieser Teil. φ steigt über die
Wanddicke $t$ gleichmässig von null auf $\phi_k$; aus dem Ringintegral wird
$\phi_k = 2A_k / \oint ds/t$, und $I_T \approx 2\,\phi_k\,A_k = 4A_k^2 / \oint ds/t$
ist die Formel von Bredt. Bei einem vollen Querschnitt gibt es keinen
Hohlraum, und alles steckt im Volumen: beim Kreis $\pi r^4/2$, beim Rechteck
eine Reihe, beim dünnen Brett $s\,t^3/3$.
