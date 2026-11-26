---
erzeugt: 9255bf39f970
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.1.2; 4.4.3.2.4"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.1.2; 4.4.3.2.4

$$
N_p = -\left(P_{\infty,1} + P_{\infty,2}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $P_{\infty,1}$ | Spannkraft nach allen Verlusten, Spannglied 1 | kN | [[Spannkraft eines Spannglieds]] |
| $P_{\infty,2}$ | Spannkraft nach allen Verlusten, Spannglied 2 | kN | [[Spannkraft eines Spannglieds]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
N_p = -\left(P_{\infty,1} + P_{\infty,2}\right) = -\left(664\,\mathrm{kN} + 308\,\mathrm{kN}\right) = -972\,\mathrm{kN}
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

Die Glieder mit Vordehnung drücken den Beton mit ihrer
[[Spannkraft eines Spannglieds|Kraft nach allen Verlusten]], mit wie ohne
Verbund: zusammen die Normalkraft $N_p$, Druck negativ. Sie wirkt am
ungerissenen Bruttoquerschnitt und zählt beim Rissmoment mit, beim spröden
Versagen und bei der Zwängung (SIA 262:2025, 4.3.1.2; 4.4.3.2.4). Ein
schlaff angesetztes Glied zählt hier nicht: seine Vorspannung steht schon
in den Lastfällen.
