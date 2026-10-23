---
erzeugt: d5aa879c1085
art: formel
tags: [formel]
normstelle: "Kap. 8.5"
---
> [!info] Normstelle
> Kap. 8.5

$$
\Delta s = \frac{\bar{J} \, q_W \, \Delta z}{M'_E} + \frac{\bar{J} \, q_E \, \Delta z}{M_E} \qquad \bar{J} = \frac{J_o + J_u}{2} \qquad s = \sum \Delta s
$$

## Im Code

- [[opencivil.geotechnik.setzung#Setzung.pruefe|Setzung.pruefe]]

## Themen

- [[Setzung]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Setzung ist die Summe der Zusammendrückungen der Teilschichten unter dem
Fundament. Eine Teilschicht der Dicke $\Delta z$ drückt sich um
$\Delta\sigma'_z \, \Delta z / M_E$ zusammen: die Zusatzspannung, die in ihrer
Tiefe noch ankommt, geteilt durch den Modul ihrer Schicht. Die Zusatzspannung
ist ein Teil der Pressung in der Sohle, $\Delta\sigma'_z = J \cdot q$
([[Einflussfaktor der Rechtecklast]]); gemittelt wird $J$ aus Ober- und
Unterkante, wie in der Tabellenform des Kapitels (Tabelle 8.4).

Was der Boden schon einmal getragen hat -- bis der Aushub für das Fundament
weggenommen wurde --, drückt ihn nur wieder zusammen: dafür gilt der Modul der
Wiederbelastung $M'_E$, meist ein Mehrfaches von $M_E$. Erst was darüber
hinausgeht, belastet ihn zum ersten Mal und rechnet mit $M_E$ (Kap. 8.5).
Darum werden die beiden Pressungen $q_W$ und $q_E$ getrennt angegeben.

Die Teilschichten sind höchstens $\Delta z_{max}$ dick, und jede
Schichtgrenze ist auch eine Grenze von Teilschichten. Feiner zu teilen lohnt
sich, wo sich $J$ stark ändert: nahe der Sohle, unter kleinen Fundamenten.
