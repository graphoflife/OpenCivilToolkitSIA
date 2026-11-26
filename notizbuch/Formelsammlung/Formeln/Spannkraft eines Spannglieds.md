---
erzeugt: cfb25778120c
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 3.3.2.2, Tabelle 7; SIA 262:2025, 4.1.5.1.5"
---
> [!info] Normstelle
> SIA 262:2025, 3.3.2.2, Tabelle 7; SIA 262:2025, 4.1.5.1.5

*In der Herleitung: «Querschnitt, Vordehnung und Spannkraft eines Glieds aus n Drähten, Litzen oder Stäben»*

$$
A_p = n \cdot a_p \qquad \varepsilon_p = \frac{\sigma_{p\infty}}{E_p} \qquad P_\infty = A_p \cdot \sigma_{p\infty}
$$

*In der Herleitung: «Spannglied 1: Spannkraft nach allen Verlusten»*

$$
P_{\infty,1} = A_{p,1} \cdot \sigma_{p\infty,1}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $A_{p,1}$ | Querschnitt des Spannstahls, Spannglied 1 | mm² | [[Querschnitt eines Spannglieds]] |
| $\sigma_{p\infty,1}$ | Spannung nach allen Verlusten, Spannglied 1 | N/mm² | [[Spannung im Spannglied nach Vorgabe]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
P_{\infty,1} = A_{p,1} \cdot \sigma_{p\infty,1} = 600\,\mathrm{mm}^{2} \cdot 1107\,\mathrm{N}/\mathrm{mm}^{2} = 664\,\mathrm{kN}
$$

## Gebraucht von

- [[Moment aus der Vorspannung]]
- [[Normalkraft aus der Vorspannung]]

## Im Code

- [[opencivil.querschnitt.spannglieder#Spannglieder._glied|Spannglieder._glied]]
- [[opencivil.querschnitt.spannglieder#Spannglieder.rechne|Spannglieder.rechne]]

## Themen

- [[Querschnittsanalyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Kraft eines Glieds nach allen Verlusten. Im Widerstand zählt sie über
das Gesetz des Glieds ([[Spannglied im Querschnitt]]) – die Zugkraft im
Spannstahl ist ein Teil des Widerstands (SIA 262:2025, 4.1.5.5.1). Die
Lastfälle stehen darum ohne Vorspannung da. Am Bruttoquerschnitt drückt sie
den Beton schon ohne Last, als [[Normalkraft aus der Vorspannung]] und
[[Moment aus der Vorspannung]]; so geht sie ins Rissmoment ein.

Vier Litzen ⌀15.7 aus Y1860 nach Vorgabe: 600 mm² · 1107 N/mm² = 664 kN.
