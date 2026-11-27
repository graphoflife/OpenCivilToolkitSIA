---
erzeugt: 5a8c93b8498f
art: formel
tags: [formel]
normstelle: "SIA 264:2014, 5.3.5; SIA 264:2014, 5.3.4.6, (25)"
---
> [!info] Normstelle
> SIA 264:2014, 5.3.5; SIA 264:2014, 5.3.4.6, (25)

*In der Herleitung: «Zweiachsig: beide Achsen linear zusammen»*

$$
\sum \frac{M_{Ed,II}}{\mu_d\, M_{pl,Rd}} = \frac{M_{y,Ed,II}}{\mu_{d,y} \cdot M_{pl,y,Rd}} + \frac{M_{z,Ed,II}}{\mu_{d,z} \cdot M_{pl,z,Rd}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $M_{y,Ed,II}$ | Moment nach Theorie 2. Ordnung | kNm | [[Moment 2. Ordnung einer Verbundstütze]] |
| $\mu_{d,y}$ | Beiwert der Interaktion | – | [[Beiwert μ_d einer Verbundstütze]] |
| $M_{pl,y,Rd}$ | Plastischer Biegewiderstand | kNm | Zwischenwert |
| $M_{z,Ed,II}$ | Moment nach Theorie 2. Ordnung | kNm | [[Moment 2. Ordnung einer Verbundstütze]] |
| $\mu_{d,z}$ | Beiwert der Interaktion | – | [[Beiwert μ_d einer Verbundstütze]] |
| $M_{pl,z,Rd}$ | Plastischer Biegewiderstand | kNm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  \sum \frac{M_{Ed,II}}{\mu_d\, M_{pl,Rd}} &= \frac{M_{y,Ed,II}}{\mu_{d,y} \cdot M_{pl,y,Rd}} + \frac{M_{z,Ed,II}}{\mu_{d,z} \cdot M_{pl,z,Rd}} \\
  &= \frac{293.1\,\mathrm{kNm}}{0.996 \cdot 863.9\,\mathrm{kNm}} + \frac{290.5\,\mathrm{kNm}}{0.999 \cdot 644.3\,\mathrm{kNm}} \\
  &= 0.792
\end{aligned}
$$

## Im Code

- [[opencivil.nachweis.qa_verbund_stuetze#_Fall._zweiachsig|_Fall._zweiachsig]]

## Themen

- [[Verbundstütze]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wird die Stütze um beide Achsen gebogen, zählen die Ausnutzungen der
Achsen linear zusammen (5.3.5): je Achse das
[[Moment 2. Ordnung einer Verbundstütze|Moment 2. Ordnung]] durch
μ_d M_pl,Rd. Die Summe hält das Werkzeug gegen dieselbe Grenze wie (25),
0.9 oder 0.8 – nach Vorgabe, nicht nachgeschlagen, im [[TODO]]. Die
Ersatzimperfektion wirkt dabei in beiden Achsen.
