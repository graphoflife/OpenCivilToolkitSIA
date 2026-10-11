---
erzeugt: 6600dcabfa13
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 2.4.2.3"
---
> [!info] Normstelle
> SIA 262:2025, 2.4.2.3

$$
\eta_{fc} = \min\left[\left(\frac{40\,\mathrm{N}/\mathrm{mm}^{2}}{f_{ck}}\right)^{1/3};\ 1.0\right]
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $f_{ck}$ | Charakteristische Zylinderdruckfestigkeit | N/mm² | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\eta_{fc} = \min\left[\left(\frac{40\,\mathrm{N}/\mathrm{mm}^{2}}{f_{ck}}\right)^{1/3};\ 1.0\right] = \min\left[\left(\frac{40\,\mathrm{N}/\mathrm{mm}^{2}}{30\,\mathrm{N}/\mathrm{mm}^{2}}\right)^{1/3};\ 1.0\right] = 1
$$

## Gebraucht von

- [[Bemessungswert der Betondruckfestigkeit]]

## Im Code

- `opencivil.material.beton:_eta_fc`

## Themen

- [[Beton]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->
