---
erzeugt: 7fdd006df5ab
art: thema
tags: [thema]
---
> [!abstract] Mauerwerk
> 30 Formeln, in der Folge, in der gerechnet wird.

## Was die Rechnung dazu sagt

Unter der Normalkraft biegt sich eine Wand aus, und die Ausmitte wächst. Der Pfeiler hält, solange er sich im Gleichgewicht verformen kann, ohne dass die Ausmitte irgendwo die Grenze der Figur 4 überschreitet. Die grösste Normalkraft, bei der das gerade noch gilt, ist k\_N · l\_w · t\_w · f\_xd.

Ein Sturz liegt an seinen Enden auf dem Mauerwerk auf und drückt es dort auf der Fläche A\_0 = a · t\_w. Liegt die Fläche mitten in einer grösseren, verteilt sich der Druck, und das Mauerwerk trägt mehr; am Rand der Öffnung kann er das nicht.

Die Querkraft geht mit der Normalkraft als geneigte Druckstrebe durch den Pfeiler. Geneigt trägt Mauerwerk nur f\_yd (Figur 7), und am Fuss nur auf der gedrückten Länge l\_2, wo die Resultierende hinkommt. Darum vergleicht der Nachweis Normalkräfte: je schräger die Strebe, desto weniger Normalkraft trägt sie.

Steiler als arctan μ\_d kann die Druckstrebe nicht stehen: sonst gleitet der Pfeiler in einer Lagerfuge. Die Reibung trägt μ\_d · N\_xd.

Quer zu ihrer Ebene trägt eine Wand aus unbewehrtem Mauerwerk über Druckgewölbe: lotrecht zwischen Kopf und Fuss mit ihrer Normalkraft, und waagrecht zwischen gehaltenen Rändern (Figur 11). Das lotrechte Gewölbe ist die verformte Wand: die Querlast gibt ihr eine Ausmitte dazu, und wie bei der Normalkraft darf diese nirgends über die Grenze der Figur 4.

Rechnet das Gebäude im Erdbeben mit q = 2.0, darf jede Wand, die zur Tragsicherheit zählt, nur mässig gedrückt sein. Dazu muss das Gebäude regelmässig sein nach SIA 261 – das prüft das Werkzeug hier nicht.

## Formeln

1. [[Bemessungswert der Druckfestigkeit senkrecht zu den Lagerfugen]]
2. [[Bemessungswert der Druckfestigkeit senkrecht zu den Stossfugen]]
3. [[Bemessungswert der Druckfestigkeit senkrecht zu den Stossfugen, vollfugig vermauert]]
4. [[Elastizitätsmodul senkrecht zu den Lagerfugen, kennzeichnend]]
5. [[Schubmodul, kennzeichnend]]
6. [[Bemessungswert des Elastizitätsmoduls senkrecht zu den Lagerfugen]]
7. [[Bemessungswert des Schubmoduls]]
8. [[Eigengewicht der Wand je m² Ansicht, aus der Dichte ihres Mauerwerks]]
9. [[Ersatzkraft des Erdbebens quer zu einer Wand]]
10. [[Krümmung einer Wand aus Mauerwerk]]
11. [[Grenze der Ausmitte einer Wand aus Mauerwerk]]
12. [[Gleichgewicht der verformten Wand – Ausmitte der Last und Auslenkung w]]
13. [[Ausmitte am Kopf – sie bleibt, wenn die Lasten wachsen]]
14. [[Bezugswert der Knicklänge einer Wand]]
15. [[Normalkraftwiderstand eines Pfeilers aus Mauerwerk]]
16. [[Erfüllungsgrad]]
17. [[Gedrückte Länge am Fuss eines Pfeilers]]
18. [[Fläche des Auflagers]]
19. [[Beiwert der Teilflächenpressung im Mauerwerk]]
20. [[Widerstand eines Sturzauflagers]]
21. [[Neigung der Druckstrebe in einem Pfeiler]]
22. [[Dicke einer Schubwand mit ausmittiger Normalkraft]]
23. [[Widerstand der Druckstrebe in einem Pfeiler]]
24. [[Widerstand eines Pfeilers gegen Gleiten]]
25. [[Ausmitte einer Wand unter Querlast]]
26. [[Normalkraft eines Pfeilers in halber Höhe]]
27. [[Normalkraftniveau eines Pfeilers]]
28. [[Durchbiegung einer Wand als waagrechter Streifen]]
29. [[Widerstand des waagrechten Druckgewölbes einer Wand]]
30. [[Querlastwiderstand einer Wand aus Mauerwerk]]

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

Lasten in der Ebene der Wand – Wind oder Erdbeben, die eine Decke in die
Wand leitet – nimmt sie als Scheibe auf: über den Öffnungen starr, darunter
die Pfeiler als eingespannte Stützen. Jeder Pfeiler bekommt seinen Teil als
Querkraft, dazu ein Moment und eine Normalkraft, mit denen die Wand dem
Kippen widersteht; auch das regelt die Norm nicht. Am Fuss jedes Pfeilers
folgen die Nachweise nach 4.3.2 und 4.3.3: die geneigte Druckstrebe auf
der gedrückten Länge (Gl. (13)), das Gleiten der Lagerfugen (Gl. (14))
und, steht die Normalkraft quer zur Wand ausmittig, die Normalkraft auf
der gedrückten Länge (Gl. (17)).

Quer zu ihrer Ebene – Wind von Hand oder das Erdbeben – trägt die Wand
über Druckgewölbe (4.3.4): lotrecht zwischen Kopf und Fuss mit ihrer
Normalkraft, gerechnet nach Theorie 2. Ordnung wie beim Knicken, und
waagrecht zwischen gehaltenen Rändern als Bogen mit drei Gelenken. Es zählt
das stärkere der beiden. Das Erdbeben quer zur Wand ist die Ersatzkraft
eines sekundären Bauteils nach SIA 261:2020, Gl. (49), mit der Schwingzeit
des Gebäudes – das Ungünstigste, nach Vorgabe, auch für eine tragende
Wand. Rechnet das Gebäude mit $q = 2.0$, darf jeder Pfeiler nur mässig
gedrückt sein, Gl. (27).
