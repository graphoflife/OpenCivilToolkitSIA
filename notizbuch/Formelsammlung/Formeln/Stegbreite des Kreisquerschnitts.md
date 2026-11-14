---
erzeugt: f3fe1d8195c2
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Breite des Stegs: die Sehne des Kreises auf der Höhe des Druckgurts, die kleinste zwischen den Gurten»*

$$
b_w = 2 \cdot \sqrt{\left(\frac{D}{2}\right)^{2} - \left(\frac{D}{2} - d + z\right)^{2}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $D$ | Durchmesser des Pfahls | mm | Vorgabe |
| $d$ | Statische Höhe des Pfahls | mm | [[Statische Höhe des Kreisquerschnitts]] |
| $z$ | Hebelarm der inneren Kräfte | mm | [[Hebelarm der inneren Kräfte]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\begin{aligned}
  b_w &= 2 \cdot \sqrt{\left(\frac{D}{2}\right)^{2} - \left(\frac{D}{2} - d + z\right)^{2}} \\
  &= 2 \cdot \sqrt{\left(\frac{900\,\mathrm{mm}}{2}\right)^{2} - \left(\frac{900\,\mathrm{mm}}{2} - 676\,\mathrm{mm} + 608.4\,\mathrm{mm}\right)^{2}} \\
  &= 474.4\,\mathrm{mm}
\end{aligned}
$$

## Gebraucht von

- [[Widerstand der Druckdiagonalen im Pfahl]]

## Im Code

- [[opencivil.pfahl.innen_quer#InnererQuerwiderstand._fachwerk|InnererQuerwiderstand._fachwerk]]

## Themen

- [[Innerer Pfahlwiderstand quer]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Druckdiagonalen laufen zwischen den beiden Gurten durch den Steg; was
sie tragen, wächst mit seiner Breite b_w. Ein Kreis hat keinen Steg gleicher
Breite: in der Mitte ist er am breitesten, zum Rand hin wird er schmal. Als
b_w zählt hier die Sehne auf der Höhe des Druckgurts, 0.1·d unter dem
gedrückten Rand. Das ist die schmalste Stelle zwischen den Gurten, denn der
Druckgurt liegt weiter von der Achse als der Zuggurt.

⌀ 900 mm: der Druckgurt 382 mm über der Achse, b_w = 2·√(450² − 382²) = 474
mm, rund die Hälfte von D.

Nach Vorgabe, nicht nachgeschlagen: die Norm sagt nicht, welche Breite ein
Kreis hat. Die schmalste liegt auf der sicheren Seite, und im Bohrpfahl
trägt ohnehin meist die Wendel weniger als die Druckdiagonalen.
