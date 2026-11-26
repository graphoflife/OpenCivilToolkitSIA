---
erzeugt: ae372e096663
art: formel
tags: [formel]
normstelle: "SIA 263:2013, 4.5.3.2, (11); 4.5.3.3"
---
> [!info] Normstelle
> SIA 263:2013, 4.5.3.2, (11); 4.5.3.3

*In der Herleitung: «Mitwirkende Breite, b zwischen den theoretischen Scheibenschnittlinien»*

$$
\bar{\lambda}_p = \frac{b/t}{28.4\, \varepsilon \sqrt{k}} \qquad \rho = \frac{0.9}{\bar{\lambda}_p} \le 1 \qquad b_{eff} = \rho\, b_c
$$

## Im Code

- [[opencivil.nachweis.qa_stahl_werte#breiten|breiten]]

## Themen

- [[Kennzahlen]]
- [[Stahlquerschnitt]]
- [[Knicken und Kippen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ein dünnes, gedrücktes Blech beult aus, bevor es fliesst. Danach trägt es
trotzdem weiter: die gehaltenen Ränder bleiben gerade und nehmen die
Spannung auf, die Mitte weicht aus. Die mitwirkende Breite ersetzt das
durch einen Streifen, der voll trägt; der Rest fällt weg.

- $\bar{\lambda}_p$ vergleicht die Schlankheit $b/t$ mit der eines Blechs,
  das gerade beim Fliessen beult. $k$ ist der Beulwert nach Tabelle 9: er
  hängt von der Halterung und vom Spannungsverlauf $\psi$ ab.
- Bis $\bar{\lambda}_p = 0.9$ trägt das Blech ganz, $\rho = 1$; darüber
  nimmt $\rho$ mit $0.9/\bar{\lambda}_p$ ab.
- Gemindert wird nur der gedrückte Teil $b_c$ der Breite.

Im Kasten, hier im Rechteckrohr, gilt der genauere Faktor (70). Der
Streifen, der wegfällt, liegt beim beidseitig gehaltenen Blech in der Mitte
der Druckzone, beim einseitig gehaltenen am freien Ende.
