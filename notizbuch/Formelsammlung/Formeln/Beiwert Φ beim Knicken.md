---
erzeugt: 787fd00b7edd
art: formel
tags: [formel]
normstelle: "SIA 263:2013, 4.5.1.3, (7); 4.5.1.4, (8); Tabelle 8"
---
> [!info] Normstelle
> SIA 263:2013, 4.5.1.3, (7); 4.5.1.4, (8); Tabelle 8

*In der Herleitung: «Beiwert um y»*

$$
\Phi_{K,y} = 0.5 \cdot \left(1 + \alpha_{K,y} \cdot \left(\bar{\lambda}_{K,y} - 0.2\right) + \bar{\lambda}_{K,y}^2\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\alpha_{K,y}$ | Imperfektionsbeiwert der Knickspannungskurve | – | Zwischenwert |
| $\bar{\lambda}_{K,y}$ | Schlankheit beim Knicken | – | [[Schlankheit beim Knicken]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  \Phi_{K,y} &= 0.5 \cdot \left(1 + \alpha_{K,y} \cdot \left(\bar{\lambda}_{K,y} - 0.2\right) + \bar{\lambda}_{K,y}^2\right) \\
  &= 0.5 \cdot \left(1 + 0.21 \cdot \left(0.323 - 0.2\right) + 0.323^2\right) \\
  &= 0.565
\end{aligned}
$$

## Gebraucht von

- [[Abminderungsfaktor beim Knicken und Kippen]]

## Im Code

- [[opencivil.nachweis.qa_stahl_stabilitaet#_Herleitung.knicken|_Herleitung.knicken]]

## Themen

- [[Knicken und Kippen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

$\Phi$ ist eine Hilfsgrösse für den
[[Abminderungsfaktor beim Knicken und Kippen]]. In ihr steckt die
Imperfektion des Stabs: $\alpha_K$ wächst mit der Krümmung, der Schiefe
und den Eigenspannungen, mit denen man bei der Form des Querschnitts
rechnen muss. Figur 7 ordnet jedem Querschnitt eine von vier
Knickspannungskurven zu, a bis d; Tabelle 8 gibt ihr $\alpha_K$, von
0.21 bis 0.76.

Bis $\bar{\lambda}_K = 0.2$ wird nichts abgemindert. Darüber wächst
$\Phi$ mit der Schlankheit und mit $\alpha_K$, und mit ihm sinkt $\chi$.
