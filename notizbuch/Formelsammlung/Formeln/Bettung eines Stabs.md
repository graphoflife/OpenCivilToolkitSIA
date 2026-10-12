---
erzeugt: fb912b6d89d8
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Bettung eines Stabs, quer und längs»*

$$
\mathbf{k}_{b} = \frac{k_{\perp} \cdot L}{420} \begin{bmatrix} 156 & 22L & 54 & -13L \\ 22L & 4L^2 & 13L & -3L^2 \\ 54 & 13L & 156 & -22L \\ -13L & -3L^2 & -22L & 4L^2 \end{bmatrix} \qquad \mathbf{k}_{b,\parallel} = \frac{k_{\parallel} \cdot L}{6} \begin{bmatrix} 2 & 1 \\ 1 & 2 \end{bmatrix}
$$

## Im Code

- [[opencivil.stabwerk.herleitung|_ansaetze]]

## Themen

- [[Steifigkeitsmethode]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ein Stab auf nachgiebigem Grund, etwa ein Fundamentbalken: der Grund drückt
mit $k_{\perp} \cdot v$ je Meter Stab zurück, wie eine dichte Reihe von
Federn (Winkler). Die Matrix ist diese verteilte Feder in arbeitsgleicher
Form, quer mit denselben kubischen Formfunktionen wie die Biegung, längs mit
linearen.

Genau ist das nur, solange ein Stück kurz ist gegen die Länge, auf der die
Biegelinie abklingt, $1/\beta$ mit $\beta = \sqrt[4]{k_{\perp} / (4 EI)}$.
Darum wird ein gebetteter Stab in Stücke von höchstens $1/(2\beta)$ geteilt;
dann weicht die Rechnung um weniger als ein Promille von der geschlossenen
Lösung ab.
