---
erzeugt: ea725cfe61d3
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Ein Stab im Raum: drei ebene Stäbe»*

$$
\mathbf{k} = \mathbf{k}_{z}(EA, EI_y) \oplus \mathbf{k}_{y}(EI_z) \oplus \mathbf{k}_{T}(GI_T) \qquad \mathbf{d}_{z} = (u, -w, \theta_y)_{a,b} \qquad \mathbf{d}_{y} = (-v, -\theta_z)_{a,b} \qquad \mathbf{d}_{T} = (\theta_x)_{a,b}
$$

## Im Code

- [[opencivil.stabwerk3d.herleitung|_ansaetze]]

## Themen

- [[Steifigkeitsmethode]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ein gerader Stab, dessen Achsen $y$ und $z$ die Hauptachsen seines
Querschnitts sind, zerfällt in drei Stäbe, die nichts voneinander wissen:
die Biegung in der Ebene $x$-$z$ samt der Längskraft, die Biegung in der
Ebene $x$-$y$ und die Torsion. Seine Steifigkeitsmatrix 12 × 12 setzt sich
darum aus drei ebenen zusammen ($\oplus$): jede Zeile und Spalte einer
ebenen Matrix fällt auf eine der zwölf Unbekannten des Stabs. Die Torsion
verhält sich wie die Längskraft, mit der [[Torsionssteifigkeit]] statt der
Dehnsteifigkeit.

Die Minuszeichen kommen von den Achsen: der ebene Stab hat seine Querachse
links, und sein Moment zieht an der rechten Faser; im Raum zeigt $z$ nach
unten. So steht jede Regel des ebenen Stabs – Steifigkeit, Lasten, Bettung,
Verlauf – nur einmal.

Was die Zerlegung nicht kennt: die Kopplung von Biegung und Torsion, wenn der
Schubmittelpunkt neben dem Schwerpunkt liegt wie beim U-Profil, die
Wölbkrafttorsion und die Theorie 2. Ordnung ([[TODO]]).
