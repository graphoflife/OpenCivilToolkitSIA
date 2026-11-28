---
erzeugt: ea8db9793fef
art: formel
tags: [formel]
normstelle: "SIA 266:2015, 4.2.1.4, Gl. (5)"
---
> [!info] Normstelle
> SIA 266:2015, 4.2.1.4, Gl. (5)

$$
E_{xd} = \frac{E_{xk}}{\gamma_M}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $E_{xk}$ | Elastizitätsmodul senkrecht zu den Lagerfugen, kennzeichnend | N/mm² | [[Elastizitätsmodul senkrecht zu den Lagerfugen, kennzeichnend]] |
| $\gamma_M$ | Widerstandsbeiwert des Mauerwerks | – | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
E_{xd} = \frac{E_{xk}}{\gamma_M} = \frac{7000\,\mathrm{N}/\mathrm{mm}^{2}}{2} = 3500\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Im Code

- [[opencivil.material.mauerwerk#_durch_gamma|_durch_gamma]]

## Themen

- [[Mauerwerk]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Für die Tragsicherheit zählt auch die Steifigkeit mit ihrem Bemessungswert:
$E_{xk}$ durch $\gamma_M = 2.0$ (4.2.1.4, Gl. (5)). Für Standardmauerwerk
ist das $1000 \cdot f_{xd}$, die Zahl der Tabelle 7. Eine weichere Wand
biegt sich unter einer ausmittigen Last stärker aus, und die Ausmitte wächst
mit; mit dem kleineren Wert liegt diese Rechnung auf der sicheren Seite. Im
Verband gilt auch er mal 0.85 (4.2.1.1).
