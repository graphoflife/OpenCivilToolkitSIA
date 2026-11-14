---
erzeugt: fef040b60095
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.2.6, (34)"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.2.6, (34)

*In der Herleitung: «Erforderliche Biegewiderstände, linearisierte Fliessbedingung»*

$$
\begin{aligned} & m_{xu} \ge m_x + |m_{xy}| \qquad m_{yu} \ge m_y + |m_{xy}| \\ & m'_{xu} \ge -m_x + |m_{xy}| \qquad m'_{yu} \ge -m_y + |m_{xy}| \end{aligned}
$$

## Im Code

- [[opencivil.decke.herleitung#_ansaetze|_ansaetze]]

## Themen

- [[Streifenmethode]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Aus $m_x$, $m_y$ und $m_{xy}$ an einer Stelle folgt, wie viel
Biegewiderstand die Bewehrung dort haben muss, in x und in y, unten und
oben (SIA 262:2025, 4.3.2.6, (34a) bis (34d)). Das Drillmoment zählt in
beiden Richtungen und auf beiden Seiten mit seinem Betrag: eine Bewehrung
in x und y trägt ein Drillmoment nur, indem beide Lagen mehr tragen.

Die Norm schreibt die vier Bedingungen als Nachweis gegen den Widerstand;
hier steht, was sie von ihm verlangen. Sie lässt das als Näherung zu, wenn
die Bewehrung in x und y liegt und die Drillmomente mässig bleiben. Fällt
ein Wert unter null, braucht es auf dieser Seite dort nichts; der Bericht
schreibt dann null.

Beispiel: $m_x = 30$, $m_y = -10$ und $m_{xy} = 5\,\mathrm{kNm/m}$ verlangen
unten in x 35, unten in y nichts ($-10 + 5 < 0$), oben in x nichts und oben
in y $15\,\mathrm{kNm/m}$.

Gesucht werden die grössten Werte an denselben Stellen wie in den Bildern.
Über Stützen und unter Einzellasten kommt das [[Lastverteilelement]] dazu.
