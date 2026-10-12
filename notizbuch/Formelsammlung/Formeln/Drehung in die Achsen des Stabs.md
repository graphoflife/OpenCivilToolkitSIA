---
erzeugt: 82df4f2813c9
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Von den Achsen des Systems in die des Stabs»*

$$
\mathbf{d} = \mathbf{T} \cdot \mathbf{d}_{glob} \qquad \mathbf{T} = \begin{bmatrix} \mathbf{R} & \mathbf{0} \\ \mathbf{0} & \mathbf{R} \end{bmatrix} \qquad \mathbf{R} = \begin{bmatrix} \cos\alpha & \sin\alpha & 0 \\ -\sin\alpha & \cos\alpha & 0 \\ 0 & 0 & 1 \end{bmatrix}
$$

## Im Code

- [[opencivil.stabwerk.herleitung|_ansaetze]]

## Themen

- [[Steifigkeitsmethode]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Verschiebungen eines Knotens stehen in den Achsen des Systems, $x$ nach
rechts und $z$ nach oben; die [[Steifigkeitsmatrix eines Stabs]] steht in
dessen eigenen Achsen, $x$ vom Anfang zum Ende und $y$ links davon.
$\mathbf{T}$ dreht um den Winkel $\alpha$ des Stabs; die Drehung $\theta$ ist
in beiden Achsen dieselbe. Im System wird aus $\mathbf{k}$ so
$\mathbf{T}^{\mathsf{T}} \cdot \mathbf{k} \cdot \mathbf{T}$.
