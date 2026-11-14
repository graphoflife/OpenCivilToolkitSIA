---
erzeugt: 98097e66323d
art: thema
tags: [thema]
---
> [!abstract] Pfähle
> 13 Formeln, in der Folge, in der gerechnet wird.

## Was die Rechnung dazu sagt

Der Pfahl steht im Boden wie ein Stab auf Federn. Längs halten ihn die Reibung am Mantel und der Druck am Fuss, quer drückt er gegen den Boden neben sich. Wie stark die Federn sind, folgt aus dem Verformungsmodul der Schichten: am Mantel und am Fuss nach Cassan, quer nach der Norm. Die Federn am Kopf -- wie weit er sich unter einer Last setzt, verschiebt und dreht -- braucht das Modell des Tragwerks darüber; sie gelten mit dem charakteristischen Modul. Für die Schnittkräfte rechnet die Norm mit einem kleineren: in weicherem Boden weicht der Pfahl weiter aus und biegt sich stärker.

## Formeln

1. [[Dehnsteifigkeit des Pfahls]]
2. [[Biegesteifigkeit des Pfahls]]
3. [[Feder am Pfahlmantel]]
4. [[Bettungsmodul quer zum Pfahl]]
5. [[Abgeminderte Bettung am Terrain]]
6. [[Feder am Pfahlfuss]]
7. [[Gebetteter Pfahl]]
8. [[Längsfeder des Pfahlkopfs]]
9. [[Querfeder des frei drehbaren Pfahlkopfs]]
10. [[Querfeder des eingespannten Pfahlkopfs]]
11. [[Kopplung am Pfahlkopf]]
12. [[Drehfeder des Pfahlkopfs]]
13. [[Bemessungswert des Verformungsmoduls]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Federn, die ein Modell des Tragwerks für den Pfahl braucht, und was der
Pfahl unter den Lasten jeder Kombination tut. Längs gelten die Federn von
Cassan (Kap. 12.8), quer die Bettung der Norm (SIA 267:2013, 9.5.4.5,
(53)), nahe dem Terrain abgemindert. Das Werkzeug löst den Pfahl als
gebetteten Stab mit finiten Elementen, mit den Schichten, wie sie
eingegeben sind.

Zwei Moduln für zwei Zwecke: die Federn am Kopf mit E_s,k, wie in der
Gebrauchstauglichkeit (5.3.2.8); Setzung, Verschiebung und Schnittkräfte je
Kombination mit E_s,k / 1.5, weil in der Tragsicherheit ein weicherer Boden
ungünstiger ist (5.3.2.5).

Was die Rechnung annimmt, ohne dass Norm oder Buch es so sagen, steht in der
Herleitung als «nach Vorgabe, nicht nachgeschlagen»: die lineare
Abminderung bis t_red, Cassans Werte auch für den Mikropfahl, der
ungerissene Querschnitt, γ_E = 1.5, längs und quer getrennt ohne zweite
Ordnung, keine Mantelfeder, wo q_s,k null ist, und die Fussfeder bei R_a,k
aus einem Versuch.

Den Bettungsdruck gegen den Widerstand des Bodens und den Widerstand quer
zur Achse rechnet [[Äusserer Pfahlwiderstand quer]] (9.4.4.2, 9.5.4.5).
