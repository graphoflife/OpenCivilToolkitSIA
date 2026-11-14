---
erzeugt: f00b8d4817d5
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 3.1.2.2.2, (6)"
---
> [!info] Normstelle
> SIA 262:2025, 3.1.2.2.2, (6)

$$
f_{cm} = f_{ck} + 8\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $f_{ck}$ | Charakteristische Zylinderdruckfestigkeit | N/mm² | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
f_{cm} = f_{ck} + 8\,\mathrm{N}/\mathrm{mm}^{2} = 30\,\mathrm{N}/\mathrm{mm}^{2} + 8\,\mathrm{N}/\mathrm{mm}^{2} = 38\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Gebraucht von

- [[Mittelwert des Elastizitätsmoduls]]

## Im Code

- [[opencivil.material.beton]]

## Themen

- [[Beton]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

$f_{ck}$ ist ein Fraktilwert: 95 % der Prüfkörper sind fester. Für das
Verhalten im Mittel -- Steifigkeit, Verformung, Rissbildung -- zählt der
Mittelwert. Der feste Zuschlag von $8\,\mathrm{N/mm^2}$ entspricht bei normal
verteilter Festigkeit dem 1.645-fachen einer Standardabweichung von
$4.8\,\mathrm{N/mm^2}$, wie sie die Norm annimmt.

Das Werkzeug braucht $f_{cm}$ für den [[Mittelwert des Elastizitätsmoduls]].
