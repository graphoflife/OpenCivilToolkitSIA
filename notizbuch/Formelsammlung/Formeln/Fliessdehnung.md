---
erzeugt: 608d0ddf370b
art: formel
tags: [formel]
normstelle: ["SIA 262:2025, 4.2.2.2, Figur 16", "SIA 262:2025, 4.3.3.2.2, (38)", "SIA 263:2013, 3.2.2.4", "SIA 262:2025, 4.2.3.3, Figur 17"]
---
> [!info] Normstellen
> SIA 262:2025, 4.2.2.2, Figur 16 · SIA 262:2025, 4.3.3.2.2, (38) · SIA 263:2013, 3.2.2.4 · SIA 262:2025, 4.2.3.3, Figur 17

*In der Herleitung: «Fliessdehnung (Bemessungswert)»*

$$
\varepsilon_{yd} = \frac{f_{yd}}{E_s}
$$

*In der Herleitung: «Fliessdehnung des Baustahls»*

$$
\varepsilon_y = \frac{f_y}{E_a}
$$

*In der Herleitung: «Fliessdehnung von Drähten und Stäben (Bemessungswert)»*

$$
\varepsilon_{pd} = \frac{f_{pd}}{E_p}
$$

*In der Herleitung: «Fliessdehnung von Litzen (Bemessungswert)»*

$$
\varepsilon_{pd}^{\mathrm{Litze}} = \frac{f_{pd}}{E_p^{\mathrm{Litze}}}
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
| $f_y$ | Streckgrenze | N/mm² | Vorgabe |
| $E_a$ | Elastizitätsmodul des Baustahls | N/mm² | Vorgabe |
| $f_{pd}$ | Bemessungswert der Fliessgrenze | N/mm² | [[Bemessungswert der Fliessgrenze]] |
| $E_p$ | Elastizitätsmodul von Drähten und Stäben | N/mm² | Vorgabe |
| $E_p^{\mathrm{Litze}}$ | Elastizitätsmodul von Litzen | N/mm² | Vorgabe |
| $f_{yk}$ | Charakteristische Fliessgrenze | N/mm² | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\varepsilon_{yd} = \frac{f_{yd}}{E_s} = \frac{435\,\mathrm{N}/\mathrm{mm}^{2}}{200000\,\mathrm{N}/\mathrm{mm}^{2}} = 0.217\,\%
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\varepsilon_y = \frac{f_y}{E_a} = \frac{355\,\mathrm{N}/\mathrm{mm}^{2}}{210000\,\mathrm{N}/\mathrm{mm}^{2}} = 1.69\,\text{‰}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\varepsilon_{pd} = \frac{f_{pd}}{E_p} = \frac{1391\,\mathrm{N}/\mathrm{mm}^{2}}{200000\,\mathrm{N}/\mathrm{mm}^{2}} = 0.696\,\%
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\varepsilon_{pd}^{\mathrm{Litze}} = \frac{f_{pd}}{E_p^{\mathrm{Litze}}} = \frac{1391\,\mathrm{N}/\mathrm{mm}^{2}}{195000\,\mathrm{N}/\mathrm{mm}^{2}} = 0.713\,\%
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\varepsilon_y = \frac{f_{yk}}{E_s} = \frac{500\,\mathrm{N}/\mathrm{mm}^{2}}{200000\,\mathrm{N}/\mathrm{mm}^{2}} = 2.5\,\text{‰} \quad < \quad \varepsilon_{s,x} = 3.47\,\text{‰}
$$

## Gebraucht von

- [[Beiwert für den Querkraftwiderstand]]
- [[Grenzdehnung des Baustahls]]

## Im Code

- [[opencivil.material.baustahl]]
- [[opencivil.material.betonstahl]]
- [[opencivil.material.spannstahl]]
- [[opencivil.nachweis.kennzahlen#Plattenkennzahlen|Plattenkennzahlen._ohne_buegel]]
- [[opencivil.nachweis.spannungsbegrenzung#Spannungsbegrenzung._protokoll_fliessen|Spannungsbegrenzung._protokoll_fliessen]]
- [[opencivil.spannungsanalyse.riss#Bruttoriss.herleitung_gesetze|Bruttoriss.herleitung_gesetze]]

## Themen

- [[Betonstahl]]
- [[Kennzahlen]]
- [[Baustahl]]
- [[Spannstahl]]
- [[Stahlspannung aus Rissbreite]]
- [[Spannung-Dehnung-Analyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Dehnung, bei der der Stahl zu fliessen beginnt: Fliessgrenze geteilt durch
den Elastizitätsmodul. Für B500B mit Bemessungswerten rund 2.17 ‰,
charakteristisch 2.5 ‰. Darunter ist die Stahlspannung $E_s \cdot
\varepsilon_s$, darüber bleibt sie am Plateau.

Beim Betonstahl wird sie an vier Stellen gebraucht:

- als Kennwert des Betonstahls, mit Bemessungswerten;
- in der Spannung-Dehnung-Analyse als Fliessbeginn: erreicht die am stärksten
  gezogene Lage diese Dehnung, knickt die Linie ab;
- in der Stahlspannungsbegrenzung: fliesst der Stahl unter der Einwirkung,
  bliebe seine Spannung am Plateau stehen und sagte nichts mehr -- verglichen
  wird dann über die Dehnung (siehe [[Zulässige Dehnung]]);
- in den [[Kennzahlen]] als
  [[Nominelle Dehnung der Zugbewehrung|nominelle Dehnung der Zugbewehrung]]
  beim Biegewiderstand: daraus der kleinste Querkraftwiderstand ohne Bügel,
  solange die Bewehrung elastisch bleibt.

Beim Baustahl ist sie Kennwert, aus Streckgrenze und $E_a$: für S355
1.69 ‰. Plastisch rechnen darf nach SIA 263:2013, 3.2.2.4, wessen
Bruchdehnung über 15 % liegt und mindestens 15-mal so gross ist wie die
Fliessdehnung, und wessen Zugfestigkeit mindestens das 1.1-Fache der
Streckgrenze ist -- die Sorten der Tabelle 1 erfüllen das. Das 15-Fache ist
darum die [[Grenzdehnung des Baustahls]].
