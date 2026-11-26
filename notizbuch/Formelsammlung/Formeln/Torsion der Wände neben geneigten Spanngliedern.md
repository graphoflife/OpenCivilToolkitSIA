---
erzeugt: 3f81b9b38286
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Was die Wände von T tragen»*

$$
T_w = T_{Ed} - T_p
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $T_{Ed}$ | – | kNm | Zwischenwert |
| $T_p$ | Moment der lotrechten Kraft der Glieder um den Schwerpunkt | kNm | [[Torsion aus der lotrechten Kraft der Spannglieder]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
T_w = T_{Ed} - T_p = 0\,\mathrm{kNm} - 2.1\,\mathrm{kNm} = -2.1\,\mathrm{kNm}
$$

## Im Code

- [[opencivil.nachweis.schubwandnachweis#Schubwandnachweis._ohne_glieder|Schubwandnachweis._ohne_glieder]]

## Themen

- [[Querkraft und Torsion]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Was die Wände von der Torsion tragen: $T_w = T_{Ed} - T_p$. Dabei ist
$T_p$ das Moment, das die lotrechten Kräfte der geneigten Glieder um den
Schwerpunkt drehen:
[[Torsion aus der lotrechten Kraft der Spannglieder]]. Dieses $T_w$
verteilt sich wie jede Torsion: als Umlauffluss in den Zellen, ohne Zelle
über die Federn der Wände mit Drehung.

Ein Kasten 200 × 500 mm auf der Bügelachse, $T_{Ed}$ = 20 kNm, vier
Litzen um 5° geneigt, 50 mm links vom Schwerpunkt: $T_w$ = 20 + 2.9 =
22.9 kNm, der Umlauffluss 22.9 kNm / (2 · 0.1 m²) = 114.5 kN/m.
