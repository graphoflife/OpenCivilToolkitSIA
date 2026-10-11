---
erzeugt: 1ff5bc83f82e
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 2.4.2.3"
---
> [!info] Normstelle
> SIA 262:2025, 2.4.2.3

$$
f_{cd} = \frac{\eta_{fc} \cdot f_{ck}}{\gamma_c}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\eta_{fc}$ | Beiwert zur Berücksichtigung der Festigkeitsminderung | – | [[Beiwert zur Berücksichtigung der Festigkeitsminderung]] |
| $f_{ck}$ | Charakteristische Zylinderdruckfestigkeit | N/mm² | Vorgabe |
| $\gamma_c$ | Teilsicherheitsbeiwert für Beton | – | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
f_{cd} = \frac{\eta_{fc} \cdot f_{ck}}{\gamma_c} = \frac{1 \cdot 30\,\mathrm{N}/\mathrm{mm}^{2}}{1.5} = 20\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Gebraucht von

- [[Beiwert der Parabel, mit dem wirksamen Modul]]
- [[Druckzonenhöhe bei reiner Biegung]]
- [[Krümmungsbeiwert der Spannungs-Dehnungs-Beziehung]]
- [[Widerstand der Druckdiagonalen]]

## Im Code

- `opencivil.material.beton`

## Themen

- [[Beton]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->
