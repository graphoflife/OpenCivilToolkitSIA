---
erzeugt: 989878cc1f4d
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.1.2; 4.4.3.2.4"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.1.2; 4.4.3.2.4

*In der Herleitung: «Moment aus der Vorspannung um y»*

$$
M_{p,y} = \left(P_{\infty,1} \cdot z'_{p,1} + P_{\infty,2} \cdot z'_{p,2}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $P_{\infty,1}$ | Spannkraft nach allen Verlusten, Spannglied 1 | kN | [[Spannkraft eines Spannglieds]] |
| $z'_{p,1}$ | Lage von Spannglied 1, vom Schwerpunkt aus | mm | Zwischenwert |
| $P_{\infty,2}$ | Spannkraft nach allen Verlusten, Spannglied 2 | kN | [[Spannkraft eines Spannglieds]] |
| $z'_{p,2}$ | Lage von Spannglied 2, vom Schwerpunkt aus | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  M_{p,y} &= \left(P_{\infty,1} \cdot z'_{p,1} + P_{\infty,2} \cdot z'_{p,2}\right) \\
  &= \left(664\,\mathrm{kN} \cdot \left(-280\,\mathrm{mm}\right) + 308\,\mathrm{kN} \cdot \left(-240\,\mathrm{mm}\right)\right) \\
  &= -259.8\,\mathrm{kNm}
\end{aligned}
$$

## Gebraucht von

- [[Spannung aus der Vorspannung an der Ecke]]

## Im Code

- [[opencivil.nachweis.rissgroessen#protokoll_vorspannung|protokoll_vorspannung]]

## Themen

- [[Sprödes Versagen je Richtung]]
- [[Zwängung auf Biegung]]
- [[Spannung-Dehnung-Analyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Kraft jedes Glieds mit Vordehnung mal seinem Abstand vom Schwerpunkt
des Bruttoquerschnitts: um y mit seiner Lage $z'$, um z mit $y'$. Liegt ein
Glied unter dem Schwerpunkt, ist $M_{p,y}$ negativ – es drückt den unteren
Rand, genau den, den ein positives Moment aufreisst. Einachsig zählt nur
das Moment um y, wie bei jeder Einwirkung.

Im Rechteck 300 × 600 mm mit vier Litzen 200 mm unter dem Schwerpunkt ist
$M_{p,y}$ = 664 kN · (−200 mm) = −132.8 kNm.
