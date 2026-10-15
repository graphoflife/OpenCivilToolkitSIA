---
erzeugt: f70f946fccc8
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
W = \frac{I_z}{v_z}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $I_z$ | Trägheitsmoment um z | ·10⁶ mm⁴ | Zwischenwert |
| $v_z$ | Abstand des gezogenen Rands vom Schwerpunkt | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
W = \frac{I_z}{v_z} = \frac{22475\,\cdot 10^{6}\,\mathrm{mm}^{4}}{400\,\mathrm{mm}} = 56.19\,\cdot 10^{6}\,\mathrm{mm}^{3}
$$

## Gebraucht von

- [[Rissmoment bei der Normalkraft]]

## Im Code

- [[opencivil.querschnitt.schnittanalyse#Schnittpaar.herleitung_riss|Schnittpaar.herleitung_riss]]

## Themen

- [[Spannung-Dehnung-Analyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Am ungerissenen, elastischen Querschnitt wächst die Spannung aus einem
Moment linear mit dem Abstand von der Schwerachse: $\sigma = M \cdot v / I$.
Am gezogenen Rand ist $v = v_z$, also $\sigma = M / W$ mit $W = I / v_z$.
$I$ gehört zur Achse der Biegung – $I_y$ bei Zug unten oder oben, $I_z$ bei
Zug links oder rechts. Bei einem unsymmetrischen Querschnitt sind die beiden
Ränder verschieden weit entfernt: zu jedem Rand gehört sein eigenes $W$. Beim
Rechteck ist $v_z = h/2$ und $W = b \cdot h^2 / 6$.
