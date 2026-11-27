---
erzeugt: d2bc0e4be9c4
art: formel
tags: [formel]
normstelle: ["SIA 262:2025, 4.1.5.2.2, (22); SIA 262:2025, 4.1.5.2.3", "SIA 262:2025, 4.1.5.2.2, (22)", "SIA 262:2025, 4.1.5.2.3"]
---
> [!info] Normstellen
> SIA 262:2025, 4.1.5.2.2, (22); SIA 262:2025, 4.1.5.2.3 · SIA 262:2025, 4.1.5.2.2, (22) · SIA 262:2025, 4.1.5.2.3

*In der Herleitung: «Grenzen der Spannung nach dem Spannen und nach allen Verlusten»*

$$
\sigma_{p0} \le \min\left(0.75 \cdot f_{pk};\ 0.85 \cdot f_{p0.1k}\right) \qquad \sigma_{p\infty} \ge 0.45 \cdot f_{pk}
$$

*In der Herleitung: «Spannglied 1: Grenze nach dem Spannen»*

$$
\sigma_{p,max} = \min\left(0.75 \cdot f_{pk};\ 0.85 \cdot f_{p0.1k}\right)
$$

*In der Herleitung: «Spannglied 1: Mindestspannung nach allen Verlusten»*

$$
\sigma_{p,min} = 0.45 \cdot f_{pk}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $f_{pk}$ | Zugfestigkeit | N/mm² | Vorgabe |
| $f_{p0.1k}$ | Fliessgrenze (0.1-%-Dehngrenze) | N/mm² | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  \sigma_{p,max} &= \min\left(0.75 \cdot f_{pk};\ 0.85 \cdot f_{p0.1k}\right) \\
  &= \min\left(0.75 \cdot 1860\,\mathrm{N}/\mathrm{mm}^{2};\ 0.85 \cdot 1600\,\mathrm{N}/\mathrm{mm}^{2}\right) \\
  &= 1360\,\mathrm{N}/\mathrm{mm}^{2} \quad \ge \quad \sigma_{p0,1} = 1302\,\mathrm{N}/\mathrm{mm}^{2}
\end{aligned}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\sigma_{p,min} = 0.45 \cdot f_{pk} = 0.45 \cdot 1860\,\mathrm{N}/\mathrm{mm}^{2} = 837\,\mathrm{N}/\mathrm{mm}^{2} \quad \le \quad \sigma_{p\infty,1} = 1107\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Im Code

- [[opencivil.querschnitt.spannglieder#Spannglieder._glied|Spannglieder._glied]]
- [[opencivil.querschnitt.spannglieder#Spannglieder.rechne|Spannglieder.rechne]]

## Themen

- [[Querschnittsanalyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Unmittelbar nach dem Spannen darf die Spannung im Spannstahl
$\min(0.75 \cdot f_{pk};\ 0.85 \cdot f_{p0.1k})$ nicht übersteigen
(SIA 262:2025, 4.1.5.2.2, Gleichung (22)); nach allen Verlusten sollen
mindestens $0.45 \cdot f_{pk}$ bleiben (4.1.5.2.3). Bei Y1860 sind das
$\min(1395;\ 1360)$ = 1360 N/mm² und 837 N/mm². Dass $\sigma_{p\infty}$
nicht über $\sigma_{p0}$ liegt, prüft schon das Feld: der Faktor
$k_{p\infty}$ ist höchstens 1. Bis 2026-11-27 meldete es ein roter Hinweis.

Liegt eine Spannung ausserhalb, sagt es ein roter Hinweis am Glied und in
der Herleitung. Gerechnet wird trotzdem mit den Faktoren des Benutzers –
sie werden nie still umgedeutet. Die Vorgabe $0.70 \cdot f_{pk}$
([[Spannung im Spannglied]]) hält die Grenze bei allen Sorten ausser den
Stäben Y1100 und Y1030.
