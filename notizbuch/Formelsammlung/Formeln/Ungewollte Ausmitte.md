---
erzeugt: 86f3906b6a47
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.7.5, (75)"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.7.5, (75)

$$
e_{0d} = \max\left(\frac{d}{30};\ \frac{\alpha_i \cdot l_{cr}}{2}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $d$ | – | mm | Zwischenwert |
| $\alpha_i$ | – | – | [[Schiefstellung]] |
| $l_{cr}$ | – | m | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
e_{0d} = \max\left(\frac{d}{30};\ \frac{\alpha_i \cdot l_{cr}}{2}\right) = \max\left(\frac{249\,\mathrm{mm}}{30};\ \frac{0.005 \cdot 3\,\mathrm{m}}{2}\right) = 8.3\,\mathrm{mm}
$$

## Im Code

- [[opencivil.nachweis.knicken#Knickverfahren|Knickverfahren._protokoll_fall]]

## Themen

- [[Knicken]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Aus der [[Schiefstellung]]: ein Stab der Knicklänge $l_{cr}$, um $\alpha_i$
geneigt, weicht in seiner Mitte um $\alpha_i \cdot l_{cr}/2$ ab. Bei kurzen
Stäben ist das wenig; dann gilt eine Mindestausmitte aus der statischen Höhe,
$d/30$ (SIA 262:2025, 4.3.7.5, (75)) -- nicht aus der Abmessung des
Querschnitts, wie hier bis 2026-11-14 stand.
