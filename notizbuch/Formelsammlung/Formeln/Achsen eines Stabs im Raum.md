---
erzeugt: 6124c323a06a
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Von den Achsen des Systems in die des Stabs»*

$$
\mathbf{d} = \mathbf{T} \cdot \mathbf{d}_{glob} \qquad \mathbf{T} = \operatorname{diag}(\mathbf{R}, \mathbf{R}, \mathbf{R}, \mathbf{R}) \qquad \mathbf{R} = \begin{bmatrix} \mathbf{e}_x^{\mathsf{T}} \\ \mathbf{e}_y^{\mathsf{T}} \\ \mathbf{e}_z^{\mathsf{T}} \end{bmatrix} \qquad \mathbf{e}_z \parallel -\mathbf{e}_Z + (\mathbf{e}_Z \cdot \mathbf{e}_x)\,\mathbf{e}_x \qquad \mathbf{e}_y = \mathbf{e}_z \times \mathbf{e}_x
$$

## Im Code

- [[opencivil.stabwerk3d.herleitung|_ansaetze]]

## Themen

- [[Steifigkeitsmethode]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Jeder Stab rechnet in seinen eigenen Achsen. Die Matrix $\mathbf{R}$ dreht
eine Verschiebung oder eine Drehung aus den Achsen des Systems in die des
Stabs, je Ende zweimal: für die drei Verschiebungen und für die drei
Drehungen. Ihre Zeilen sind die Einheitsvektoren des Stabs; sie ist darum
orthogonal, zurück geht es mit $\mathbf{R}^{\mathsf{T}}$, und die Steifigkeit
in den Achsen des Systems ist $\mathbf{T}^{\mathsf{T}}\,\mathbf{k}\,\mathbf{T}$.

$x$ läuft vom Anfang zum Ende. $z$ liegt in der lotrechten Ebene durch den
Stab und zeigt nach unten – dorthin, wo im 2D-Balkensystem die gestrichelte
Faser liegt. $y = z \times x$ ergänzt zum Rechtssystem. Ein lotrechter Stab
hat keine eigene lotrechte Ebene; bei ihm ist $y$ die Achse $-Y$ des Systems.
Der Drehwinkel $\beta$ dreht $y$ und $z$ danach im Rechtssinn um $x$: so steht
der Steg eines Profils schräg oder quer.

Ob $M_z$ mit diesen Achsen das erwartete Vorzeichen hat, ist offen: [[TODO]].
