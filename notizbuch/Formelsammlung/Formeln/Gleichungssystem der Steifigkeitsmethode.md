---
erzeugt: 11f2defed2c3
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Gesamtsteifigkeitsmatrix und Gleichungssystem»*

$$
\mathbf{K} = \sum_{\text{Stäbe}} \mathbf{T}^{\mathsf{T}} \cdot \mathbf{k} \cdot \mathbf{T} \qquad \mathbf{K} \cdot \mathbf{x} = \mathbf{F}
$$

## Im Code

- [[opencivil.stabwerk.herleitung|_ansaetze]]

## Themen

- [[Steifigkeitsmethode]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Jeder Stab steuert seine Matrix bei, gedreht in die Achsen des Systems; an
jedem Knoten halten die Kräfte der Stäbe den Lasten das Gleichgewicht.
Daraus wird $\mathbf{K} \cdot \mathbf{x} = \mathbf{F}$, mit den
Verschiebungen und Drehungen $\mathbf{x}$ aller Knoten als Unbekannte --
ausser denen, die ein Lager festhält.

Gelöst wird mit der Zerlegung
$\mathbf{K} = \mathbf{L} \cdot \mathbf{D} \cdot \mathbf{L}^{\mathsf{T}}$.
Wird dabei ein Diagonalwert null, ist das System beweglich: $\mathbf{K}$ lässt
sich nicht invertieren, und die Meldung nennt, was sich ohne Widerstand
bewegt. Ein Knoten, an dem alle Stäbe gelenkig hängen, hat für seine Drehung
gar keine Steifigkeit; sie wird gestrichen und null gesetzt -- «Verdrehung
nicht bestimmbar, da keine Steifigkeit».

Die Lagerkräfte folgen danach aus dem Gleichgewicht der Knoten. Die
Gleichgewichtsprobe zählt Lasten und Lagerkräfte zusammen; was übrig bleibt,
ist Rundung.
