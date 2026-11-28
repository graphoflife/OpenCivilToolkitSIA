---
erzeugt: 35778b264393
art: formel
tags: [formel]
normstelle: "SIA 266:2015, 4.3.4.1, Gl. (20)"
---
> [!info] Normstelle
> SIA 266:2015, 4.3.4.1, Gl. (20)

*In der Herleitung: «Durchbiegung der Wand als waagrechter Streifen zwischen den Rändern, elastisch und ungerissen, mit E\_xd»*

$$
w_d = \frac{5 \cdot p_d \cdot L^{4}}{32 \cdot E_{xd} \cdot t_w^{3}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $p_d$ | Querlast der Kombination, Betrag | kN/m² | Zwischenwert |
| $L$ | Spannweite des waagrechten Gewölbes | m | Zwischenwert |
| $E_{xd}$ | Elastizitätsmodul der Wand | N/mm² | Zwischenwert |
| $t_w$ | Dicke der Wand | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
w_d = \frac{5 \cdot p_d \cdot L^{4}}{32 \cdot E_{xd} \cdot t_w^{3}} = \frac{5 \cdot 1.5\,\mathrm{kN}/\mathrm{m}^{2} \cdot \left(2.4\,\mathrm{m}\right)^{4}}{32 \cdot 2975\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(175\,\mathrm{mm}\right)^{3}} = 0.49\,\mathrm{mm}
$$

## Im Code

- [[opencivil.mauerwerk.querlast#Querlastnachweis._waagrecht|Querlastnachweis._waagrecht]]

## Themen

- [[Mauerwerk]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Nach 4.3.4.1 darf eine Wand unter Querlast ohne Effekte 2. Ordnung
gerechnet werden, wenn zwei Bedingungen gelten: Sie ist höchstens 15-mal so
hoch wie dick, Gl. (19), und ihre Durchbiegung $w_d$ bleibt unter 0.002
der Länge $h_{cr}$, Gl. (20). $w_d$ kommt aus der Elastizitätstheorie
1. Ordnung, mit Bemessungswerten.

Das waagrechte Gewölbe ist ohne Effekte 2. Ordnung gerechnet. Das Werkzeug
prüft darum beide Bedingungen, mit der Spannweite $L$ von Rand zu Rand an
der Stelle der Höhe – nach Vorgabe, nicht nachgeschlagen. Ein Streifen von
1 m Höhe ist ein einfacher Balken über $L$, ungerissen, mit
$I = t_w^3/12$ je Meter und $E_{xd}$ nach Gl. (5):
$w_d = 5\, p_d\, L^4/(384\, E_{xd}\, I)$, gekürzt die Formel oben. Hält
eine der beiden Bedingungen nicht, zählt das waagrechte Gewölbe nicht.

Beispiel: die Wand zwischen Querwänden im Prüfprojekt, $L$ = 2.4 m und
$t_w$ = 175 mm. $L/t_w$ = 13.7 ist kleiner als 15, und unter 1.5 kN/m²
biegt sie sich um 0.49 mm, weit unter 0.002 · 2400 mm = 4.8 mm: Das
waagrechte Gewölbe zählt.
