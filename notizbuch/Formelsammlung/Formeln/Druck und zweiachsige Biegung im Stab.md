---
erzeugt: 43e1caa1611b
art: formel
tags: [formel]
normstelle: "SIA 263:2013, 5.1.10.1, (50); 5.2.9"
---
> [!info] Normstelle
> SIA 263:2013, 5.1.10.1, (50); 5.2.9

*In der Herleitung: «Druck und zweiachsige Biegung im Stab – N\_K,Rd das kleinere, M\_Rd um die starke Achse M\_D,Rd»*

$$
\frac{N_{Ed}}{N_{K,Rd}} + \frac{\omega_y}{1 - N_{Ed}/N_{cr,y}} \cdot \frac{M_{y,Ed}}{M_{y,Rd}} + \frac{\omega_z}{1 - N_{Ed}/N_{cr,z}} \cdot \frac{M_{z,Ed}}{M_{z,Rd}} \le 1
$$

## Im Code

- [[opencivil.nachweis.qa_stahl_stabilitaet#_Herleitung.gleichung_50|_Herleitung.gleichung_50]]

## Themen

- [[Knicken und Kippen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die allgemeine Gleichung für einen Stab unter Druck und Biegung: der
Anteil der Druckkraft am Knickwiderstand und je Achse der Anteil des
Moments am Biegewiderstand. Jedes Moment wird dabei mit
$\omega/(1 - N_{Ed}/N_{cr})$ vervielfacht: $\omega$ mindert es für eine
günstige Verteilung, der Bruch vergrössert es für die Ausbiegung des
Stabs.

Um die starke Achse steht, wo der Stab kippen kann, der
[[Kippwiderstand]] statt des Biegewiderstands. $N_{K,Rd}$ ist der kleinere
der beiden Werte aus [[Knickwiderstand]]. In den Klassen 1 und 2 sind die
Widerstände plastisch, in Klasse 3 elastisch (5.2.9).
