---
erzeugt: 642b45c9472d
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.1.5.1.5"
---
> [!info] Normstelle
> SIA 262:2025, 4.1.5.1.5

*In der Herleitung: «Spannglied 1: Vordehnung, mit dem Modul der Litzen»*

$$
\varepsilon_{p,1} = \frac{\sigma_{p\infty,1}}{E_p^{\mathrm{Litze}}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\sigma_{p\infty,1}$ | Spannung nach allen Verlusten, Spannglied 1 | N/mm² | [[Spannung im Spannglied]] |
| $E_p^{\mathrm{Litze}}$ | Elastizitätsmodul von Litzen | N/mm² | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\varepsilon_{p,1} = \frac{\sigma_{p\infty,1}}{E_p^{\mathrm{Litze}}} = \frac{1107\,\mathrm{N}/\mathrm{mm}^{2}}{195000\,\mathrm{N}/\mathrm{mm}^{2}} = 5.68\,\text{‰}
$$

## Im Code

- [[opencivil.querschnitt.spannglieder#Spannglieder._glied|Spannglieder._glied]]

## Themen

- [[Querschnittsanalyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Mit Verbund ist ein Spannglied schon gedehnt, bevor eine Last wirkt: um
seine Vordehnung $\varepsilon_p$ gegenüber dem Beton an seiner Stelle
(SIA 262:2025, 4.1.5.1.5). Bei der Dehnung null des Querschnitts trägt es
darum $\sigma_{p\infty}$, und jede weitere Dehnung kommt dazu
([[Spannglied im Querschnitt]]). Der Modul ist der des Erzeugnisses:
195 kN/mm² für Litzen, 200 kN/mm² für Drähte und Stäbe (3.3.2.4). Vier
Litzen aus Y1860 nach Vorgabe: 1107/195 000 = 5.68 ‰.

Genau genommen kommt zu $\sigma_{p\infty}/E_p$ noch die Stauchung, die die
Vorspannung im Beton an der Stelle des Glieds weckt. Das Werkzeug lässt sie
weg (nach Vorgabe, nicht nachgeschlagen). Ohne Last trägt ein Glied darum
etwas weniger als $\sigma_{p\infty}$: im Rechteck 300 × 600 mm mit vier
Litzen 200 mm unter dem Schwerpunkt 1055 statt 1107 N/mm², knapp 5 %.
