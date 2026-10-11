---
erzeugt: 62e6c77f6e5f
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.2.1.6"
---
> [!info] Normstelle
> SIA 262:2025, 4.2.1.6

$$
k_{\sigma} = \frac{E_{cd}}{400 \cdot f_{cd}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $E_{cd}$ | Bemessungswert des Elastizitätsmoduls | N/mm² | [[Bemessungswert des Elastizitätsmoduls]] |
| $f_{cd}$ | Bemessungswert der Betondruckfestigkeit | N/mm² | [[Bemessungswert der Betondruckfestigkeit]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
k_{\sigma} = \frac{E_{cd}}{400 \cdot f_{cd}} = \frac{33620\,\mathrm{N}/\mathrm{mm}^{2}}{400 \cdot 20\,\mathrm{N}/\mathrm{mm}^{2}} = 4.202
$$

## Im Code

- [[opencivil.material.beton]]
- [[opencivil.querschnitt.analyse#Querschnittsanalyse.werkstoffe_protokollieren|Querschnittsanalyse.werkstoffe_protokollieren]]

## Themen

- [[Beton]]
- [[Schiefe Biegung]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->
