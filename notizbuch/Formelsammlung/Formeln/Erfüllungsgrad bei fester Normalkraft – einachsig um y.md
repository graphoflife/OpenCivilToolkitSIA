---
erzeugt: 23dbd20f4b5d
art: formel
tags: [formel]
normstelle: "SIA 264:2014, 5.4.1.1"
---
> [!info] Normstelle
> SIA 264:2014, 5.4.1.1

$$
\alpha_{eff} = \frac{M_{Rd}}{M_{Ed}} \qquad M_{Ed} = |M_{y,Ed}|
$$

## Im Code

- [[opencivil.nachweis.qa_blechverbund#BlechBiegungQA.pruefe|BlechBiegungQA.pruefe]]

## Themen

- [[Blechverbunddecke]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Eine Blechverbunddecke trägt nur in Richtung ihrer Rippen. Das Werkzeug
rechnet sie darum immer einachsig um y: es zählt allein $M_{y,Ed}$. Ein
$M_{z,Ed}$, ein $V_{y,Ed}$ oder ein $T_{Ed}$ des Lastfalls bleibt
unberücksichtigt, und ein gelber Hinweis nennt den Lastfall.

Die Normalkraft $N_{Ed}$ bleibt fest; das Moment wächst in seiner
Richtung, bis der plastische Widerstand $M_{Rd}$ erreicht ist. Der
Erfüllungsgrad ist das Verhältnis der beiden Momente. Anders als bei der
schiefen Biegung ([[Erfüllungsgrad bei fester Normalkraft und fester Richtung]])
dreht die Nulllinie nicht, sie bleibt waagrecht.

Zeigt selbst das grösste Moment, das die Decke bei dieser Normalkraft mit
der gezogenen Seite trägt, in die Gegenrichtung, trägt sie in Richtung der
Einwirkung keines: $M_{Rd}$ ist dann null. Ebenso, wo unter negativem
Moment nichts Zug trägt – ohne Betonstahl über der Stütze.
