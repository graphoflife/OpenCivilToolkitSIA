---
erzeugt: 2d1d5bdf072e
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Gleichgewicht der verformten Wand: Ausmitte der Last und Auslenkung w»*

$$
e_z(x) = e_u + \left(e_o - e_u\right) \cdot \frac{x}{h_w} + w(x) \qquad w''(x) = -\chi_y\left(e_z(x)\right) \qquad w(0) = w(h_w) = 0
$$

## Im Code

- [[opencivil.mauerwerk.nachweise#Normalkraft.ansatz|Normalkraft.ansatz]]

## Themen

- [[Mauerwerk]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Ausmitte an einer Stelle ist die der Lasten – zwischen $e_u$ am Fuss und
$e_o$ am Kopf linear, wie ihr Moment – plus die Auslenkung $w$ der Wand dort.
Die Auslenkung folgt aus der Krümmung, und die Krümmung hängt nach Figur 3
an der Ausmitte: die Gleichung enthält ihre Lösung selbst und wird darum
Schritt für Schritt gelöst.

An einem gelenkigen Rand ist $w = 0$. Ein eingespannter Rand dreht sich
nicht, dort gilt zudem $w' = 0$; seine Ausmitte stellt sich so ein, dass das
aufgeht – das Moment der Lasten nimmt die Einspannung.

Das ist die Theorie 2. Ordnung nach 4.3.1.3, mit der Krümmung der Figur 3
statt einer festen Steifigkeit. Die Wand ist in gleiche Stücke geteilt, in
jedem gilt die Krümmung seiner Mitte. Die Normalkraft wächst, bis die Wand
kein Gleichgewicht mehr findet – sie knickt – oder bis ihre Ausmitte
irgendwo die [[Grenze der Ausmitte einer Wand aus Mauerwerk]] erreicht.
