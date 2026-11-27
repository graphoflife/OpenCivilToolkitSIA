---
erzeugt: 269d84e63d10
art: formel
tags: [formel]
normstelle: ["SIA 263:2013, 4.5.1.3, (7); 4.5.1.4, (8); Tabelle 8", "SIA 263:2013, 4.5.2.2, (9); 4.5.2.3, (10)"]
---
> [!info] Normstellen
> SIA 263:2013, 4.5.1.3, (7); 4.5.1.4, (8); Tabelle 8 · SIA 263:2013, 4.5.2.2, (9); 4.5.2.3, (10)

*In der Herleitung: «Abminderung um y»*

$$
\chi_{K,y} = \min\left(1;\ \frac{1}{\Phi_{K,y} + \sqrt{\Phi_{K,y}^2 - \bar{\lambda}_{K,y}^2}}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\Phi_{K,y}$ | Beiwert beim Knicken | – | [[Beiwert Φ beim Knicken]] |
| $\bar{\lambda}_{K,y}$ | Schlankheit beim Knicken | – | [[Schlankheit beim Knicken]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  \chi_{K,y} &= \min\left(1;\ \frac{1}{\Phi_{K,y} + \sqrt{\Phi_{K,y}^2 - \bar{\lambda}_{K,y}^2}}\right) \\
  &= \min\left(1;\ \frac{1}{0.565 + \sqrt{0.565^2 - 0.323^2}}\right) \\
  &= 0.972
\end{aligned}
$$

## Gebraucht von

- [[Kippwiderstand]]
- [[Knickwiderstand]]
- [[Knickwiderstand einer Verbundstütze]]

## Im Code

- [[opencivil.nachweis.qa_stahl_stabilitaet#_Herleitung.kippen|_Herleitung.kippen]]
- [[opencivil.nachweis.qa_stahl_stabilitaet#_Herleitung.knicken|_Herleitung.knicken]]
- [[opencivil.nachweis.qa_verbund_stuetze#_Fall|_Fall._knicken]]

## Themen

- [[Knicken und Kippen]]
- [[Verbundstütze]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ein wirklicher Stab ist nie ganz gerade und nie frei von
Eigenspannungen. Er erreicht darum weder die Fliesslast noch die
[[Knicklast nach Euler]], sondern weniger – und am meisten fehlt dort, wo
beide gleich gross sind. Der Abminderungsfaktor $\chi$ fasst das in
einer Kurve über der bezogenen Schlankheit zusammen: für gedrungene
Stäbe eins, darüber fallend, für schlanke nahe an der Kurve nach Euler.

Dieselbe Formel gilt beim Knicken (8) und beim Kippen (10). Was sich
unterscheidet, sind der Beiwert $\Phi$ – siehe [[Beiwert Φ beim Knicken]]
und [[Beiwert Φ beim Kippen]] – und die Schlankheit, bis zu der nichts
abgemindert wird.
