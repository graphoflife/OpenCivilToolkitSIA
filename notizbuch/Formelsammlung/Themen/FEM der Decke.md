---
erzeugt: db19ef767475
art: thema
tags: [thema]
---
> [!abstract] Decken
> 4 Formeln, in der Folge, in der gerechnet wird.

## Formeln

1. [[Momente der Platte nach Kirchhoff]]
2. [[Querkräfte aus den Momenten der Platte]]
3. [[Träger in der Platte]]
4. [[Linearisierte Fliessbedingung]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die FEM rechnet die Decke als eine elastische Platte: linear, ungerissen,
mit $E_{cm}$ und $\nu_c$ ihres Betons. Die Platte ist dünn genug, dass ihre
Querschnitte eben und senkrecht zur Mittelfläche bleiben (Kirchhoff); dann
folgen alle Momente aus der Biegelinie $w$
([[Momente der Platte nach Kirchhoff]]) und die Querkräfte aus dem Gefälle
der Momente ([[Querkräfte aus den Momenten der Platte]]).

Gerechnet wird an einem Netz aus Dreiecken, das den Rändern, Lagern,
Trägern und Linienlasten folgt; jede Stütze ist ein Knoten. Je Knoten sind
$w$ und die beiden Neigungen unbekannt. Das Dreieck DKT gibt Momente, die
über jedes Dreieck linear sind, an einer gemeinsamen Kante aber nicht ganz
zusammenpassen. Darum gilt an jedem Knoten das Mittel der Dreiecke um ihn –
ausser wo die Platte nicht durchläuft: an einem Lager, einem Träger, einer
Linienlast oder einer Fuge behält jede Seite ihren Wert.

Die Lager halten, wie sie gezeichnet sind. Ein Linienlager hält die Höhe,
eingespannt auch die Drehung quer zu ihm; eine Stütze hält nur ihren
Punkt. Ein Träger mit Höhe ist ein Balken in der Mittelebene der Platte
([[Träger in der Platte]]). Was die Lager tragen, folgt aus dem
Gleichgewicht jedes Knotens; zusammen ist es die ganze Last.

Was die FEM besser kann als die [[Streifenmethode]]: die Durchbiegung und
die Verteilung der Momente, wie sie sich elastisch einstellt. Was sie nicht
kann: Sie lagert nichts um. Über einer Stütze, die als Punkt hält, wächst
das Moment mit feinerem Netz ohne Grenze; die Spitze dort gehört zum
Modell, nicht zur Decke. Die Querkräfte sind
Ableitungen geglätteter Werte und an einem Rand mit grobem Netz ungenau.
Die Ecken einer gelenkig gelagerten Platte heben sich ab, wenn das Lager sie
nicht niederhält; die FEM rechnet es als Lager, das zieht.

Aus den Momenten folgt wie in der Streifenmethode, was die Bewehrung
tragen muss ([[Linearisierte Fliessbedingung]]).
