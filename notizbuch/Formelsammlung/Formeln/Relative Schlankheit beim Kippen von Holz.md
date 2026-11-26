---
erzeugt: 88ca97bf312e
art: formel
tags: [formel]
normstelle: "SIA 265:2012, 4.2.9.3, (40) und (41)"
---
> [!info] Normstelle
> SIA 265:2012, 4.2.9.3, (40) und (41)

*In der Herleitung: «Relative Schlankheit beim Kippen»*

$$
\lambda_{rel,m} = \sqrt{\frac{f_{m,k}}{\sigma_{m,crit}}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $f_{m,k}$ | Biegefestigkeit, kennzeichnend | N/mm² | Vorgabe |
| $\sigma_{m,crit}$ | Kippspannung | N/mm² | [[Kippspannung eines Rechtecks aus Holz]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\lambda_{rel,m} = \sqrt{\frac{f_{m,k}}{\sigma_{m,crit}}} = \sqrt{\frac{24\,\mathrm{N}/\mathrm{mm}^{2}}{112.8\,\mathrm{N}/\mathrm{mm}^{2}}} = 0.461
$$

## Gebraucht von

- [[Kippbeiwert des Holzes]]

## Im Code

- [[opencivil.nachweis.qa_holz_stabilitaet#_Herleitung|_Herleitung._kippen]]

## Themen

- [[Knicken und Kippen eines Holzstabs]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie beim Knicken ein Verhältnis zweier Spannungen: die kennzeichnende
Biegefestigkeit gegen die
[[Kippspannung eines Rechtecks aus Holz|Kippspannung]]. Unter 0.75 bricht
der Träger, bevor er kippt. Das Werkzeug rechnet sie mit den
kennzeichnenden Werten, ohne $\eta_w$ – nach Vorgabe, nicht
nachgeschlagen.
