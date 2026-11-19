---
erzeugt: e3fd7b70c75f
art: thema
tags: [thema]
---
> [!abstract] Querschnittsanalyse
> 8 Formeln, in der Folge, in der gerechnet wird.

## Was die Rechnung dazu sagt

Der Querschnitt ist gezeichnet: Polygone, jedes mit seinem Material. Liegt ein Polygon ganz in einem anderen, ersetzt es dieses dort – eine Aussparung nimmt die Fläche weg. y zeigt nach rechts, z nach oben; alle Masse in Millimetern.

Für ein beliebiges Polygon gibt es keine Formel für I\_T. Gerechnet wird mit der Spannungsfunktion φ von Prandtl, auf einem Gitter: seine Linien laufen durch jede waagrechte und lotrechte Kante, je Zelle gibt es einen Wert, und eine schräge Kante wird zwischen zwei Zellmitten genau geschnitten. Am Rand eines Hohlraums ist φ fest, und hinaus fliesst so viel, wie der Hohlraum Fläche hat. Der Fehler fällt mit dem Quadrat der Zellgrösse; ein zweites Gitter, jede Zelle halbiert, hebt ihn heraus.

## Formeln

1. [[Fläche und Schwerpunkt eines Polygons (Satz von Gauss)]]
2. [[Trägheitsmomente eines Polygons, bezogen auf den Schwerpunkt]]
3. [[Teilung einer Stablinie – gleiche Felder, auf die Länge gerundet]]
4. [[Bügelquerschnitt je Länge einer Schubwand (n Schnitte)]]
5. [[Verschmierte Stahlfläche aus Stäben]]
6. [[Spannungsfunktion von Prandtl]]
7. [[Torsionsträgheitsmoment aus der Spannungsfunktion]]
8. [[Torsionsträgheitsmoment, nach Richardson aus beiden Gittern]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Neben der Platte kennt das Werkzeug den gezeichneten Querschnitt: beliebige
Polygone, jedes mit seinem Material, dazu Stäbe, Stablinien und Schubwände.
Ein Unterzug, ein Hohlkasten, eine Stütze mit Aussparung -- was sich zeichnen
lässt, lässt sich rechnen.

Aus der Zeichnung entstehen zuerst die Querschnittswerte: Fläche,
Schwerpunkt und Trägheitsmomente jedes Polygons nach dem Satz von Gauss.
Liegt ein Polygon ganz in einem anderen, ersetzt es dieses dort; eine
Aussparung nimmt die Fläche weg. Stablinien werden in gleiche Felder geteilt,
Schubwände bekommen ihren Bügelquerschnitt je Länge.

Darauf bauen die Nachweise auf: [[Schiefe Biegung]] für Moment und
Normalkraft in beliebiger Richtung, [[Querkraft und Torsion]] über die
Schubwände, und je Richtung die [[Duktilität je Richtung|Duktilität]] und das
[[Sprödes Versagen je Richtung|spröde Versagen]].
