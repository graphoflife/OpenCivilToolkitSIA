---
erzeugt: f8e6ab5bfc89
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Die Momente der Platte aus ihrer Krümmung, nach Kirchhoff»*

$$
\begin{aligned} & D = \frac{E_{cm} \cdot h^3}{12 \cdot (1 - \nu_c^2)} \\ & m_x = -D \cdot \left(\frac{\partial^2 w}{\partial x^2} + \nu_c \cdot \frac{\partial^2 w}{\partial y^2}\right) \qquad m_y = -D \cdot \left(\frac{\partial^2 w}{\partial y^2} + \nu_c \cdot \frac{\partial^2 w}{\partial x^2}\right) \\ & m_{xy} = -D \cdot (1 - \nu_c) \cdot \frac{\partial^2 w}{\partial x \, \partial y} \end{aligned}
$$

## Im Code

- [[opencivil.decke.fem.herleitung#_ansaetze|_ansaetze]]

## Themen

- [[FEM der Decke]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Eine dünne Platte biegt sich wie ein Blatt: jeder Querschnitt bleibt eben
und senkrecht zur verbogenen Mittelfläche, die Schubverformung zählt
nicht. Die Krümmungen sind dann die zweiten Ableitungen der Durchbiegung
$w$, und die Momente folgen aus ihnen mit der Plattensteifigkeit $D$. Die
Querdehnung $\nu_c$ koppelt die Richtungen: eine Krümmung in x gibt auch
ein Moment in y.

$w$ zählt nach unten. Ein Moment ist positiv, wenn es unten zieht – eine
Platte, die nach unten durchhängt, hat dort positive Momente. $D$ wächst
mit $h^3$: eine Platte von 250 mm ist fast doppelt so steif wie eine von
200 mm ($1.25^3 = 1.95$).

Beispiel: C30/37 mit $E_{cm} = 32\,000\,\mathrm{N/mm^2}$, $\nu_c = 0.2$ und
$h = 0.25\,\mathrm{m}$ gibt
$D = 32\,000 \cdot 0.25^3 / (12 \cdot 0.96) = 43.4\,\mathrm{MNm}$.

Das Dreieck DKT erfüllt die Annahme nicht im ganzen Dreieck, sondern an
seinen Ecken und in der Mitte seiner Kanten; mit feinerem Netz kommt es der
dünnen Platte beliebig nahe. Eine gleichmässige Krümmung gibt es genau
wieder.
