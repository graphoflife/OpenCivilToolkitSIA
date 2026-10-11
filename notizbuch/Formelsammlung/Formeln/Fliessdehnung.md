---
erzeugt: be9d0783684a
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.2.2.4"
---
> [!info] Normstelle
> SIA 262:2025, 4.2.2.4

*In der Herleitung: «Fliessdehnung (Bemessungswert)»*

$$
\varepsilon_{yd} = \frac{f_{yd}}{E_s}
$$

*In der Herleitung: «Grösste Zugdehnung in der Bewehrung»*

$$
\varepsilon_y = \frac{f_{yk}}{E_s}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $f_{yd}$ | Bemessungswert der Fliessgrenze | N/mm² | [[Bemessungswert der Fliessgrenze]] |
| $E_s$ | Elastizitätsmodul des Betonstahls | N/mm² | Vorgabe |
| $f_{yk}$ | Charakteristische Fliessgrenze | N/mm² | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\varepsilon_{yd} = \frac{f_{yd}}{E_s} = \frac{435\,\mathrm{N}/\mathrm{mm}^{2}}{200000\,\mathrm{N}/\mathrm{mm}^{2}} = 0.217\,\%
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\varepsilon_y = \frac{f_{yk}}{E_s} = \frac{500\,\mathrm{N}/\mathrm{mm}^{2}}{200000\,\mathrm{N}/\mathrm{mm}^{2}} = 2.5\,\text{‰} \quad < \quad \varepsilon_{s,x} = 4.67\,\text{‰}
$$

## Im Code

- [[opencivil.material.betonstahl]]
- [[opencivil.nachweis.spannungsbegrenzung#Spannungsbegrenzung._protokoll_fliessen|Spannungsbegrenzung._protokoll_fliessen]]
- [[opencivil.spannungsanalyse#_herleitung|_herleitung]]

## Themen

- [[Betonstahl]]
- [[Stahlspannung aus Rissbreite]]
- [[Spannung-Dehnung-Analyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->
