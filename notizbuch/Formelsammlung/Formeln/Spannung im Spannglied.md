---
erzeugt: a3364045af9c
art: formel
tags: [formel]
normstelle: ["nach Vorgabe, nicht nachgeschlagen", "SIA 262:2025, 4.1.5.3"]
---
> [!info] Normstellen
> nach Vorgabe, nicht nachgeschlagen · SIA 262:2025, 4.1.5.3

*In der Herleitung: «Spannungen nach dem Spannen und nach allen Verlusten, aus den Faktoren des Glieds»*

$$
\sigma_{p0} = k_{p0} \cdot f_{pk} \qquad \sigma_{p\infty} = k_{p\infty} \cdot \sigma_{p0}
$$

*In der Herleitung: «Spannglied 1: nach dem Spannen, nach Vorgabe»*

$$
\sigma_{p0,1} = k_{p0,1} \cdot f_{pk}
$$

*In der Herleitung: «Spannglied 1: nach allen Verlusten, nach Vorgabe»*

$$
\sigma_{p\infty,1} = k_{p\infty,1} \cdot \sigma_{p0,1}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $k_{p0,1}$ | Anteil von f\_pk nach dem Spannen | – | Zwischenwert |
| $f_{pk}$ | Zugfestigkeit | N/mm² | Vorgabe |
| $k_{p\infty,1}$ | Anteil von σ\_p0 nach allen Verlusten | – | Zwischenwert |
| $\sigma_{p0,1}$ | Spannung nach dem Spannen, Spannglied 1 | N/mm² | – |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\sigma_{p0,1} = k_{p0,1} \cdot f_{pk} = 0.7 \cdot 1860\,\mathrm{N}/\mathrm{mm}^{2} = 1302\,\mathrm{N}/\mathrm{mm}^{2}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\sigma_{p\infty,1} = k_{p\infty,1} \cdot \sigma_{p0,1} = 0.85 \cdot 1302\,\mathrm{N}/\mathrm{mm}^{2} = 1107\,\mathrm{N}/\mathrm{mm}^{2}
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

Ein Spannglied wird nicht mit seinen Spannungen beschrieben, sondern mit
zwei Faktoren. $k_{p0}$ gibt die Spannung nach dem Spannen als Anteil der
Zugfestigkeit, $\sigma_{p0} = k_{p0} \cdot f_{pk}$; $k_{p\infty}$ gibt den
Anteil, der davon nach allen Verlusten bleibt,
$\sigma_{p\infty} = k_{p\infty} \cdot \sigma_{p0}$. Beide sind höchstens 1:
über $f_{pk}$ lässt sich nicht spannen, und die Verluste mindern die
Spannung.

Ein neues Glied beginnt mit 0.70 und 0.85, also 15 % Verlust. Bei Y1860
sind das 1302 und 1107 N/mm². Beide Zahlen hat der Benutzer am 2026-11-25
vorgegeben; nachgeschlagen sind sie nicht. Die Verluste aus Reibung,
Schlupf, Schwinden, Kriechen und Relaxation hängen am Bauwerk und am
Spannsystem (SIA 262:2025, 4.1.5.3), und die Vorgabe ersetzt ihre Rechnung
nicht.

Bis 2026-11-27 waren $\sigma_{p0}$ und $\sigma_{p\infty}$ selbst die Felder,
leer galt die Vorgabe. Mit den Faktoren folgt die Spannung einem Wechsel
der Sorte, und das Zeichenfenster zeigt sie gerechnet hinter dem Feld:
«σ_p0 = 0.70 · f_pk = 1302 N/mm²».

Bei den Stäben Y1100 und Y1030 liegt schon die Vorgabe über der Grenze nach
dem Spannen, 770 über 765 und 721 über 705.5 N/mm² – siehe
[[Grenzen der Spannung im Spannstahl]]. Ob die Vorgabe dort tiefer liegen
soll, ist offen ([[TODO]]); bis dahin hält ein kleinerer Faktor die Grenze,
etwa 0.65.
