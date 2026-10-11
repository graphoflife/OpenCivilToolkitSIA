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

## Theorie

Was ein Beton an Schub ohne Bügel aufnimmt, wächst nicht mit der
Druckfestigkeit, sondern etwa mit ihrer Wurzel -- es hängt an der
Zugfestigkeit, und die folgt demselben Gesetz. Daher $\sqrt{f_{ck}}$. Die
Formel ist empirisch: $f_{ck}$ geht als blosse Zahl in N/mm² ein, und das
Ergebnis ist eine Spannung in N/mm².

$\tau_{cd}$ ist der Grundwert des
[[Querkraftwiderstand ohne Querkraftbewehrung|Querkraftwiderstands ohne Querkraftbewehrung]];
der [[Beiwert für die statische Höhe]] passt ihn an Höhe, Dehnung und
Gesteinskörnung an.
