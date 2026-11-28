---
erzeugt: 3edcde8bc99c
art: formel
tags: [formel]
normstelle: "SIA 266:2015, 4.3.4.2, Figur 11"
---
> [!info] Normstelle
> SIA 266:2015, 4.3.4.2, Figur 11

*In der Herleitung: «Ausmitte der Wand unter Normalkraft und Querlast, w(x) nach Figur 3»*

$$
e_z(x) = e_u + \left(e_o - e_u\right) \cdot \frac{x}{h_w} + \frac{p_d \cdot b_q \cdot x \cdot \left(h_w - x\right)}{2 \cdot N_m} + w(x)
$$

## Im Code

- [[opencivil.mauerwerk.querlast#Querlastnachweis.ansatz|Querlastnachweis.ansatz]]

## Themen

- [[Mauerwerk]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ohne Bewehrung trägt eine Wand Querlast nur über Druck. Zwischen Kopf und
Fuss hält die Normalkraft sie zusammen: Die Querlast schiebt die Druckkraft
zur Seite, und solange diese in der Wand bleibt, steht ein lotrechtes
Gewölbe (SIA 266:2015, 4.3.4.2, Figur 11).

Der Pfeiler bekommt die Querlast $p_d$ über die Breite $b_q$. Zwischen Kopf
und Fuss gibt sie das Moment eines einfachen Balkens,
$p_d\, b_q\, x\,(h_w - x)/2$; durch $N_m$ geteilt ist das die Ausmitte,
um die die Druckkraft wandert, in halber Höhe am weitesten:
$p_d\, b_q\, h_w^2/(8\, N_m)$. Dazu kommen die Ausmitten der Lasten an
Kopf und Fuss, linear über die Höhe, und die Auslenkung $w(x)$: Die Wand
biegt sich unter der Ausmitte, und die Biegung vergrössert diese, nach
Figur 3 wie beim Knicken. Ein eingespannter Rand dreht sich nicht; seine
Ausmitte folgt aus dem Gleichgewicht.

Das Werkzeug lässt die Querlast wachsen, bis die Ausmitte irgendwo die
Grenze nach Gl. (6) und Figur 4 erreicht oder die Wand kein Gleichgewicht
mehr findet. Die letzte Querlast, die hält, ist $p_{Rd,v}$.

Gl. (19) und (20) erlaubten, die Effekte 2. Ordnung wegzulassen, wenn die
Wand gedrungen ist und sich wenig biegt (4.3.4.1). Das Werkzeug rechnet sie
immer mit: So liegt es auf der sicheren Seite, und das Modell ist dasselbe
wie beim Nachweis der Normalkraft. Dass Kopf und Fuss die Kräfte des
Gewölbes aufnehmen und weiterleiten (4.3.4.5), prüft es nicht.
