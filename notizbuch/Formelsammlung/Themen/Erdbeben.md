---
erzeugt: 0613869c09d1
art: thema
tags: [thema]
---
> [!abstract] Erdbeben
> 16 Formeln, in der Folge, in der gerechnet wird.

## Was die Rechnung dazu sagt

Getrennte Teile des Kerns verbinden nur die Decken: jeder biegt sich um seinen eigenen Schwerpunkt, und ihre Trägheitsmomente werden addiert, ohne Steiner-Anteil zwischen ihnen. Innerhalb eines Teils bleibt er – seine Wände sind fest verbunden und biegen sich gemeinsam.

Das Beben wird durch waagrechte Kräfte ersetzt: je Hauptrichtung eine Ersatzkraft aus dem Bemessungsspektrum bei der Grundschwingzeit, verteilt auf die Geschosse nach Höhe und Gewicht. Der Kern trägt sie als Kragarm, eingespannt am Fuss, in jedem Geschoss mit dessen Biegesteifigkeit; getrennte Teile am Fuss je nach ihrem Anteil daran.

## Formeln

1. [[Trägheitsmomente des Kerns]]
2. [[Gewicht eines Geschosses]]
3. [[Gewicht des Gebäudes]]
4. [[Biegesteifigkeit des Kerns]]
5. [[Auslenkung aus einem Geschoss]]
6. [[Auslenkung des Dachs]]
7. [[Grundschwingzeit]]
8. [[Bemessungsspektrum (32)]]
9. [[Ersatzkraft]]
10. [[Ersatzkraft eines Geschosses]]
11. [[Kippmoment am Fuss]]
12. [[Grenze der Grundschwingzeit]]
13. [[Erfüllungsgrad]]
14. [[Bemessungsspektrum (31)]]
15. [[Bemessungsspektrum (33)]]
16. [[Bemessungsspektrum (34)]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das Ersatzkraftverfahren nach SIA 261:2020, 16.5.2, für ein Gebäude aus
Geschossen, jedes mit seinem Kern aus Beton. Je Hauptrichtung ein ebenes
Modell: der Kern als Kragarm, am Fuss eingespannt, die Decken starr in ihrer
Ebene. Den Kern zeichnet man in einer Querschnittsanalyse, ganz, mit allen
Wänden in $x$ und in $y$, wie er im Grundriss liegt; je Geschoss darf es ein
anderer sein, oben etwa ein dünnerer. Aus den Gewichten und der
[[Biegesteifigkeit des Kerns]] in jedem Geschoss folgt die
[[Grundschwingzeit]], aus ihr das Spektrum, die [[Ersatzkraft]] und ihre
Verteilung auf die Geschosse und am Fuss auf die getrennten Teile des
Kerns.

Ob das Verfahren gilt, ist ein Urteil wie ein Nachweis: $T_1 \le 4 \cdot
T_C$ in beiden Richtungen, dazu ein regelmässiger Grund- und Aufriss
([[Grenze der Grundschwingzeit]]). Was das Verfahren verlangt und hier nicht
gerechnet wird, steht grau unter dem Bild: die Torsion (16.5.2.7), die
vertikale Komponente (16.5.4) und die sekundären Bauteile (16.7) – und wo
$q$ über 2.0 liegt, die Bemessungswerte duktiler Tragwände nach SIA
262:2025, 4.3.9.4.

Nach Vorgabe, nicht nachgeschlagen: getrennte Teile des Kerns ohne
Steiner-Anteil zwischen ihnen ([[Trägheitsmomente des Kerns]]), die
Verteilung auf sie nach ihrem Anteil an $I$, nur Biegung, der Anteil
$\eta_{EI} = 0.5$ der ungerissenen Steifigkeit und $g = 10\,\mathrm{m/s^2}$
wie beim Eigengewicht.
