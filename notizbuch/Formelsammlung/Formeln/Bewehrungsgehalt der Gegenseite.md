---
erzeugt: f23219c56650
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.4.3.2.5, (104)"
---
> [!info] Normstelle
> SIA 262:2025, 4.4.3.2.5, (104)

*In der Herleitung: «Bewehrungsgehalt der Gegenseite, Zug unten»*

$$
\rho'_{u} = \frac{A_{s,3,x,g}}{b \cdot d_{2,x}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $A_{s,3,x,g}$ | – | mm² | Zwischenwert |
| $b$ | Betrachtete Breite (x) | mm | Vorgabe |
| $d_{2,x}$ | – | mm | [[Statische Höhe]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\rho'_{u} = \frac{A_{s,3,x,g}}{b \cdot d_{2,x}} = \frac{754\,\mathrm{mm}^{2}}{1000\,\mathrm{mm} \cdot 248.1\,\mathrm{mm}} = 0.00304
$$

## Gebraucht von

- [[Vergrösserungsfaktor der Durchbiegung]]

## Im Code

- [[opencivil.nachweis.verformung#Vergroesserungsfaktor.rechne|Vergroesserungsfaktor.rechne]]

## Themen

- [[Verformung]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Bewehrung der Seite gegenüber der gezogenen, im Verhältnis zu
$b \cdot d$ der gezogenen Seite: SIA 262, 4.4.3.2.5 bezieht beide Gehalte
des [[Vergrösserungsfaktor der Durchbiegung|Vergrösserungsfaktors]] auf die
statische Höhe des Bauteils. Bis 2026-11-14 teilte das Werkzeug durch das
$d$ der Gegenseite; im Beispiel wurde $\omega_w'$ dadurch 7.52 statt 7.55.
Ohne Bewehrung auf der Gegenseite ist $\rho' = 0$.
