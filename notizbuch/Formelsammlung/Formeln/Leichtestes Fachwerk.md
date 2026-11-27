---
erzeugt: de05dc4f9eb0
art: formel
tags: [formel]
normstelle: "He, Gilbert & Song (2019), Abschnitt 3, Gl. (7)"
---
> [!info] Normstelle
> He, Gilbert & Song (2019), Abschnitt 3, Gl. (7)

*In der Herleitung: «Ziel der Optimierung»*

$$
V = \sum_i l_i \, \left( w_Z \, N_i^{+} + w_D \, N_i^{-} \right) \;\rightarrow\; \min
$$

## Im Code

- [[opencivil.fachwerkmodell.herleitung#_fachwerk|_fachwerk]]

## Themen

- [[Fachwerkmodell]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ein Fachwerk trägt seine Lasten über Stäbe, die nur Zug oder nur Druck
haben. Wie viel Material ein Stab braucht, wächst mit seiner Kraft und
seiner Länge: bei derselben Spannung $f$ ist sein Volumen $l \, |N| / f$.
Ohne Material und ohne Dicke zählt darum $V$, die Summe aus Länge mal
Kraft – je kleiner, desto leichter das Fachwerk.

$N_i^{+}$ ist der Zug eines Stabs, $N_i^{-}$ sein Druck, beide positiv
gezählt; ein Stab hat das eine oder das andere. Mit $w_Z = w_D = 1$ zählen
Zug und Druck gleich (nach Vorgabe, nicht nachgeschlagen). Ein grösseres
$w_Z$ macht Zug teurer – etwa, weil ein Zugglied Bewehrung braucht und
eine Druckstrebe nur Beton –, und das Fachwerk meidet ihn.

Gesucht wird unter allen Fachwerken aus den möglichen Stäben, die an
jedem Knoten im Gleichgewicht sind. $V$ und das Gleichgewicht sind in den
Kräften linear: eine lineare Optimierung, und ihr Minimum ist das
leichteste Fachwerk. Sie gibt zugleich ein Feld virtueller Verschiebungen.
Jeder Stab, den es gibt, dehnt sich darin höchstens um $w_Z$ und staucht
sich höchstens um $w_D$; ein Stab, der mehr hätte, machte das Fachwerk
leichter. So findet die Suche Runde um Runde die Stäbe, die noch fehlen.

Beispiel: eine Konsole, Lager bei (0, 0) und (0, 2) m, eine Last von
100 kN nach unten bei (1, 1) m. Zwei Stäbe von je $\sqrt{2} = 1.414$ m,
der obere mit 70.7 kN Zug, der untere mit 70.7 kN Druck:
$V = 2 \cdot 1.414 \cdot 70.7 = 200\,\mathrm{kNm}$. Mit $w_Z = 2$ zählt
der Zug doppelt, und $V = 300\,\mathrm{kNm}$.
