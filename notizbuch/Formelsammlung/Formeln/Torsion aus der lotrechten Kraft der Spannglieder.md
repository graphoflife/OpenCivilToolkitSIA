---
erzeugt: 95615688f0c4
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Ihr Moment um den Schwerpunkt»*

$$
T_p = P_{max,2} \cdot \sin \beta_{p,2} \cdot e_{p,2}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $P_{max,2}$ | Grösste Kraft im Glied, Spannglied 2 | kN | [[Grösste Kraft eines geneigten Spannglieds]] |
| $\beta_{p,2}$ | Neigung, Spannglied 2 | ° | Zwischenwert |
| $e_{p,2}$ | Lage neben dem Schwerpunkt, y - y\_S, Spannglied 2 | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
T_p = P_{max,2} \cdot \sin \beta_{p,2} \cdot e_{p,2} = 380.2\,\mathrm{kN} \cdot \sin \left(-4{}^{\circ}\right) \cdot \left(-80\,\mathrm{mm}\right) = 2.1\,\mathrm{kNm}
$$

## Gebraucht von

- [[Torsion der Wände neben geneigten Spanngliedern]]

## Im Code

- [[opencivil.nachweis.schubwandnachweis#Schubwandnachweis._ohne_glieder|Schubwandnachweis._ohne_glieder]]

## Themen

- [[Querkraft und Torsion]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Liegt ein geneigtes Glied neben dem Schwerpunkt, dreht seine lotrechte
Kraft um ihn: $T_p = \sum F_i \sin \beta_{p,i} \cdot e_{p,i}$ mit
$e_p = y - y_S$. Die Querkraft eines Lastfalls greift im Schwerpunkt an
und $T_{Ed}$ dreht um ihn; was die Glieder selbst tragen, fehlt den
Wänden darum auch in der Torsion – siehe
[[Torsion der Wände neben geneigten Spanngliedern]]. Ein Glied in der
Achse des Schwerpunkts dreht nichts, und die Formel fällt weg.

Vier Litzen um 5° geneigt, 50 mm links vom Schwerpunkt: 57.9 kN ·
(−50 mm) = −2.9 kNm.
