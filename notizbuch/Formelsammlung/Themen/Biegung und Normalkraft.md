---
erzeugt: 5e83a579a225
art: thema
tags: [thema]
---
> [!abstract] Platte
> 26 Formeln, in der Folge, in der gerechnet wird.

## Was die Rechnung dazu sagt

Druckzone als Spannungsblock der Höhe 0.85·x mit durchgehend f\_cd; gedrückter Stahl bleibt unberücksichtigt. Die Bewehrung ist je Seite zu einer Lage zusammengefasst, das Moment bezieht sich auf die halbe Querschnittshöhe.

Der Querschnitt bleibt eben (Bernoulli). Zu jeder Dehnungsebene ergeben sich Normalkraft und Moment aus den Spannungen über die Höhe; Zug ist positiv, das Moment bezieht sich auf die halbe Querschnittshöhe. Die Resistenzlinie ist der Rand aller zulässigen Ebenen: an ihm erreicht der Stahl ε\_ud, der Beton am gedrückten Rand −ε\_c2d oder, wenn der ganze Querschnitt gedrückt ist, im Punkt C −ε\_c1d.

Der Beton ist in 200 Fasern über die Höhe geteilt, die Bewehrung zählt Lage für Lage, und an ihrer Stelle zählt der Stahl statt des Betons – auch die gedrückte Bewehrung wirkt mit. Den Widerstand bei einer Einwirkung sucht die Rechnung auf dem Rand selbst, zwischen zwei benachbarten Ebenen; was dort gilt, zeigt bei jeder Kombination die Probe.

Der Beton ist in 200 Fasern über die Höhe geteilt, jede mit ihrer mittleren Spannung, die Bewehrung zählt Lage für Lage, und an ihrer Stelle zählt der Stahl statt des Betons – auch die gedrückte Bewehrung wirkt mit. Den Widerstand bei einer Einwirkung sucht die Rechnung auf dem Rand selbst, zwischen zwei benachbarten Ebenen; was dort gilt, zeigt bei jeder Kombination die Probe.

## Formeln

1. [[Schwerpunkt der zusammengefassten Lage]]
2. [[Bewehrungsquerschnitt der zusammengefassten Lage]]
3. [[Gleichmässiger Druck, ohne Bewehrung]]
4. [[Beide Lagen fliessen auf Zug]]
5. [[Kräfte mal Hebelarm um die halbe Höhe]]
6. [[Statische Höhe]]
7. [[Druckzonenhöhe aus dem Kräftegleichgewicht]]
8. [[Momentenwiderstand bei reiner Biegung]]
9. [[Nulllinie auf halber Höhe]]
10. [[Dehnung der Zugbewehrung]]
11. [[Stahlspannung, höchstens die Fliessgrenze]]
12. [[Kräftegleichgewicht]]
13. [[Momentengleichgewicht um die halbe Höhe]]
14. [[Widerstand bei festgehaltenem N_Ed]]
15. [[Erfüllungsgrad]]
16. [[Wirksamer Elastizitätsmodul]]
17. [[Beiwert der Parabel, mit dem wirksamen Modul]]
18. [[Parabel-Rechteck-Beziehung des Betons]]
19. [[Bilineare Beziehung des Betonstahls]]
20. [[Schnittgrössen aus der Spannungsverteilung]]
21. [[Spannungsblock des Betons]]
22. [[Bezugsgrösse der Normalkraft]]
23. [[Bezugsgrösse des Moments]]
24. [[Einwirkung im normierten Diagramm]]
25. [[Kürzester Abstand zur Resistenzlinie]]
26. [[Widerstand im normierten Diagramm]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Eine Platte unter Moment und Normalkraft trägt, solange der Punkt
$(N_{Ed}, M_{Ed})$ innerhalb ihrer **Resistenzlinie** liegt -- der
geschlossenen Linie aller Kombinationen, die der Querschnitt gerade noch
aufnimmt. Rechts endet sie im reinen Zug, links im reinen Druck, oben und
unten liegen die grössten Momente beider Vorzeichen.

Das Werkzeug kennt zwei Linien:

- **Die Handrechnung** verbindet wenige Eckpunkte mit Geraden: reiner Druck
  ([[Gleichmässiger Druck, ohne Bewehrung]]), reiner Zug
  ([[Beide Lagen fliessen auf Zug]]), reine Biegung
  ([[Momentenwiderstand bei reiner Biegung]]) und die
  [[Nulllinie auf halber Höhe]], je für beide Momentenvorzeichen. Der Beton
  trägt als Spannungsblock, gedrückter Stahl zählt nicht, und die Bewehrung
  jeder Seite ist in ihrem Schwerpunkt zusammengefasst. Jeder Punkt lässt
  sich von Hand nachrechnen.
- **Die Linie aus Dehnungsebenen** fährt den Rand aller zulässigen
  Dehnungsebenen ab. Der Querschnitt bleibt eben, Beton und Stahl folgen
  ihren Werkstoffgesetzen ([[Parabel-Rechteck-Beziehung des Betons]] oder
  [[Spannungsblock des Betons]], [[Bilineare Beziehung des Betonstahls]]),
  und jede Lage zählt für sich -- auch die gedrückte. Die
  [[Schnittgrössen aus der Spannungsverteilung]] folgen durch Integration
  über 200 Fasern.

Welche Linie gilt, wählt das Kapitel mit seiner Rechenwahl; die andere steht
zum Vergleich im Diagramm. Wie weit eine Einwirkung von der Linie entfernt
ist, sagt der [[Erfüllungsgrad]] -- gemessen bei festgehaltener Normalkraft,
bei festgehaltenem Moment oder als kürzester Abstand im normierten
Diagramm.
