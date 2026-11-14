---
erzeugt: 3cabf5c0bec5
art: formel
tags: [formel]
normstelle: "Kap. 12.5"
---
> [!info] Normstelle
> Kap. 12.5

*In der Herleitung: «Wirksame Spannung am Fuss»*

$$
\sigma'_{v,F} = \sum \gamma_i \, t_i - u
$$

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\sigma'_{v,F} = \sum \gamma_i \, t_i - u = 180\,\mathrm{kPa}
$$

## Gebraucht von

- [[Spitzendruck drainiert]]

## Im Code

- [[opencivil.pfahl.aussen#AeussererWiderstand|AeussererWiderstand._fuss_drainiert]]

## Themen

- [[Äusserer Pfahlwiderstand]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die wirksame Überlagerung in der Tiefe des Fusses: das Gewicht aller
Schichten darüber, weniger dem Wasserdruck dort. Sie behindert den Bruch des
Bodens am Fuss, wie die Auflast neben einem Fundament. Ein Fuss 25 m tief,
darüber 3 m Boden mit 19.7 kN/m³ über dem Wasser, 18 m mit 9.7 und 4 m mit
10.2 kN/m³ darunter: 59.1 + 174.6 + 40.8 = 274.5 kN/m².
