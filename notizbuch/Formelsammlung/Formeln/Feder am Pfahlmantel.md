---
erzeugt: e0e11a53ba9e
art: formel
tags: [formel]
normstelle: "Kap. 12.8, Bild 12.9"
---
> [!info] Normstelle
> Kap. 12.8, Bild 12.9

*In der Herleitung: «Feder am Mantel je Meter Pfahl, für Bohrpfähle»*

$$
k_l = B \cdot \pi \cdot D \qquad B = 0.42 \cdot E_{s,k}
$$

## Im Code

- [[opencivil.pfahl.steifigkeit#Pfahlsteifigkeit._bettung|Pfahlsteifigkeit._bettung]]

## Themen

- [[Pfahlsteifigkeit]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie stark der Boden am Mantel gegen eine Setzung hält, je Meter Pfahl: die
Schubspannung je Setzung B mal dem Umfang. Für Bohrpfähle gibt Cassan
B ≈ 0.42 · E_s (Kap. 12.8, Bild 12.9), für Rammpfähle rund dreimal mehr.
Den Mikropfahl rechnet das Werkzeug mit dem Wert der Bohrpfähle -- nach
Vorgabe, nicht nachgeschlagen.

Die Feder ist linear und kennt keine Grenze: sie gilt, solange die Last
deutlich unter dem Mantelwiderstand bleibt. Eine Schicht, deren
Mantelreibung null eingegeben ist, hat auch keine Feder. ⌀ 900 mm in
E_s,k = 30 MN/m²: 0.42 · 30 · π · 0.9 ≈ 36 MN je Meter Setzung und Meter
Pfahl.
