---
erzeugt: e3dcf06c882c
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 2.4.2.4"
---
> [!info] Normstelle
> SIA 262:2025, 2.4.2.4

$$
\tau_{cd} = \frac{0.3 \cdot \sqrt{f_{ck}}}{\gamma_c} \quad \left(f_{ck}\ \text{in}\ \mathrm{N}/\mathrm{mm}^{2}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $f_{ck}$ | Charakteristische Zylinderdruckfestigkeit | N/mm² | Vorgabe |
| $\gamma_c$ | Teilsicherheitsbeiwert für Beton | – | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\tau_{cd} = \frac{0.3 \cdot \sqrt{f_{ck}}}{\gamma_c} = \frac{0.3 \cdot \sqrt{30}}{1.5} = 1.1\,\mathrm{N}/\mathrm{mm}^{2} \quad \left(f_{ck}\ \text{in}\ \mathrm{N}/\mathrm{mm}^{2}\right)
$$

## Im Code

- [[opencivil.material.beton#_tau_cd|_tau_cd]]

## Themen

- [[Beton]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->
