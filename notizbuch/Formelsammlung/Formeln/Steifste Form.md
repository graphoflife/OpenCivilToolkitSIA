---
erzeugt: 71ae6ff64fed
art: formel
tags: [formel]
normstelle: "Andreassen et al. (2011), Gl. (1), (2) und (9)"
---
> [!info] Normstelle
> Andreassen et al. (2011), Gl. (1), (2) und (9)

*In der Herleitung: «Ziel der Form»*

$$
c = F^{T} U \;\rightarrow\; \min \qquad K(\tilde{\rho}) \, U = F \qquad \sum_e \tilde{\rho}_e \, A_e = \bar{\rho} \, A \qquad E_e = E_{min} + \tilde{\rho}_e^{\,p} \left( E_0 - E_{min} \right)
$$

## Im Code

- [[opencivil.fachwerkmodell.herleitung#_aus_der_form|_aus_der_form]]

## Themen

- [[Fachwerkmodell]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das Verfahren SIMP teilt die Scheibe in quadratische Elemente und gibt
jedem eine Dichte $\rho_e$ zwischen 0, leer, und 1, voll. Gesucht ist die
Verteilung, mit der die Scheibe unter ihren Lasten am steifsten ist: Die
Arbeit $c = F^{T} U$, die die Lasten $F$ an den Verschiebungen $U$
leisten, soll so klein wie möglich sein. Das Material ist knapp: Alle
Elemente zusammen haben den Anteil $\bar{\rho}$ der Fläche $A$, Vorgabe
30 %.

Ein Element ist mit $\tilde{\rho}_e^{\,p}$ steif, mit $p = 3$. Halb voll
hat es ein Achtel der Steifigkeit, braucht aber die Hälfte des Materials –
es lohnt sich, das Material zu sammeln, wo es trägt. So wird die Form
klar, fast nur voll oder leer. Ein leeres Element behält
$E_{min} = 10^{-9}\,E_0$, damit die Rechnung nicht auseinanderfällt.

$\tilde{\rho}_e$ ist die Dichte gemittelt über die Nachbarn bis 1.5
Netzweiten, nach ihrem Abstand gewichtet. Ohne dieses Mittel entstünden
Schachbretter aus vollen und leeren Elementen, die steifer scheinen, als
sie sind, und die Form hinge stark an der Netzweite.

Schritt um Schritt rechnet das Werkzeug die Scheibe linear elastisch.
Dann fragt es jedes Element, um wie viel steifer die Scheibe mit etwas
mehr Material dort wäre, und verteilt neu: mehr, wo es viel bringt,
weniger, wo wenig, je Schritt um höchstens 0.2. Fertig ist die Form, wenn
sich keine Dichte mehr um 0.01 ändert. $E_0$ kürzt sich heraus; nur die
Querdehnzahl $\nu = 0.2$ geht ein – ohne Material und Dicke hängt die Form
nur an Scheibe, Lagern und Lasten.

Die steifste Form ist nicht das leichteste Fachwerk, aber sie zeigt, wo
die Kräfte fliessen. Darum liest das Werkzeug aus ihren Mittellinien die
Knoten und möglichen Stäbe; die Kräfte bestimmt dann die Optimierung des
[[Leichtestes Fachwerk|leichtesten Fachwerks]].

Beispiel: die Konsole 1 × 2 m, Lager bei (0, 0) und (0, 2) m, 100 kN nach
unten bei (1, 1) m, Netzweite 0.1 m – 200 Elemente – und 30 % Material.
Nach 9 Schritten stehen zwei Streben von den Lagern zur Last. Das
Fachwerk aus ihnen hat zwei Stäbe von je 1.414 m, oben 70.7 kN Zug und
unten 70.7 kN Druck, wie die Handrechnung: $V = 200\,\mathrm{kNm}$.
