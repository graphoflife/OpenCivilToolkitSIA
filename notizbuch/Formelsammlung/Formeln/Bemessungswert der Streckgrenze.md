---
erzeugt: 5c086c0d63aa
art: formel
tags: [formel]
normstelle: ["SIA 263:2013, 4.1.1, (1); 4.1.3", "SIA 264:2014, 4.1.3, (1); 4.1.5"]
---
> [!info] Normstellen
> SIA 263:2013, 4.1.1, (1); 4.1.3 · SIA 264:2014, 4.1.3, (1); 4.1.5

*In der Herleitung: «Bemessungswert der Streckgrenze»*

$$
f_{yd} = \frac{f_{y}}{\gamma_{M1}}
$$

*In der Herleitung: «Bemessungswert der Streckgrenze»*

$$
f_{ypd} = \frac{f_{yp}}{\gamma_{ap}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $f_{y}$ | Streckgrenze | N/mm² | Vorgabe |
| $\gamma_{M1}$ | Widerstandsbeiwert für Festigkeits- und Stabilitätsnachweise | – | Vorgabe |
| $f_{yp}$ | Streckgrenze des Profilblechstahls | N/mm² | Vorgabe |
| $\gamma_{ap}$ | Widerstandsbeiwert des Profilblechstahls | – | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
f_{yd,\text{S355}} = \frac{f_{y,\text{S355}}}{\gamma_{M1,\text{S355}}} = \frac{355\,\mathrm{N}/\mathrm{mm}^{2}}{1.05} = 338\,\mathrm{N}/\mathrm{mm}^{2}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
f_{ypd} = \frac{f_{yp}}{\gamma_{ap}} = \frac{350\,\mathrm{N}/\mathrm{mm}^{2}}{1.05} = 333\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Im Code

- [[opencivil.material.baustahl]]
- [[opencivil.material.profilblech]]

## Themen

- [[Baustahl]]
- [[Profilblechstahl]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Beim Baustahl heisst die Fliessgrenze Streckgrenze, $f_y$. SIA 263:2013
teilt jeden charakteristischen Widerstand durch einen Widerstandsbeiwert
(4.1.1, Gleichung (1)); für Festigkeits- und Stabilitätsnachweise ist das
$\gamma_{M1} = 1.05$ (4.1.3). Für S355 bis 40 mm Dicke gibt das 338 N/mm².

$f_{yd}$ ist das Plateau der elastisch-plastischen Beziehung des Baustahls --
in Zug und Druck dasselbe, anders als beim Betonstahl, der auf Druck eine
eigene Fliessgrenze haben darf ([[Bemessungswert der Fliessgrenze auf Druck]]).
Gerechnet wird mit der Streckgrenze bis 40 mm Dicke; die kleinere darüber
steht als eigener Kennwert in der Sortentabelle, denn welche gilt, hängt am
Erzeugnis, nicht am Material.
