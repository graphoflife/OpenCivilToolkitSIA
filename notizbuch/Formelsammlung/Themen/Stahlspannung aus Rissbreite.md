---
erzeugt: 28fa9273db59
art: thema
tags: [thema]
---
> [!abstract] Platte
> 14 Formeln, in der Folge, in der gerechnet wird.

## Was die Rechnung dazu sagt

Unter quasi-ständiger Einwirkung begrenzt die Stahlspannung die Rissbreite – dieselbe Grenze wie bei der Zwängung, nur dass die Spannung hier aus den Lasten kommt und nicht aus einer aufgezwungenen Verformung. Gerechnet wird am gerissenen Querschnitt: der Beton nimmt keinen Zug auf. Die Bewehrung wirkt auf Zug und auf Druck – nur in der Handrechnung zählt die gedrückte nicht. Gemessen wird an der am stärksten gezogenen Lage.

Drei Festlegungen stecken in jeder Zahl unten, und alle drei sind Auslegung der Norm und nicht Rechnung. Erstens das Kriechen: angesetzt wird das φ dieses Kapitels. Ein grösseres φ weicht den Beton auf, die Druckzone wächst, der Hebelarm wird kleiner und die Stahlspannung damit grösser; mit φ = 0 gehen die Spannungen zurück, und der Nachweis geht leichter auf. Mit dem Spannungsblock hängt kein Gesetz am Modul – dort wirkt φ nicht.

Zweitens die Werkstoffgesetze: sie rechnen mit den charakteristischen Festigkeiten. Der Stahl ist linear bis f\_yk und fliesst dann, der Beton trägt höchstens f\_ck. Ein Gebrauchsnachweis fragt, was der Querschnitt tut, und nicht, was er darf – der Teilsicherheitsbeiwert gehört in die Tragsicherheit. Läge das Plateau bei f\_yd, bliebe jede Stahlspannung darunter, und eine Grenze darüber könnte nie überschritten werden.

Drittens die Grenze: dieselbe wie bei der Zwängung, mit f\_yk und bei erhöhter und hoher Anforderung zusätzlich begrenzt durch die Rissbreite. Massgebend ist der dickste Stab der Tragrichtung. Welche Lage die grösste Zugspannung trägt, wechselt mit dem Lastfall – bei einem Feldmoment die untere, bei einem Stützmoment die obere –, und der dickste Stab gibt die kleinste zulässige Spannung. Das liegt für beide auf der sicheren Seite.

Fliesst die Bewehrung, bleibt ihre Spannung am Plateau stehen, während die Dehnung weiterwächst. Verglichen wird dann die Dehnung: ε\_s gegen ε\_s,adm = σ\_s,adm / E\_s. Solange der Stahl elastisch bleibt, ist das genau der Spannungsvergleich; fliesst er, fällt der Nachweis durch, und zwar um so deutlicher, je weiter er gedehnt ist.

Die Dehnungsebene wird gesucht, nicht hergeleitet. Eine ebene Dehnungsverteilung hat zwei Unbekannte – die Dehnung in der Mittelebene ε\_m und die Krümmung χ – und ihnen stehen zwei Gleichgewichtsbedingungen gegenüber: N und M. Geschlossen auflösen lässt sich das nicht, weil die Werkstoffgesetze nichtlinear sind.

Das Integral über den Beton wird als Summe über 60 Fasern gleicher Dicke gebildet, jede mit der Spannung in ihrer Mitte; der Stahl kommt Lage für Lage dazu, und die von ihm verdrängte Betonfläche wird abgezogen, damit dieselbe Fläche nicht zweimal zählt.

Gesucht wird in zwei geschachtelten Suchen, beide durch Halbieren. Innen: zu einer festgehaltenen Krümmung χ wird ε\_m gesucht, bis N\_int die verlangte Normalkraft trifft – das geht sicher, weil mehr Dehnung immer mehr Zug bedeutet. Aussen: mit diesem ε\_m bleibt ein Moment übrig, und χ wird gesucht, bis auch M\_int stimmt – hier trägt die Monotonie, dass mehr Krümmung mehr Moment heisst.

Das Suchfenster bleibt dabei innerhalb der Grenzdehnungen (-3.0 ‰ bis 45.0 ‰). Jenseits davon geben die Werkstoffgesetze null zurück, die Kraft wäre nicht mehr monoton, und die Suche liefe auf eine beliebige Stelle zu. Passt zu einer Krümmung kein Fenster mehr, gibt es keine Gleichgewichtslage – dann sagt der Nachweis das und rät nicht.

Nachgewiesen wird deshalb nicht der Weg, sondern das Ergebnis: dass die gefundene Ebene genau die angegebenen Schnittgrössen erzeugt. Diese Probe steht bei jedem Fall.

Erzeugt die gefundene Ebene die Einwirkung nicht, gibt es zu ihr keine Ebene, und der Nachweis sagt das, statt die Probe abzuhaken. Das kommt vor, wo ein Gesetz springt wie der Spannungsblock: bei viel Druck und wenig Moment liegt der Block immer ganz an einem Rand und gibt mehr Moment, als einwirkt.

Mit dem Spannungsblock trägt der Beton unter (1 − 0.85)·ε\_c2d nichts. Unter Gebrauchslast liegt die Druckresultierende damit am Rand, und der Hebelarm wird beinahe d – die Stahlspannung kleiner, als der Querschnitt sie hat. Der Block ist ein Modell für den Bruch.

Mit der Handrechnung rechnet der Querschnitt wie die Resistenzlinie aus Handrechnung: der Beton als Spannungsblock, die gedrückte Bewehrung weggelassen, die Bewehrung jeder Seite zu einer Lage in ihrem Schwerpunkt zusammengefasst, und der Beton auch dort gezählt, wo der Stahl liegt.

Das Integral über den Beton wird als Summe über 60 Fasern gleicher Dicke gebildet; der Stahl kommt Lage für Lage dazu. Wie in der Handrechnung zählt der Beton auch dort, wo der Stahl liegt.

Unter quasi-ständiger Einwirkung begrenzt die Stahlspannung die Rissbreite – dieselbe Grenze wie bei der Zwängung, nur dass die Spannung hier aus den Lasten kommt und nicht aus einer aufgezwungenen Verformung. Gerechnet wird am gerissenen Querschnitt: der Beton nimmt keinen Zug auf, die Bewehrung wirkt auf Zug und auf Druck. Jeder gezogene Stab hält gegen seine Grenze; massgebend ist der mit dem kleinsten Erfüllungsgrad.

Drittens die Grenze: dieselbe wie bei der Zwängung, mit f\_yk und bei erhöhter und hoher Anforderung zusätzlich begrenzt durch die Rissbreite. Jeder gezogene Stab hält gegen seine eigene Grenze, mit seinem Durchmesser und dem f\_ctm des Betons, in dem er liegt; massgebend ist der Stab mit dem kleinsten Erfüllungsgrad.

Einachsig bleibt die Nulllinie waagrecht, und M\_z zählt nicht – wie in der Tragsicherheit.

## Formeln

1. [[Wirksamer Elastizitätsmodul]]
2. [[Zulässige Stahlspannung (Rissbreite w_nom)]]
3. [[Beton linear, ohne Zug]]
4. [[Bilineare Beziehung des Betonstahls]]
5. [[Dehnungsebene und innere Kräfte]]
6. [[Erfüllungsgrad]]
7. [[Zulässige Stahlspannung (normale Anforderung)]]
8. [[Fliessdehnung]]
9. [[Zulässige Dehnung]]
10. [[Spannungsblock des Betons]]
11. [[Betonstahl nur auf Zug]]
12. [[Fiktiver Durchmesser einer verschmierten Linie]]
13. [[Beiwert der Parabel]]
14. [[Parabel-Rechteck-Beziehung des Betons]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie breit ein Riss wird, hängt an der Spannung des Stahls, der ihn
überbrückt: je höher sie ist, desto mehr dehnt er sich zwischen den
Rissen, und desto weiter öffnet sich der Riss. Die Rissbreite lässt sich
darum über eine Grenze der Stahlspannung begrenzen -- unter
quasi-ständiger Einwirkung, der Last, die dauernd wirkt.

Die Spannung kommt aus einer Gebrauchsrechnung am gerissenen Querschnitt:
gesucht wird die Dehnungsebene, die die Einwirkung im Gleichgewicht hält
(siehe [[Dehnungsebene und innere Kräfte]]). Womit gerechnet wird -- elastisch
mit dem [[Wirksamer Elastizitätsmodul|kriechweichen Modul]], mit der Parabel
oder dem Block, mit welchen Werten --, wählt das Kapitel. Gemessen wird an
der am stärksten gezogenen Lage; fliesst sie, vergleicht der Nachweis
Dehnungen statt Spannungen (siehe [[Zulässige Dehnung]]).
