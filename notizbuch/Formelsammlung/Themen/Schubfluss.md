---
erzeugt: dc6101a13724
art: thema
tags: [thema]
---
> [!abstract] Querschnittsanalyse
> 3 Formeln, in der Folge, in der gerechnet wird.

## Was die Rechnung dazu sagt

Wächst das Moment längs des Bauteils, wächst auch die Kraft im Teil, den ein Schnitt abtrennt. Was sie auf einer Länge Δx gewinnt, kommt durch den Schnitt: der Schubfluss v = ΔF′/Δx, mit ΔM = V·Δx. F′ ist die Kraft im abgetrennten Teil, aus zwei Dehnungsebenen des ganzen Querschnitts – gerissen, mit waagrechter Nulllinie und der Rechenwahl des Falls. Elastisch ist das V·S′/I.

## Formeln

1. [[Schubfluss im Schnitt]]
2. [[Zuwachs des Moments über Δx]]
3. [[Schubspannung im Schnitt]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ein Schnitt quer durch den Querschnitt trennt einen Teil ab: den Flansch
neben dem Steg, den Aufbeton über der Fuge, die Betonplatte über dem
Stahlprofil. Ändert sich das Moment längs des Bauteils, ändert sich die
Kraft $F'$ in diesem Teil – was er auf einer Länge $\Delta x$ gewinnt, kommt
durch den Schnitt: der [[Schubfluss im Schnitt|Schubfluss]] $v$, eine Kraft
je Meter. Auf die Länge $b_i$ verteilt, auf der der Schnitt Material von
Material trennt, ist er die mittlere
[[Schubspannung im Schnitt|Schubspannung]] $\tau = v/b_i$.

$F'$ kommt aus zwei Dehnungsebenen des ganzen Querschnitts, bei $M$ und bei
$M + \Delta M$ ([[Zuwachs des Moments über Δx]]), gesucht wie in einer
Spannung-Dehnung-Analyse: gerissen, mit der Rechenwahl des Falls, die
Nulllinie waagrecht. Integriert wird über den abgetrennten Teil samt den
Stäben und Spanngliedern darin, auf denselben Streifen wie der ganze
Querschnitt – zwei Schnitte, die dieselbe Druckzone abtrennen, geben so
dieselbe Zahl.

Zwei Sonderfälle zeigen, was die Regel tut. Elastisch ist sie
$V \cdot S'/I$, mit dem statischen Moment $S'$ des abgetrennten Teils.
Gerissen, ohne Normalkraft und mit festem Hebelarm $z$ ist sie $V/z$ mal dem
Anteil des Teils an der Kraft seines Gurts – so rechnet der Eurocode die
Kraft in einer Fuge, $\beta \cdot V/z$ (EN 1992-1-1, 6.2.5, nicht
nachgeschlagen). Beispiel: ein Plattenbalken mit einem Flansch von 1600 mm
über einem Steg von 400 mm; ein Schnitt am Steg trennt 600 mm ab, also 3/8
der Druckkraft. Bei $V = 400$ kN und $z = 0.71$ m gehen
$3/8 \cdot 400/0.71 = 211$ kN/m durch ihn. Die Regel gilt aber auch mit
Normalkraft und wo der Hebelarm mit dem Moment wandert.

Liegt die ganze Druckzone im Aufbeton, geht die ganze Druckkraft durch die
Fuge, so viel wie durch einen Schnitt dicht über dem Stahl. Reicht sie unter
die Fuge, geht weniger hindurch: der Rest bleibt im Fertigteil.

Nur die Einwirkung, ohne Widerstand (Benutzer, 2026-11-27): ob eine Fuge,
die Dübel oder eine Naht $v$ tragen, steht nicht hier.

Nach Vorgabe, nicht nachgeschlagen: die Regel selbst – SIA 262 nennt die
Kraft in einer Fuge nicht –, $\Delta x = 10$ mm, $\Delta M$ mit dem
Vorzeichen von $M$, und angegeben ist der Betrag von $v$.
