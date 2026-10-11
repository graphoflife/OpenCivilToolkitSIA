---
erzeugt: 62b92fbddff5
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 3.1.2.3.3"
---
> [!info] Normstelle
> SIA 262:2025, 3.1.2.3.3

$$
E_{cm} = k_e \cdot \sqrt[3]{f_{cm}} \quad \left(f_{cm}\ \text{in}\ \mathrm{N}/\mathrm{mm}^{2}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $k_e$ | Beiwert für die Gesteinskörnung | – | Vorgabe |
| $f_{cm}$ | Mittelwert der Zylinderdruckfestigkeit | N/mm² | [[Mittelwert der Zylinderdruckfestigkeit]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
E_{cm} = k_e \cdot \sqrt[3]{f_{cm}} = 10000 \cdot \sqrt[3]{38} = 33620\,\mathrm{N}/\mathrm{mm}^{2} \quad \left(f_{cm}\ \text{in}\ \mathrm{N}/\mathrm{mm}^{2}\right)
$$

## Gebraucht von

- [[Bemessungswert des Elastizitätsmoduls]]
- [[Wertigkeit im gerissenen Zustand]]
- [[Wirksamer Elastizitätsmodul]]

## Im Code

- `opencivil.material.beton:_e_cm`

## Themen

- [[Beton]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->
