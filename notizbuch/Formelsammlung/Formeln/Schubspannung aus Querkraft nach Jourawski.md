---
erzeugt: 6f9e8f6dde29
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Schubspannung nach Jourawski – auf dem Schnitt quer zur Querkraft, auf dem S/b am grössten ist; S ist das statische Moment jenseits davon, b seine Breite»*

$$
\tau = \frac{V \cdot S}{I \cdot b} = \frac{V}{A_V} \qquad A_V = \frac{I \cdot b}{S}
$$

## Im Code

- [[opencivil.nachweis.qa_holz_werte#HolzwerteQA|HolzwerteQA._schub]]

## Themen

- [[Holzquerschnitt]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Aus dem Gleichgewicht eines kurzen Stücks: ändert sich das Moment, ändern
sich die Biegespannungen, und was jenseits eines Längsschnitts mehr
ankommt, muss der Schnitt als Schub weitergeben. Darum $\tau = V S/(I b)$,
mit dem statischen Moment $S$ der Fläche jenseits des Schnitts und seiner
Breite $b$. Am grössten, wo $S/b$ am grössten ist – beim Rechteck in der
Mitte. Das Werkzeug sucht die Stelle auf vielen Schnitten zwischen den
Ecken.
