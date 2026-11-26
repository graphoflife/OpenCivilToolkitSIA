---
erzeugt: af1d7d626f8f
art: formel
tags: [formel]
normstelle: "nach Vorgabe, nicht nachgeschlagen"
---
> [!info] Normstelle
> nach Vorgabe, nicht nachgeschlagen

*In der Herleitung: «Spannungen nach Vorgabe, wo keine eingegeben ist»*

$$
\sigma_{p0} = 0.70 \cdot f_{pk} \qquad \sigma_{p\infty} = 0.85 \cdot \sigma_{p0}
$$

*In der Herleitung: «Spannglied 1: nach dem Spannen, nach Vorgabe»*

$$
\sigma_{p0,1} = 0.70 \cdot f_{pk}
$$

*In der Herleitung: «Spannglied 1: nach allen Verlusten, nach Vorgabe»*

$$
\sigma_{p\infty,1} = 0.85 \cdot \sigma_{p0,1}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $f_{pk}$ | Zugfestigkeit | N/mm² | Vorgabe |
| $\sigma_{p0,1}$ | Spannung nach dem Spannen, Spannglied 1 | N/mm² | – |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\sigma_{p0,1} = 0.70 \cdot f_{pk} = 0.70 \cdot 1860\,\mathrm{N}/\mathrm{mm}^{2} = 1302\,\mathrm{N}/\mathrm{mm}^{2}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\sigma_{p\infty,1} = 0.85 \cdot \sigma_{p0,1} = 0.85 \cdot 1302\,\mathrm{N}/\mathrm{mm}^{2} = 1107\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Gebraucht von

- [[Spannkraft eines Spannglieds]]
- [[Vordehnung eines Spannglieds]]

## Im Code

- [[opencivil.querschnitt.spannglieder#Spannglieder._glied|Spannglieder._glied]]
- [[opencivil.querschnitt.spannglieder#Spannglieder.rechne|Spannglieder.rechne]]

## Themen

- [[Querschnittsanalyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wo keine Spannung eingegeben ist, nimmt das Werkzeug nach dem Spannen
$\sigma_{p0} = 0.70 \cdot f_{pk}$ und nach allen Verlusten
$\sigma_{p\infty} = 0.85 \cdot \sigma_{p0}$, also 15 % Verlust. Bei Y1860
sind das 1302 und 1107 N/mm². Beide Zahlen hat der Benutzer am 2026-11-25
vorgegeben; nachgeschlagen sind sie nicht. Die Verluste aus Reibung,
Schlupf, Schwinden, Kriechen und Relaxation hängen am Bauwerk und am
Spannsystem (SIA 262:2025, 4.1.5.3), und die Vorgabe ersetzt ihre Rechnung
nicht. Eine eingegebene Zahl gilt, wie sie ist.

Bei den Stäben Y1100 und Y1030 liegt schon die Vorgabe über der Grenze nach
dem Spannen, 770 über 765 und 721 über 705.5 N/mm² – siehe
[[Grenzen der Spannung im Spannstahl]]. Ob die Vorgabe dort tiefer liegen
soll, ist offen ([[TODO]]).
