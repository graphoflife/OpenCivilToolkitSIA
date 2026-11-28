---
erzeugt: 1b5536b3a404
art: thema
tags: [thema]
---
> [!abstract] Mauerwerk
> 18 Formeln, in der Folge, in der gerechnet wird.

## Was die Rechnung dazu sagt

Unter der Normalkraft biegt sich eine Wand aus, und die Ausmitte wächst. Der Pfeiler hält, solange er sich im Gleichgewicht verformen kann, ohne dass die Ausmitte irgendwo die Grenze der Figur 4 überschreitet. Die grösste Normalkraft, bei der das gerade noch gilt, ist k\_N · l\_w · t\_w · f\_xd.

Ein Sturz liegt an seinen Enden auf dem Mauerwerk auf und drückt es dort auf der Fläche A\_0 = a · t\_w. Liegt die Fläche mitten in einer grösseren, verteilt sich der Druck, und das Mauerwerk trägt mehr; am Rand der Öffnung kann er das nicht.

## Formeln

1. [[Bemessungswert der Druckfestigkeit senkrecht zu den Lagerfugen]]
2. [[Bemessungswert der Druckfestigkeit senkrecht zu den Stossfugen]]
3. [[Bemessungswert der Druckfestigkeit senkrecht zu den Stossfugen, vollfugig vermauert]]
4. [[Elastizitätsmodul senkrecht zu den Lagerfugen, kennzeichnend]]
5. [[Schubmodul, kennzeichnend]]
6. [[Bemessungswert des Elastizitätsmoduls senkrecht zu den Lagerfugen]]
7. [[Bemessungswert des Schubmoduls]]
8. [[Eigengewicht der Wand je m² Ansicht, aus der Dichte ihres Mauerwerks]]
9. [[Krümmung einer Wand aus Mauerwerk]]
10. [[Grenze der Ausmitte einer Wand aus Mauerwerk]]
11. [[Gleichgewicht der verformten Wand – Ausmitte der Last und Auslenkung w]]
12. [[Ausmitte am Kopf – sie bleibt, wenn die Lasten wachsen]]
13. [[Bezugswert der Knicklänge einer Wand]]
14. [[Normalkraftwiderstand eines Pfeilers aus Mauerwerk]]
15. [[Erfüllungsgrad]]
16. [[Fläche des Auflagers]]
17. [[Beiwert der Teilflächenpressung im Mauerwerk]]
18. [[Widerstand eines Sturzauflagers]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Mauerwerk ist ein Verbund aus Steinen und Mörtel, der Druck gut trägt und
Zug kaum: Kohäsion in der Lagerfuge und Zugfestigkeit zählen in der
Bemessung nicht (SIA 266:2015, 4.1.2). Eine Wand trägt darum, indem sie in
sich einen Weg für Druck findet – lotrecht von oben nach unten, über
Öffnungen hinweg auf Stürze und Pfeiler, und quer zu ihrer Ebene als Gewölbe
zwischen gehaltenen Rändern.

Die Formeln hier sind die Werte des Materials: die Festigkeiten senkrecht zu
den Lagerfugen und zu den Stossfugen und die Steifigkeiten, kennzeichnend
und als Bemessungswerte mit $\gamma_M = 2.0$. Standardmauerwerk hat seine
Werte je Sorte in den Tabellen 1 und 7; deklariertes bringt sie aus der
Deklaration mit und muss die Mindestwerte nach 3.1.3.1 erfüllen. Wie die
Wand gemauert ist, ändert die Werte, mit denen sie rechnet: im Verband alle
mal 0.85, vollfugig das grössere $f_{yd}$. Das wählt die Wand; ihre
Herleitung zeigt die Werte des Mauerwerks neben ihren eigenen.

Die Lasten kommen je Lastfall von oben und gehen zu den Pfeilern zwischen
den Öffnungen: was über einem Pfeiler liegt, in ihn, was über einer Öffnung
liegt, über ihren Sturz. Das regelt die Norm nicht; so rechnet das Werkzeug
nach Vorgabe, nicht nachgeschlagen. Je Pfeiler und Kombination folgt der
Nachweis der Normalkraft nach 4.3.1: die verformte Wand muss im
Gleichgewicht stehen, ohne dass ihre Ausmitte die Grenze der Figur 4
überschreitet. Je Sturzauflager und Kombination drückt die Auflagerkraft
das Mauerwerk auf einer kleinen Fläche – die Teilflächenpressung nach
4.2.1.2.
