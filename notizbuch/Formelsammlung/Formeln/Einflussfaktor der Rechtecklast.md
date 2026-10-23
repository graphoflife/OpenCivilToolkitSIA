---
erzeugt: 47a831b09cf2
art: formel
tags: [formel]
normstelle: "Kap. 8.2"
---
> [!info] Normstelle
> Kap. 8.2

*In der Herleitung: «Einflussfaktor nach Boussinesq in der Tiefe z: die vier Rechtecke, die sich im Punkt treffen»*

$$
\begin{aligned} J &= J_E(x, y) + J_E(L - x, y) + J_E(x, B - y) + J_E(L - x, B - y) \\ J_E(a, b) &= \frac{1}{2\pi} \left[\arctan\frac{a \, b}{z \, R} + \frac{a \, b \, z}{R} \left(\frac{1}{a^2 + z^2} + \frac{1}{b^2 + z^2}\right)\right] \qquad R = \sqrt{a^2 + b^2 + z^2} \end{aligned}
$$

## Im Code

- [[opencivil.geotechnik.setzung#Setzung._punkt|Setzung._punkt]]

## Themen

- [[Setzung]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie viel einer gleichmässigen Pressung $q$ in der Tiefe $z$ unter einem Punkt
ankommt, sagt der Einflussfaktor $J = \Delta\sigma'_z / q$ nach Boussinesq --
für einen homogenen, elastischen Halbraum unter einer schlaffen Last. Unter
der Ecke eines Rechtecks $a \times b$ gibt es dafür eine geschlossene Formel,
$J_E$. Unter einem anderen Punkt teilt man die Fläche in die vier Rechtecke,
die sich in ihm treffen, und zählt ihre Eckwerte zusammen. In der Sohle ist
$J = 1$; mit der Tiefe nimmt er ab, unter langen Streifen langsamer als unter
quadratischen Flächen (Tabelle 8.5).

Das Kapitel 8 verwendet $J$, die Formel selbst steht in Kapitel 3, das nicht
vorliegt. Sie gibt die Werte $J_K$ der Tabelle 8.4 auf die gedruckte Stelle
wieder und die Grenztiefen der Tabelle 8.5 so genau, wie sie dort abgelesen
sind -- nachgeschlagen ist sie nicht.
