---
erzeugt: 73b8efe10c75
art: thema
tags: [thema]
---
> [!abstract] Erdbeben
> 14 Formeln, in der Folge, in der gerechnet wird.

## Was die Rechnung dazu sagt

Das Beben wird durch waagrechte Kräfte ersetzt: je Hauptrichtung eine Ersatzkraft aus dem Bemessungsspektrum bei der Grundschwingzeit, verteilt auf die Geschosse nach Höhe und Gewicht. Die Wände tragen sie als Kragarme, eingespannt am Fuss – jede nach ihrem Anteil an der Biegesteifigkeit.

## Formeln

1. [[Gewicht eines Geschosses]]
2. [[Gewicht des Gebäudes]]
3. [[Biegesteifigkeit der Wände]]
4. [[Auslenkung des Dachs]]
5. [[Grundschwingzeit]]
6. [[Bemessungsspektrum (32)]]
7. [[Ersatzkraft]]
8. [[Ersatzkraft eines Geschosses]]
9. [[Kippmoment am Fuss]]
10. [[Grenze der Grundschwingzeit]]
11. [[Erfüllungsgrad]]
12. [[Bemessungsspektrum (31)]]
13. [[Bemessungsspektrum (33)]]
14. [[Bemessungsspektrum (34)]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das Ersatzkraftverfahren nach SIA 261:2020, 16.5.2, für ein Gebäude aus
Geschossen und Wänden aus Beton. Je Hauptrichtung ein ebenes Modell: die
Wände als Kragarme, am Fuss eingespannt, die Decken starr in ihrer Ebene.
Aus den Gewichten und der Steifigkeit der Wände folgt die
[[Grundschwingzeit]], aus ihr das Spektrum, die [[Ersatzkraft]] und ihre
Verteilung auf die Geschosse und auf die Wände.

Ob das Verfahren gilt, ist ein Urteil wie ein Nachweis: $T_1 \le 4 \cdot
T_C$ in beiden Richtungen, dazu ein regelmässiger Grund- und Aufriss
([[Grenze der Grundschwingzeit]]). Was das Verfahren verlangt und hier nicht
gerechnet wird, steht grau unter dem Bild: die Torsion (16.5.2.7), die
vertikale Komponente (16.5.4) und die sekundären Bauteile (16.7) -- und wo
$q$ über 2.0 liegt, die Bemessungswerte duktiler Tragwände nach SIA
262:2025, 4.3.9.4.

Nach Vorgabe, nicht nachgeschlagen: die Verteilung auf die Wände nach ihrer
Biegesteifigkeit, nur Biegung, der Anteil $\eta_{EI} = 0.5$ der ungerissenen
Steifigkeit und $g = 10\,\mathrm{m/s^2}$ wie beim Eigengewicht.
