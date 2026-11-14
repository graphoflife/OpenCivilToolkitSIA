---
erzeugt: 10a9f75aff27
art: formel
tags: [formel]
normstelle: "Kap. 12.8, Bild 12.9; Kap. 12.10, Bild 12.14"
---
> [!info] Normstelle
> Kap. 12.8, Bild 12.9; Kap. 12.10, Bild 12.14

*In der Herleitung: «Gebetteter Stab: längs die Setzung w, quer die Verschiebung y»*

$$
EA \cdot w'' = k_l \cdot w \qquad EI \cdot y'''' = -k_s \cdot D \cdot y
$$

## Im Code

- [[opencivil.pfahl.steifigkeit#Pfahlsteifigkeit|Pfahlsteifigkeit._federn]]

## Themen

- [[Pfahlsteifigkeit]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Pfahl als Stab auf Federn, längs und quer getrennt. Längs gibt der
Pfahl, wo er sich setzt, über den Mantel Kraft an den Boden ab; die
Normalkraft nimmt nach unten ab, und was am Fuss bleibt, trägt dessen
Feder. Quer biegt er sich wie ein Balken auf einer Bettung: je weiter er
sich verschiebt, desto stärker drückt der Boden zurück (Kap. 12.8, 12.10).

Wie tief eine Querlast reicht, sagt die elastische Länge
(4 EI / (k_s · D))^¼. Ist der Pfahl länger als etwa das Dreifache, gilt er
als lang: was am Fuss geschieht, spürt der Kopf nicht mehr (Kap. 12.10).
⌀ 900 mm aus C30/37 in E_s,k = 30 MN/m²: 3.5 m, ein Pfahl über gut 10 m ist
also lang.

Das Werkzeug löst beides mit finiten Elementen, mit den Schichten und der
Abminderung am Terrain, wie sie eingegeben sind. Es rechnet linear: die
Federn ohne Grenze und ohne Theorie zweiter Ordnung, für die die Norm eine
eigene Untersuchung verlangt (SIA 267:2013, 9.5.3.4.3) -- nach Vorgabe,
nicht nachgeschlagen.
