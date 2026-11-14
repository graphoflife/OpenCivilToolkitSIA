---
erzeugt: 91cccc164e76
art: thema
tags: [thema]
---
> [!abstract] Platte
> 16 Formeln, in der Folge, in der gerechnet wird.

## Was die Rechnung dazu sagt

Querkraftwiderstand mit Querkraftbewehrung, Fachwerkmodell mit veränderlicher Neigung der Druckdiagonalen. Massgebend ist das Kleinere aus dem Widerstand der Bügel und dem der Druckdiagonalen; der Betonanteil ohne Bügel geht nicht zusätzlich ein.

Beide Anteile gelten je Laufmeter, wie die Querkraft selbst; der Hebelarm der inneren Kräfte ist 0.9 · d. Gesucht wird ganzgradig zwischen α\_min und α\_max die Neigung mit dem grössten Widerstand V\_Rd = min(V\_Rd,s; V\_Rd,c). Bei einer Normalzugkraft steilt sich die Druckdiagonale auf: α\_min ist dann mindestens 40°, und α\_max wird notfalls mitgehoben.

Querkraftwiderstand ohne Querkraftbewehrung. Massgebend sind die statische Höhe der gezogenen Bewehrung, die Grösstkorngrösse und die nominelle Dehnung der Zugbewehrung.

N\_Ed zählt mit Vorzeichen, Zug positiv: Druck hebt das Dekompressionsmoment und entlastet, Zug macht es negativ und vergrössert die Dehnung. Da der Widerstand über m\_Ed und N\_Ed von der Einwirkung abhängt, wird er für jede Kombination einzeln bestimmt.

## Formeln

1. [[Querkraftwiderstand mit Querkraftbewehrung]]
2. [[Teilung in y aus der Stabzahl]]
3. [[Schwerpunkt der zusammengefassten Lage]]
4. [[Statische Höhe]]
5. [[Widerstand der Bügel]]
6. [[Widerstand der Druckdiagonalen]]
7. [[Erfüllungsgrad]]
8. [[Querkraftwiderstand ohne Querkraftbewehrung]]
9. [[Dekompressionsmoment und Dehnung]]
10. [[Beiwert der Gesteinskörnung]]
11. [[Wirksame Höhe, um die Einlage vermindert]]
12. [[Dekompressionsmoment]]
13. [[Widerstand bei festgehaltenem N_Ed]]
14. [[Nominelle Dehnung der Zugbewehrung]]
15. [[Beiwert für den Querkraftwiderstand]]
16. [[Wirksame Höhe ohne Abzug]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ob eine Platte Querkraftbewehrung trägt, entscheidet, welcher von zwei
Ansätzen gilt -- addiert werden sie nicht.

**Ohne Bügel** trägt der Beton allein. Die Querkraft läuft über einen
Druckbogen, und was sie begrenzt, ist der kritische Schubriss: je breiter er
sich öffnet, desto weniger Kraft überträgt er durch die Verzahnung seiner
Ufer. Seine Breite wächst mit der Dehnung der Platte und mit ihrer Höhe. Der
Widerstand ist darum $\tau_{cd}$ mal einer Höhe, gemindert durch den
[[Beiwert für den Querkraftwiderstand]], in den die
[[Nominelle Dehnung der Zugbewehrung|nominelle Dehnung der Zugbewehrung]],
die statische Höhe und die Gesteinskörnung eingehen. Weil die Dehnung vom
Moment abhängt, gilt der Widerstand je Kombination aus Moment und
Normalkraft.

**Mit Bügeln** trägt ein Fachwerk: die Bügel als Zugstäbe, der Beton als
schräge Druckdiagonalen, die Längsbewehrung als Gurt. Die Neigung der
Diagonalen ist in Grenzen frei; gesucht wird die, die am meisten trägt. Massgebend ist
das Kleinere aus dem [[Widerstand der Bügel]] und dem
[[Widerstand der Druckdiagonalen]].

Gerechnet wird je Tragrichtung und je Laufmeter, wie die Querkraft selbst.
