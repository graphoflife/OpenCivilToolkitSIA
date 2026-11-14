---
erzeugt: 1ced844ef15c
art: formel
tags: [formel]
normstelle: "Stahlbeton II, 7.2 Platten, Folie 38"
---
> [!info] Normstelle
> Stahlbeton II, 7.2 Platten, Folie 38

*In der Herleitung: «Was ein Lastverteilelement l\_x × l\_y zusätzlich braucht»*

$$
\begin{aligned} & m'_{xu} \ge \frac{Q}{8} \cdot \frac{l_x}{l_y} \qquad m_{xu} \ge \left(\frac{1}{2\pi} - \frac{1}{8}\right) \cdot Q \cdot \frac{l_x}{l_y} \\ & m'_{yu} \ge \frac{Q}{8} \cdot \frac{l_y}{l_x} \qquad m_{yu} \ge \left(\frac{1}{2\pi} - \frac{1}{8}\right) \cdot Q \cdot \frac{l_y}{l_x} \end{aligned}
$$

## Im Code

- [[opencivil.decke.herleitung#_ansaetze|_ansaetze]]

## Themen

- [[Streifenmethode]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Streifen nehmen die Kraft $Q$ einer Stütze als gleichmässige Pressung
über den Stützenbereich $l_x \times l_y$ ab
([[Pressung eines Flächenlagers]]) -- die Stütze drückt aber nur auf ihre
kleine Fläche. Damit beides zusammenpasst, braucht der Bereich ein eigenes
Element, das die Kraft vom Punkt auf die Fläche verteilt. Es verlangt
zusätzlich zu dem, was die Streifen brauchen, oben $Q/8 \cdot l_x/l_y$ in x
und unten den kleineren Wert $(1/(2\pi) - 1/8) \cdot Q \cdot l_x/l_y$; in y
mit $l_y/l_x$.

Unter einer Einzellast ist es umgekehrt: die Last kommt als Punkt von oben,
die Streifen tragen sie als Fläche. Dann tauschen oben und unten.

Beispiel aus dem Kolloquium 4: die mittlere Stütze trägt $276.4\,\mathrm{kN}$
über $1 \times 1\,\mathrm{m}$. Das verlangt in beiden Richtungen oben
$34.5\,\mathrm{kNm/m}$ und unten $9.4\,\mathrm{kNm/m}$; die Musterlösung
gibt 34.4 und 9.4.

Der Bericht nennt die Werte je Stütze und Einzellast. Sie gelten nur im
Bereich des Elements und kommen dort zu den
[[Linearisierte Fliessbedingung|Widerständen der Streifen]] dazu.
